import duckdb

from sqlalchemy import create_engine

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain_huggingface import HuggingFacePipeline, ChatHuggingFace

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

from langchain_community.utilities import SQLDatabase


import requests

# ----------------------------------------------------
# Download data
# ----------------------------------------------------

def download_csv(path="airports.csv"):
    url = "https://www.dadosmundiais.com/downloads/airports.csv"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    open(path, "wb").write(r.content)

download_csv()

# ----------------------------------------------------
# Create DuckDB database from CSV
# ----------------------------------------------------

db_file = "airports.duckdb"

conn = duckdb.connect(db_file)

conn.execute("""
CREATE OR REPLACE TABLE airports AS
SELECT *
FROM read_csv_auto('airports.csv');
""")

conn.close()


engine = create_engine(
    f"duckdb:///{db_file}"
)

db = SQLDatabase(engine)


# ----------------------------------------------------
# Load LFM2.5-Instruct locally
# ----------------------------------------------------

model_id = "LiquidAI/LFM2.5-350M" #"LiquidAI/LFM2.5-1.2B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(
    model_id
)

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",
    torch_dtype="auto",
)


text_generation_pipeline = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=512,
    temperature=0,
    do_sample=False,
    return_full_text=False,   # important
)


llm = HuggingFacePipeline(
    pipeline=text_generation_pipeline
)

chat_model = ChatHuggingFace(
    llm=llm
)


# ----------------------------------------------------
# LCEL SQL generation chain
# ----------------------------------------------------

sql_prompt = PromptTemplate.from_template(
"""
You are a DuckDB SQL expert.

Database schema:
{schema}

Generate a SQL query that answers the question.

Constraints:
- Output SQL only.
- No markdown.
- No explanations.
- Use DuckDB syntax.

Question:
{question}

SQL:
"""
)


sql_chain = (
    {
        "schema": lambda x: db.get_table_info(),
        "question": RunnablePassthrough(),
    }
    | sql_prompt
    | chat_model
)


# ----------------------------------------------------
# Execute SQL
# ----------------------------------------------------

def execute_sql(sql):

    sql = (
        sql
        .replace("```sql", "")
        .replace("```", "")
        .strip()
    )

    with engine.connect() as conn:
        result = conn.exec_driver_sql(sql)

        return [
            dict(row._mapping)
            for row in result
        ]


# ----------------------------------------------------
# Query
# ----------------------------------------------------

question = """
What are the top 10 countries with most airports?
"""


response = sql_chain.invoke(question)

sql = response.content

print("\nGenerated SQL:")
print(sql)


rows = execute_sql(sql)

print("\nResults:")
for row in rows:
    print(row)
