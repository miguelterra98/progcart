import sys
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5 import uic
from pathlib import Path
from qgis.gui import QgsFileWidget


class MyDialog(QDialog):
    def __init__(self):
        super().__init__()
        script_dir = Path(__file__).parent.resolve()
        uic.loadUi(script_dir / "dialog.ui", self)
        self.pushButton.clicked.connect(self.baixar)

    def baixar(self):
        self.accept()  # Close the dialog and return QDialog.Accepted

def main():
    app = QApplication(sys.argv)
    dlg = MyDialog()
    dlg.exec()


if __name__ == "__main__":
    main()

