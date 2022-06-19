from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QCheckBox, QApplication, QDialog, QLabel


class QLabelClickable(QLabel):
    clicked = pyqtSignal()

    def __init__(self):
        pass

    def mousePressEvent(self, event):
        self.clicked.emit()

    class recuperarImagen(QDialog):
        def __init__(self):
            self.setWindowTitle("Registro de Clientes - SIAC")
            self.setWindowIcon(QIcon("siac.ico"))
            self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
            self.setFixedSize(1000, 900)

            self.initUI()



if __name__ == '__main__':
    import sys

    aplicacion = QApplication(sys.argv)

    ventana = recuperarImagen()
    ventana.show()

    sys.exit(aplicacion.exec_())
