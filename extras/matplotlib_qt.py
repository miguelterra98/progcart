import sys
import time
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
#Note a utilizaçao de um backend especı́fico.
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt5 import QtWidgets, uic

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()
        # Carrega a MainWindow que tem um objeto verticalLayout
        uic.loadUi('main_window.ui', self)

        # Cria um canvas da MatPlotLib integrado à PyQt
        self.static_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        #  Adiciona a barra de navegação no layout
        self.verticalLayout.addWidget(NavigationToolbar(self.static_canvas, self))
        # Adiciona o canvas no layout
        self.verticalLayout.addWidget(self.static_canvas)

    def draw_plot(self): # Função que gera os dados e desenha
        self._static_ax = self.static_canvas.figure.subplots()
        t = np.linspace(0, 10, 501)
        m = np.random.rand(128,128)
        self._static_ax.imshow(m)

if __name__ == "__main__":
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)

    window = ApplicationWindow()
    window.show()
    window.draw_plot()
    app.exec()
