import psycopg2.errors

from CursorDelPool import CursorDelPool
from oficina import Oficina
from empresa import Empresa
from notifypy import Notify
from os import environ


"""
El módulo *recuperarImagen* permite mostrar una foto en un QLabel y un nombre de usuario
en un QLineEdit que están almacenados en una Base de Datos (SQLite).
"""

from os import getcwd
from sqlite3 import connect

from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt, pyqtSignal, QByteArray, QIODevice, QBuffer, QRect, QSize
from PyQt5.QtWidgets import (QApplication, QDialog, QPushButton, QFileDialog,
                             QLabel, QLineEdit, QComboBox, QRadioButton, QMainWindow, QMessageBox, QTableWidget,
                             QAbstractItemView, QMenu, QAction, QTableWidgetItem, QActionGroup, QSystemTrayIcon)
import webbrowser


# ===================== CLASE QLabelClickable ======================

def suppress_qt_warnings():
    environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    environ["QT_SCALE_FACTOR"] = "1"


class QLabelClickable(QLabel):
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super(QLabelClickable, self).__init__(parent)

    def mousePressEvent(self, event):
        self.clicked.emit()


class OficinaDAO2:
    _INSERTAR = 'INSERT INTO oficina3(no_id, nombres, apellidos, fecha, dpi, telefono, direccion , fecha_dpi,imagen, ' \
                'passwd) VALUES(%s, %s, %s, %s,%s, %s, %s, %s, %s, %s)'
    _INSERTAR_EMPRESA = 'INSERT INTO empresas(nombre, descripcion, no_id) VALUES (%s, %s, %s)'
    _SELECCIONAR = 'SELECT imagen, nombres, apellidos, fecha, dpi, telefono, direccion, fecha_dpi, passwd FROM oficina3 ' \
                   'WHERE no_id = %s'
    _SELECCIONAR_EMPRESA = 'SELECT nombre, descripcion FROM empresas WHERE no_id = %s ORDER BY no_empresa;'
    _ACTUALIZAR_PERSONA = 'UPDATE oficina3 SET nombres = %s, apellidos = %s, fecha = %s, dpi = %s, telefono = %s, ' \
                          'direccion = %s, fecha_dpi = %s, passwd = %s, imagen = %s WHERE no_id = %s'
    _ELIMINAR_PERSONA = 'DELETE FROM oficina3 WHERE no_id = %s'
    _ELIMINAR_EMPRESA = 'DELETE FROM empresas WHERE no_id = %s'
    _DIAS_RESTANTES = 'SELECT nombres, apellidos, telefono, (fecha_dpi::DATE -now()::DATE) AS Dias_Restantes, ' \
                      'fecha_dpi FROM oficina3 ORDER BY fecha_dpi ;'
    _CONSULTA_GENERAL = 'SELECT nombres, apellidos, dpi, telefono, no_id, passwd FROM oficina3 ORDER BY nombres'
    _NOTIFICACION = 'SELECT nombres, apellidos, (fecha_dpi::DATE -now()::DATE) AS Dias_Restantes FROM oficina3 ORDER BY fecha_dpi;'

    @classmethod
    def insertardatos(cls, oficina):
        with CursorDelPool() as cursor:
            valores1 = (oficina.NIT, oficina.Nombres, oficina.apellidos, oficina.fecha, oficina.dpi, oficina.Telefono,
                        oficina.Direccion, oficina.Fecha_dpi, oficina.imagen, oficina.Password)
            cursor.execute(cls._INSERTAR, valores1)
            return cursor.rowcount

    @classmethod
    def notificacion(cls):
        with CursorDelPool() as cursor:
            cursor.execute(cls._NOTIFICACION)
            notificaciones = cursor.fetchall()
            return notificaciones

    @classmethod
    def insertarempresas(cls, empresa):
        with CursorDelPool() as cursor:
            empresas1 = (empresa.nom_empresa, empresa.descripcion, empresa.NIT)
            cursor.execute(cls._INSERTAR_EMPRESA, empresas1)
            return cursor.rowcount

    @classmethod
    def seleccionarpersonas(cls, NIT):
        with CursorDelPool() as cursor:
            cursor.execute(cls._SELECCIONAR, (NIT,))
            registros = cursor.fetchall()
            return registros

    @classmethod
    def seleccionarempresas(cls, NIT):
        with CursorDelPool() as cursor:
            cursor.execute(cls._SELECCIONAR_EMPRESA, (NIT,))
            registros = cursor.fetchall()
            return registros

    @classmethod
    def actualizarpersonas(cls, oficina):
        with CursorDelPool() as cursor:
            valores1 = (oficina.Nombres, oficina.apellidos, oficina.fecha, oficina.dpi, oficina.Telefono,
                        oficina.Direccion, oficina.Fecha_dpi, oficina.Password, oficina.imagen, oficina.NIT)
            cursor.execute(cls._ACTUALIZAR_PERSONA, valores1)

    @classmethod
    def actualizarempresas(cls, empresa):
        with CursorDelPool() as cursor:
            valores1 = (empresa.nom_empresa, empresa.descripcion, empresa.NIT)
            cursor.execute(cls._INSERTAR_EMPRESA, valores1)

    @classmethod
    def eliminarempresas(cls, NIT):
        with CursorDelPool() as cursor:
            cursor.execute(cls._ELIMINAR_EMPRESA, (NIT,))

    @classmethod
    def eliminarclientes(cls, NIT):
        with CursorDelPool() as cursor:
            cursor.execute(cls._ELIMINAR_PERSONA, (NIT,))

    @classmethod
    def dias_dpi(cls):
        with CursorDelPool() as cursor:
            cursor.execute(cls._DIAS_RESTANTES)
            registros = cursor.fetchall()
            usuarios = []
            contador = 1
            for registro in registros:
                usuario = (str(contador), registro[0], registro[1], registro[2], str(registro[3]), str(registro[4]))
                usuarios.append(usuario)
                contador += 1
            return usuarios

    @classmethod
    def CONSULTA_GENERAL(cls):
        with CursorDelPool() as cursor:
            cursor.execute(cls._CONSULTA_GENERAL)
            registros = cursor.fetchall()
            usuarios = []
            contador = 1
            for registro in registros:
                usuario = (str(contador), registro[0], registro[1], registro[2], str(registro[3]), str(registro[4]), str(registro[5]))
                usuarios.append(usuario)
                contador += 1
            return usuarios


# ==================== CLASE recuperarImagen =======================

class recuperarImagen(QDialog):

    def NingunaEmpresa(self):
        self.lineEditDescripcionEmpresa1.setDisabled(True)
        self.lineEditDescripcionEmpresa2.setDisabled(True)
        self.lineEditDescripcionEmpresa3.setDisabled(True)
        self.lineEditNombreEmpresa1.setDisabled(True)
        self.lineEditNombreEmpresa2.setDisabled(True)
        self.lineEditNombreEmpresa3.setDisabled(True)
        self.boton1.setChecked(False)
        self.boton2.setChecked(False)
        self.boton3.setChecked(False)

    def UnaEmpresa(self):
        self.lineEditDescripcionEmpresa1.setDisabled(False)
        self.lineEditDescripcionEmpresa2.setDisabled(True)
        self.lineEditDescripcionEmpresa3.setDisabled(True)
        self.lineEditNombreEmpresa1.setDisabled(False)
        self.lineEditNombreEmpresa2.setDisabled(True)
        self.lineEditNombreEmpresa3.setDisabled(True)
        self.botonN.setChecked(False)
        self.boton2.setChecked(False)
        self.boton3.setChecked(False)

    def DosEmpresas(self):
        self.lineEditDescripcionEmpresa1.setDisabled(False)
        self.lineEditDescripcionEmpresa2.setDisabled(False)
        self.lineEditDescripcionEmpresa3.setDisabled(True)
        self.lineEditNombreEmpresa1.setDisabled(False)
        self.lineEditNombreEmpresa2.setDisabled(False)
        self.lineEditNombreEmpresa3.setDisabled(True)
        self.botonN.setChecked(False)
        self.boton1.setChecked(False)
        self.boton3.setChecked(False)

    def TresEmpresas(self):
        self.lineEditDescripcionEmpresa1.setDisabled(False)
        self.lineEditDescripcionEmpresa2.setDisabled(False)
        self.lineEditDescripcionEmpresa3.setDisabled(False)
        self.lineEditNombreEmpresa1.setDisabled(False)
        self.lineEditNombreEmpresa2.setDisabled(False)
        self.lineEditNombreEmpresa3.setDisabled(False)
        self.botonN.setChecked(False)
        self.boton1.setChecked(False)
        self.boton2.setChecked(False)

    def __init__(self, parent=None):
        super(recuperarImagen, self).__init__(parent)

        self.setWindowTitle("Registro de Clientes - SIAC")
        self.setWindowIcon(QIcon("siac.ico"))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setFixedSize(1000, 900)

        self.initUI()

    def initUI(self):

        self.setStyleSheet("font-weight: bold;")
        # ==================== WIDGET QLABEL ======================= m

        self.labelImagen = QLabelClickable(self)
        self.labelImagen.setGeometry(30, 25, 168, 180)
        self.labelImagen.setToolTip("Imagen")
        self.labelImagen.setCursor(Qt.PointingHandCursor)

        self.labelImagen.setStyleSheet("QLabel {background-color: white; border: 1px solid "
                                       "#01DFD7; border-radius: 2px;}")

        self.labelImagen.setAlignment(Qt.AlignCenter)

        # ==================== WIDGETS QLABEL ======================

        labelNombreEmpresa = QLabel("REGISTRO DE CLIENTES", self)
        labelNombreEmpresa.setStyleSheet("QLabel {color:black; font-size: 50px; "
                                         "padding:5px; margin: 5px; font-family: serif}")
        labelNombreEmpresa.setAlignment(Qt.AlignCenter)
        labelNombreEmpresa.setGeometry(250, 30, 700, 100)
        # ==================== NIT QLABEL ======================

        labelNIT = QLabel("NUMERO DE IDENTIFICACION TRIBUTARIA (NIT)", self)
        labelNIT.setStyleSheet("QLabel {background-color: gray; color:white; font-size: 14px; "
                               "padding:5px; margin: 5px}")
        labelNIT.setAlignment(Qt.AlignCenter)
        labelNIT.setGeometry(220, 135, 750, 40)

        # ==================== NOMBRE QLABEL ======================
        labelNombre = QLabel("NOMBRE DE USUARIO", self)
        labelNombre.setStyleSheet("QLabel {background-color: gray; color:white; font-size: 14px; "
                                  "padding:5px; margin: 5px}")
        labelNombre.setAlignment(Qt.AlignCenter)
        labelNombre.setGeometry(26, 240, 460, 40)

        # ==================== APELLIDO QLABEL ======================
        labelApellido = QLabel("APELLIDO DE USUARIO", self)
        labelApellido.setStyleSheet("QLabel {background-color: gray; color:white; font-size: 14px; "
                                    "padding:5px; margin: 5px}")
        labelApellido.setAlignment(Qt.AlignCenter)
        labelApellido.setGeometry(500, 240, 466, 40)

        # ==================== DPI QLABEL ======================
        labelDPI = QLabel("DOCUMENTO PERSONAL DE IDENTIFICACIÓN (DPI)", self)
        labelDPI.setStyleSheet("QLabel {background-color: gray; color:white; font-size: 14px; "
                               "padding:5px; margin: 5px}")
        labelDPI.setAlignment(Qt.AlignCenter)
        labelDPI.setGeometry(26, 330, 460, 40)

        # ==================== Fecha QLABEL ======================
        labelfecha = QLabel("FECHA DE NACIMIENTO", self)
        labelfecha.setStyleSheet("QLabel {background-color: gray; color:white; font-size: 14px; "
                                 "padding:5px; margin: 5px}")
        labelfecha.setAlignment(Qt.AlignCenter)
        labelfecha.setGeometry(500, 330, 466, 40)

        # ==================== Telefono QLABEL ======================
        labelTelefono = QLabel("NO. DE TELEFONO", self)
        labelTelefono.setStyleSheet("QLabel {background-color: gray; color:white; font-size: 14px; "
                                    "padding:5px; margin: 5px}")
        labelTelefono.setAlignment(Qt.AlignCenter)
        labelTelefono.setGeometry(26, 420, 460, 40)

        # ==================== Direccion QLABEL ======================
        labelDomicilio = QLabel("DIRECCION DE DOMICILIO", self)
        labelDomicilio.setStyleSheet("QLabel {background-color: gray; color:white; font-size: 14px; "
                                     "padding:5px; margin: 5px}")
        labelDomicilio.setAlignment(Qt.AlignCenter)
        labelDomicilio.setGeometry(500, 420, 466, 40)

        # ==================== Fecha de Vencimiento DPI QLABEL ======================
        labelDomicilio = QLabel("FECHA DE VENCIMIENTO DE DPI", self)
        labelDomicilio.setStyleSheet("QLabel {background-color: gray; color:white; font-size: 14px; "
                                     "padding:5px; margin: 5px}")
        labelDomicilio.setAlignment(Qt.AlignCenter)
        labelDomicilio.setGeometry(26, 510, 466, 40)

        # ==================== Contraseña Portal QLABEL ======================
        labelContraseña = QLabel("CONTRASEÑA PORTAL DE LA SAT", self)
        labelContraseña.setStyleSheet("QLabel {background-color: gray; color:white; font-size: 14px; "
                                      "padding:5px; margin: 5px}")
        labelContraseña.setAlignment(Qt.AlignCenter)
        labelContraseña.setGeometry(500, 510, 466, 40)

        # ==================== NO. DE PROPIEDADES QLABEL ======================
        labelDomicilio = QLabel("¿CUÁNTAS EMPRESAS POSEE EL CLIENTE A REGISTRAR?", self)
        labelDomicilio.setStyleSheet("QLabel {background-color: gray; color:white; font-size: 14px; "
                                     "padding:5px; margin: 5px}")
        labelDomicilio.setAlignment(Qt.AlignCenter)
        labelDomicilio.setGeometry(25, 600, 940, 40)

        # ================== WIDGETS QLINEEDIT =====================

        # ================== QLINEEDIT NIT =====================

        self.lineEditNIT = QLineEdit(self)
        self.lineEditNIT.setAlignment(Qt.AlignCenter)
        self.lineEditNIT.setFont(QFont('Arial', 11))
        self.lineEditNIT.setGeometry(225, 180, 739, 25)

        # ================== QLINEEDIT NOMBRE =====================

        self.lineEditNombre = QLineEdit(self)
        self.lineEditNombre.setAlignment(Qt.AlignCenter)
        self.lineEditNombre.setFont(QFont('Arial', 11))
        self.lineEditNombre.setGeometry(30, 285, 450, 25)

        # ================== QLINEEDIT APELLIDO =====================

        self.lineEditApellido = QLineEdit(self)
        self.lineEditApellido.setAlignment(Qt.AlignCenter)
        self.lineEditApellido.setFont(QFont('Arial', 11))
        self.lineEditApellido.setGeometry(504, 285, 455, 25)

        # ================== QLINEDIT DPI =====================

        self.lineEditDPI = QLineEdit(self)
        self.lineEditDPI.setAlignment(Qt.AlignCenter)
        self.lineEditDPI.setFont(QFont('Arial', 11))
        self.lineEditDPI.setGeometry(30, 375, 450, 25)

        # ================== QComboBox FECHA =====================

        self.qdia = QComboBox(self)
        for i in range(1, 32):
            if i == 15:
                self.qdia.setCurrentText(str(i))
            else:
                pass
            self.qdia.addItem(str(i))
        self.qdia.setGeometry(QRect(504, 375, 100, 25))

        self.qmes = QComboBox(self)
        meses = ('Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre',
                 'Noviembre', 'Diciembre')
        for mes in meses:
            self.qmes.addItem(mes)
        self.qmes.setGeometry(QRect(610, 375, 200, 25))

        self.qano = QComboBox(self)
        for i in range(1930, 2022):
            self.qano.addItem(str(i))
        self.qano.setGeometry(QRect(820, 375, 140, 25))

        # ================== QLINEDIT TELEFONO =====================

        self.lineEditTelefono = QLineEdit(self)
        self.lineEditTelefono.setAlignment(Qt.AlignCenter)
        self.lineEditTelefono.setFont(QFont('Arial', 11))
        self.lineEditTelefono.setGeometry(30, 465, 450, 25)

        # ================== QLINEDIT DIRECCION =====================

        self.lineEditDireccion = QLineEdit(self)
        self.lineEditDireccion.setAlignment(Qt.AlignCenter)
        self.lineEditDireccion.setFont(QFont('Arial', 11))
        self.lineEditDireccion.setGeometry(504, 465, 455, 25)

        # ================== QLINEDIT VENCIMIENTO DPI =====================

        self.qdiadpi = QComboBox(self)
        for i in range(1, 32):
            self.qdiadpi.addItem(str(i))
        self.qdiadpi.setGeometry(QRect(30, 555, 100, 25))

        self.qmesdpi = QComboBox(self)
        meses = ('Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre',
                 'Noviembre', 'Diciembre')
        for mes in meses:
            self.qmesdpi.addItem(mes)
        self.qmesdpi.setGeometry(QRect(136, 555, 200, 25))

        self.qanodpi = QComboBox(self)
        for i in range(2021, 2036):
            self.qanodpi.addItem(str(i))
        self.qanodpi.setGeometry(QRect(346, 555, 140, 25))

        self.lineEditPassword = QLineEdit(self)
        self.lineEditPassword.setAlignment(Qt.AlignCenter)
        self.lineEditPassword.setFont(QFont('Arial', 11))
        self.lineEditPassword.setGeometry(504, 555, 456, 25)

        # ================== QLINEDIT TABLA EMPRESAS =====================

        self.lineEditNombreEmpresa1 = QLineEdit(self)
        self.lineEditNombreEmpresa1.setAlignment(Qt.AlignCenter)
        self.lineEditNombreEmpresa1.setFont(QFont('Arial', 11))
        self.lineEditNombreEmpresa1.setGeometry(50, 680, 350, 25)

        self.lineEditDescripcionEmpresa1 = QLineEdit(self)
        self.lineEditDescripcionEmpresa1.setAlignment(Qt.AlignLeft)
        self.lineEditDescripcionEmpresa1.setFont(QFont('Arial', 10))
        self.lineEditDescripcionEmpresa1.setGeometry(415, 680, 545, 25)

        self.lineEditNombreEmpresa2 = QLineEdit(self)
        self.lineEditNombreEmpresa2.setAlignment(Qt.AlignCenter)
        self.lineEditNombreEmpresa2.setFont(QFont('Arial', 11))
        self.lineEditNombreEmpresa2.setGeometry(50, 720, 350, 25)

        self.lineEditDescripcionEmpresa2 = QLineEdit(self)
        self.lineEditDescripcionEmpresa2.setAlignment(Qt.AlignLeft)
        self.lineEditDescripcionEmpresa2.setFont(QFont('Arial', 10))
        self.lineEditDescripcionEmpresa2.setGeometry(415, 720, 545, 25)

        self.lineEditNombreEmpresa3 = QLineEdit(self)
        self.lineEditNombreEmpresa3.setAlignment(Qt.AlignCenter)
        self.lineEditNombreEmpresa3.setFont(QFont('Arial', 11))
        self.lineEditNombreEmpresa3.setGeometry(50, 760, 350, 25)

        self.lineEditDescripcionEmpresa3 = QLineEdit(self)
        self.lineEditDescripcionEmpresa3.setAlignment(Qt.AlignLeft)
        self.lineEditDescripcionEmpresa3.setFont(QFont('Arial', 10))
        self.lineEditDescripcionEmpresa3.setGeometry(415, 760, 545, 25)

        labelNombreEmpresa = QLabel("Nombre de la Empresa", self)
        labelNombreEmpresa.setStyleSheet("QLabel {color:black; font-size: 14px; "
                                         "padding:5px; margin: 5px}")
        labelNombreEmpresa.setAlignment(Qt.AlignCenter)
        labelNombreEmpresa.setGeometry(0, 640, 466, 40)

        labelDescripcionEmpresa = QLabel("Descripción de la Empresa", self)
        labelDescripcionEmpresa.setStyleSheet("QLabel {color:black; font-size: 14px; "
                                              "padding:5px; margin: 5px}")
        labelDescripcionEmpresa.setAlignment(Qt.AlignCenter)
        labelDescripcionEmpresa.setGeometry(470, 640, 466, 40)

        # labelDescripcionEmpresa = QLabel("¿Cuantas empresas posee?", self)
        # labelDescripcionEmpresa.setStyleSheet("QLabel {color:black; font-size: 14px; "
        #                                       "padding:5px; margin: 5px}")
        # labelDescripcionEmpresa.setAlignment(Qt.AlignCenter)
        # labelDescripcionEmpresa.setGeometry(-100, 620, 466, 40)

        self.botonN = QRadioButton("Ninguno", self)
        self.botonN.setGeometry(20, 650, 80, 30)
        self.botonN.setFont(QFont('Arial', 10))
        self.botonN.toggled.connect(self.NingunaEmpresa)
        self.botonN.setChecked(False)

        self.boton1 = QRadioButton("1", self)
        self.boton1.setGeometry(20, 675, 100, 30)
        self.boton1.setFont(QFont('Arial', 10))
        self.boton1.toggled.connect(self.UnaEmpresa)
        self.boton1.setChecked(False)

        self.boton2 = QRadioButton("2", self)
        self.boton2.setGeometry(20, 715, 120, 30)
        self.boton2.setFont(QFont('Arial', 10))
        self.boton2.toggled.connect(self.DosEmpresas)
        self.boton2.setChecked(False)

        self.boton3 = QRadioButton("3", self)
        self.boton3.setGeometry(20, 755, 140, 30)
        self.boton3.setFont(QFont('Arial', 10))
        self.boton3.toggled.connect(self.TresEmpresas)
        self.boton3.setChecked(False)

        # ================= WIDGETS QPUSHBUTTON ====================

        buttonGuardar = QPushButton("Guardar", self)
        buttonGuardar.setCursor(Qt.PointingHandCursor)
        buttonGuardar.setGeometry(400, 800, 200, 75)
        buttonGuardar.setStyleSheet("background-color: gray; color: white; font-size: 25px;")
        buttonGuardar.clicked.connect(self.Guardar)
        # ===================== EVENTO QLABEL ======================

        # Llamar función al hacer clic sobre el label
        self.labelImagen.clicked.connect(self.seleccionarImagen)
        pixmapImagen = QPixmap("sinfoto.png").scaled(166, 178, Qt.KeepAspectRatio,
                                              Qt.SmoothTransformation)
        self.labelImagen.setPixmap(pixmapImagen)

        # ================== EVENTOS QPUSHBUTTON ===================

    # ======================= FUNCIONES ============================

    def seleccionarImagen(self):
        imagen, extension = QFileDialog.getOpenFileName(self, "Seleccionar imagen", getcwd(),
                                                        "Archivos de imagen (*.png *.jpg)",
                                                        options=QFileDialog.Options())

        if imagen:
            # Adaptar imagen
            pixmapImagen = QPixmap(imagen).scaled(166, 178, Qt.KeepAspectRatio,
                                                  Qt.SmoothTransformation)

            # Mostrar imagen
            self.labelImagen.setPixmap(pixmapImagen)


    def Buscar(self):
        # Obtener nombre de usuario
        nombre = " ".join(self.lineEditNombre.text().split()).title()

        if nombre:
            # Establecer conexión con la base de datos
            conexion = connect("DB_USUARIOS.db")
            cursor = conexion.cursor()

            # Buscar usuario en la base de datos
            cursor.execute("SELECT * FROM Usuarios WHERE NOMBRE = ?", (nombre,))
            resultado = cursor.fetchone()

            # Validar si se encontro algún resultado
            if resultado:
                # Cargar foto a un QPixmap
                foto = QPixmap()
                foto.loadFromData(resultado[1], "PNG", Qt.AutoColor)

                # Insertar foto en el QLabel
                self.labelImagen.setPixmap(foto)

                # Insertar nombre de usuario en el QLineEdit
                self.lineEditNombre.setText(resultado[0])
            else:
                self.labelImagen.clear()
                print("El usuario {} no existe.".format(nombre))

            # Cerrar la conexión con la base de datos
            conexion.close()

            self.lineEditNombre.setFocus()
        else:
            self.lineEditNombre.clear()
            self.lineEditNombre.setFocus()

    def Guardar(self):
        if self.lineEditNIT.text():
            try:
                nuevo_nit = str(self.lineEditNIT.text())
                nuevo_nombres = str(self.lineEditNombre.text())
                nuevo_apellidos = str(self.lineEditApellido.text())
                dia = str(self.qdia.currentText())
                mes_primitivo = str(self.qmes.currentText())
                if mes_primitivo == 'Enero':
                    mes = str('01')
                elif mes_primitivo == 'Febrero':
                    mes = str('02')
                elif mes_primitivo == 'Marzo':
                    mes = str('03')
                elif mes_primitivo == 'Abril':
                    mes = str('04')
                elif mes_primitivo == 'Mayo':
                    mes = str('05')
                elif mes_primitivo == 'Junio':
                    mes = str('06')
                elif mes_primitivo == 'Julio':
                    mes = str('07')
                elif mes_primitivo == 'Agosto':
                    mes = str('08')
                elif mes_primitivo == 'Septiembre':
                    mes = str('09')
                elif mes_primitivo == 'Octubre':
                    mes = str('10')
                elif mes_primitivo == 'Noviembre':
                    mes = str('11')
                elif mes_primitivo == 'Diciembre':
                    mes = str('12')
                else:
                    mes = str('06')
                ano = str(self.qano.currentText())
                fecha_cumple = str(dia + '/' + mes + '/' + ano)
                nuevo_dpi = str(self.lineEditDPI.text())
                nuevo_telefono = str(self.lineEditTelefono.text())
                nueva_direccion = str(self.lineEditDireccion.text())
                dia_dpi = str(self.qdiadpi.currentText())
                mes_primitivo2 = str(self.qmesdpi.currentText())
                if mes_primitivo2 == 'Enero':
                    mes2 = str('01')
                elif mes_primitivo2 == 'Febrero':
                    mes2 = str('02')
                elif mes_primitivo2 == 'Marzo':
                    mes2 = str('03')
                elif mes_primitivo2 == 'Abril':
                    mes2 = str('04')
                elif mes_primitivo2 == 'Mayo':
                    mes2 = str('05')
                elif mes_primitivo2 == 'Junio':
                    mes2 = str('06')
                elif mes_primitivo2 == 'Julio':
                    mes2 = str('07')
                elif mes_primitivo2 == 'Agosto':
                    mes2 = str('08')
                elif mes_primitivo2 == 'Septiembre':
                    mes2 = str('09')
                elif mes_primitivo2 == 'Octubre':
                    mes2 = str('10')
                elif mes_primitivo2 == 'Noviembre':
                    mes2 = str('11')
                elif mes_primitivo2 == 'Diciembre':
                    mes2 = str('12')
                else:
                    mes2 = '06'
                ano_dpi = str(self.qanodpi.currentText())
                fecha_vencimiento = str(dia_dpi + '/' + mes2 + '/' + ano_dpi)
                passwd = str(self.lineEditPassword.text())
                nombre1 = str(self.lineEditNombreEmpresa1.text())
                nombre2 = str(self.lineEditNombreEmpresa2.text())
                nombre3 = str(self.lineEditNombreEmpresa3.text())
                descripcion1 = str(self.lineEditDescripcionEmpresa1.text())
                descripcion2 = str(self.lineEditDescripcionEmpresa2.text())
                descripcion3 = str(self.lineEditDescripcionEmpresa3.text())
                imagen = self.labelImagen.pixmap()
                if imagen:
                    bArray = QByteArray()
                    bufer = QBuffer(bArray)
                    bufer.open(QIODevice.WriteOnly)
                    bufer.close()
                    imagen.save(bufer, "PNG")
                    byte_data = bArray.data()
                else:
                    bArray = ""

                cliente0 = Oficina(NIT=nuevo_nit, Nombres=nuevo_nombres, Apellidos=nuevo_apellidos,
                                   Fecha_Nacimiento=fecha_cumple, DPI=nuevo_dpi, Telefono=nuevo_telefono,
                                   Direccion=nueva_direccion, fecha_dpi=fecha_vencimiento, Imagen=byte_data,
                                   Password=passwd)
                OficinaDAO2.insertardatos(cliente0)

                if self.boton1.isChecked():
                    empresa0 = Empresa(nom_empresa=nombre1, desc_empresa=descripcion1, NIT=nuevo_nit)
                    OficinaDAO2.insertarempresas(empresa0)
                    print(f'Funcion en ejecucion')
                elif self.boton2.isChecked():
                    empresa0 = Empresa(nom_empresa=nombre1, desc_empresa=descripcion1, NIT=nuevo_nit)
                    OficinaDAO2.insertarempresas(empresa0)
                    empresa1 = Empresa(nom_empresa=nombre2, desc_empresa=descripcion2, NIT=nuevo_nit)
                    OficinaDAO2.insertarempresas(empresa1)
                elif self.boton3.isChecked():
                    empresa0 = Empresa(nom_empresa=nombre1, desc_empresa=descripcion1, NIT=nuevo_nit)
                    OficinaDAO2.insertarempresas(empresa0)
                    empresa1 = Empresa(nom_empresa=nombre2, desc_empresa=descripcion2, NIT=nuevo_nit)
                    OficinaDAO2.insertarempresas(empresa1)
                    empresa2 = Empresa(nom_empresa=nombre3, desc_empresa=descripcion3, NIT=nuevo_nit)
                    OficinaDAO2.insertarempresas(empresa2)

                self.labelImagen.clear()
                self.lineEditNombre.clear()
                self.lineEditApellido.clear()
                self.lineEditNIT.clear()
                self.qdia.setCurrentText('1')
                self.qmes.setCurrentText('Enero')
                self.qmes.setCurrentText('1950')
                self.lineEditDPI.clear()
                self.lineEditTelefono.clear()
                self.lineEditDireccion.clear()
                self.qdiadpi.setCurrentText('1')
                self.qmesdpi.setCurrentText('Enero')
                self.qanodpi.setCurrentText('2021')
                self.lineEditNombreEmpresa1.clear()
                self.lineEditNombreEmpresa2.clear()
                self.lineEditNombreEmpresa3.clear()
                self.lineEditDescripcionEmpresa1.clear()
                self.lineEditDescripcionEmpresa2.clear()
                self.lineEditDescripcionEmpresa3.clear()
                self.botonN.setChecked(True)
                self.lineEditPassword.clear()

                QMessageBox.information(self, 'Registro Ingresado',
                                        'Registro ingresado exitosamente.')
            except UnboundLocalError:
                QMessageBox.information(self, 'No se ha ingresado una imagen',
                                        'Por favor, ingrese una imagen para \nasignarla'
                                        ' al cliente a registrar.')
            except Exception as e:
                QMessageBox.information(self, 'El registro ya ha sido ingresado',
                                        f'Error: {e}')
        else:
            QMessageBox.information(self, 'Ingrese el NIT',
                                    'Por favor, ingrese el NIT del cliente \n'
                                    '(requisito obligatorio).')


class ventanaPrincipal(QMainWindow):

    def notificacion(self):
        notificaciones = OficinaDAO2.notificacion()
        for notificacion_individual in notificaciones:
            if int(notificacion_individual[2]) <= 30:
                notificacion = Notify()
                notificacion.title = "Cliente con DPI Vencido"
                notificacion.message = f"El DPI del cliente {notificacion_individual[0]} {notificacion_individual[1]} " \
                                       f"se encuentra vencido. Ingrese a la Consulta de DPI de los " \
                                       f"clientes."
                notificacion.send()

    def __init__(self, parent=None):
        super(ventanaPrincipal, self).__init__(parent)

        self.setWindowTitle("Sistemas Integrales de Administración y Contabilidad")
        self.setWindowIcon(QIcon("siac.ico"))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setFixedSize(1000, 620)

        self.initUI()

    def initUI(self):

        # ======================= WIDGETS ==========================

        self.setStyleSheet("font-size: 16px; font-family: Verdana; font-weight: bold; background-color: darkgray")

        labelSiac = QLabel(self)
        pixmap = QPixmap('logo.png')
        labelSiac.setPixmap(pixmap)
        labelSiac.setGeometry(20, 40, 290, 178)
        self.resize(pixmap.width(), pixmap.height())
        pixmap.scaled(250, 158, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        labelTitulo1 = QLabel("CONTROL DE", self)
        labelTitulo1.setStyleSheet("QLabel {color:#9C0000; font-size: 70px; "
                                   "font-weight: bold;}")
        labelTitulo1.setAlignment(Qt.AlignCenter)
        labelTitulo1.setGeometry(370, 50, 550, 60)

        labelTitulo2 = QLabel("CLIENTES", self)
        labelTitulo2.setStyleSheet("QLabel {color:#9C0000; font-size: 70px; "
                                   "font-weight: bold;}")
        labelTitulo2.setAlignment(Qt.AlignCenter)
        labelTitulo2.setGeometry(370, 120, 550, 60)

        buttonreg = QPushButton("Registro de Clientes", self)
        buttonreg.setStyleSheet("background-color: #4A0000; color: white; ")
        buttonreg.setGeometry(350, 250, 300, 60)
        pixmap = QPixmap("inscribir.png")
        BotonIcono = QIcon(pixmap)
        buttonreg.setIcon(BotonIcono)
        size = QSize(100, 100)
        buttonreg.setIconSize(size)

        buttoncons = QPushButton("Consulta de Clientes", self)
        buttoncons.setStyleSheet("background-color: #550000; color: white;")
        buttoncons.setGeometry(25, 250, 300, 60)
        pixmap = QPixmap("consultar2.png")
        BotonIcono = QIcon(pixmap)
        buttoncons.setIcon(BotonIcono)
        size = QSize(100, 100)
        buttoncons.setIconSize(size)

        buttonactualizar = QPushButton("Actualizacion de Clientes", self)
        buttonactualizar.setStyleSheet("background-color: #5C0000; color: white;")
        buttonactualizar.setGeometry(675, 250, 300, 60)
        pixmap = QPixmap("actualizar.png")
        BotonIcono = QIcon(pixmap)
        buttonactualizar.setIcon(BotonIcono)
        size = QSize(80, 80)
        buttonactualizar.setIconSize(size)

        buttonconsdpi = QPushButton("Consulta DPI Clientes", self)
        buttonconsdpi.setStyleSheet("background-color: #6B0000; color: white;")
        buttonconsdpi.setGeometry(25, 340, 462, 60)
        pixmap = QPixmap("consultar.png")
        BotonIcono = QIcon(pixmap)
        buttonconsdpi.setIcon(BotonIcono)
        size = QSize(120, 120)
        buttonconsdpi.setIconSize(size)

        buttoneliminar = QPushButton("Eliminar Clientes     ", self)
        buttoneliminar.setStyleSheet("background-color: #7C0000; color: white;")
        buttoneliminar.setGeometry(512, 340, 463, 60)
        pixmap = QPixmap("eliminar.png")
        BotonIcono = QIcon(pixmap)
        buttoneliminar.setIcon(BotonIcono)
        size = QSize(120, 120)
        buttoneliminar.setIconSize(size)

        buttonacercade = QPushButton("Redireccion a pagina web de Banrural", self)
        buttonacercade.setStyleSheet("background-color: #8C0000; color: white;")
        buttonacercade.setGeometry(25, 430, 800, 60)
        pixmap = QPixmap("Nuevo_Logo_Banrural.png")
        BotonIcono = QIcon(pixmap)
        buttonacercade.setIcon(BotonIcono)
        size = QSize(120, 120)
        buttonacercade.setIconSize(size)

        buttonsat = QPushButton("  Redireccion a pagina web de la SAT", self)
        buttonsat.setStyleSheet("background-color: #9C0000; color: white;")
        buttonsat.setGeometry(25, 520, 800, 60)
        pixmap = QPixmap("sat-logo.png")
        BotonIcono = QIcon(pixmap)
        buttonsat.setIcon(BotonIcono)
        size = QSize(120, 120)
        buttonsat.setIconSize(size)

        buttonusers = QPushButton("",self)
        buttonusers.setStyleSheet("background-color: #9C0000; color: white; font-size: 25px;")
        buttonusers.setGeometry(850, 430, 123, 151)
        pixmap = QPixmap("16363.png")
        BotonIcono = QIcon(pixmap)
        buttonusers.setIcon(BotonIcono)
        size = QSize(65,65)
        buttonusers.setIconSize(size)

        buttonreg.clicked.connect(self.AbrirRegistro)
        buttoncons.clicked.connect(self.AbrirConsulta)
        buttonconsdpi.clicked.connect(self.AbrirConsultaDPI)
        buttonactualizar.clicked.connect(self.AbrirActualizar)
        buttoneliminar.clicked.connect(self.AbrirEliminar)
        buttonacercade.clicked.connect(self.AbrirBanrural)
        buttonsat.clicked.connect(self.AbrirSAT)
        buttonusers.clicked.connect(self.VerUsuarios)

        self.notificacion()

    def AbrirRegistro(self):
        global primerform
        primerform = recuperarImagen()
        primerform.show()

    def AbrirConsulta(self):
        global segundoform
        segundoform = ventanaConsulta()
        segundoform.show()

    def AbrirConsultaDPI(self):
        global tercerform
        tercerform = ventanaConsultaDPI()
        tercerform.show()

    def AbrirActualizar(self):
        global cuartoform
        cuartoform = ventanaActualizacion()
        cuartoform.show()

    def AbrirEliminar(self):
        global quintoform
        quintoform = ventanaEliminar()
        quintoform.show()

    def VerUsuarios(self):
        global sextoform
        sextoform = ventanaConsultaGeneral()
        sextoform.show()

    def AbrirBanrural(self):
        webbrowser.open('https://www.banrural.com.gt/banruralc/default.aspx')

    def AbrirSAT(self):
        webbrowser.open('https://portal.sat.gob.gt/portal/')


class ventanaConsulta(QDialog):
    def __init__(self, parent=None):
        super(ventanaConsulta, self).__init__(parent)

        # self.setStyleSheet("background-color: asdf;")
        self.setWindowTitle("Consulta de Clientes - SIAC")
        self.setWindowIcon(QIcon("siac.ico"))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setFixedSize(1000, 900)

        self.initUI()

    def initUI(self):
        # ======================= WIDGETS ==========================

        self.setStyleSheet("font-weight: bold;")

        self.labelImagen = QLabelClickable(self)
        self.labelImagen.setGeometry(30, 25, 168, 180)
        self.labelImagen.setToolTip("Imagen")
        self.labelImagen.setCursor(Qt.PointingHandCursor)

        self.labelImagen.setStyleSheet("QLabel {background-color: white; border: 1px solid "
                                       "#01DFD7; border-radius: 2px;}")

        self.labelImagen.setAlignment(Qt.AlignCenter)

        labelNombreEmpresa = QLabel("CONSULTA DE CLIENTES", self)
        labelNombreEmpresa.setStyleSheet("QLabel {color:black; font-size: 50px; "
                                         "padding:5px; margin: 5px; font-family: serif}")
        labelNombreEmpresa.setAlignment(Qt.AlignCenter)
        labelNombreEmpresa.setGeometry(250, 30, 700, 100)
        # ==================== NIT QLABEL ======================

        labelNIT = QLabel("NUMERO DE IDENTIFICACION TRIBUTARIA (NIT)", self)
        labelNIT.setStyleSheet("QLabel {background-color: gray; color:white; font-size: 14px; "
                               "padding:5px; margin: 5px}")
        labelNIT.setAlignment(Qt.AlignCenter)
        labelNIT.setGeometry(220, 135, 750, 40)

        # ==================== NOMBRE QLABEL ======================
        labelNombre = QLabel("NOMBRE DE USUARIO", self)
        labelNombre.setStyleSheet("QLabel {background-color: gray; color:white; font-size: 14px; "
                                  "padding:5px; margin: 5px}")
        labelNombre.setAlignment(Qt.AlignCenter)
        labelNombre.setGeometry(26, 240, 460, 40)

        # ==================== APELLIDO QLABEL ======================
        labelApellido = QLabel("APELLIDO DE USUARIO", self)
        labelApellido.setStyleSheet("QLabel {background-color: gray; color:white; font-size: 14px; "
                                    "padding:5px; margin: 5px}")
        labelApellido.setAlignment(Qt.AlignCenter)
        labelApellido.setGeometry(500, 240, 466, 40)

        # ==================== DPI QLABEL ======================
        labelDPI = QLabel("DOCUMENTO PERSONAL DE IDENTIFICACIÓN (DPI)", self)
        labelDPI.setStyleSheet("QLabel {background-color: gray; color:white; font-size: 14px; "
                               "padding:5px; margin: 5px}")
        labelDPI.setAlignment(Qt.AlignCenter)
        labelDPI.setGeometry(26, 330, 460, 40)

        # ==================== Fecha QLABEL ======================
        labelfecha = QLabel("FECHA DE NACIMIENTO", self)
        labelfecha.setStyleSheet("QLabel {background-color: gray; color:white; font-size: 14px; "
                                 "padding:5px; margin: 5px}")
        labelfecha.setAlignment(Qt.AlignCenter)
        labelfecha.setGeometry(500, 330, 466, 40)

        # ==================== Telefono QLABEL ======================
        labelTelefono = QLabel("NO. DE TELEFONO", self)
        labelTelefono.setStyleSheet("QLabel {background-color: gray; color:white; font-size: 14px; "
                                    "padding:5px; margin: 5px}")
        labelTelefono.setAlignment(Qt.AlignCenter)
        labelTelefono.setGeometry(26, 420, 460, 40)

        # ==================== Direccion QLABEL ======================
        labelDomicilio = QLabel("DIRECCION DE DOMICILIO", self)
        labelDomicilio.setStyleSheet("QLabel {background-color: gray; color:white; font-size: 14px; "
                                     "padding:5px; margin: 5px}")
        labelDomicilio.setAlignment(Qt.AlignCenter)
        labelDomicilio.setGeometry(500, 420, 466, 40)

        # ==================== Fecha de Vencimiento DPI QLABEL ======================
        labelDomicilio = QLabel("FECHA DE VENCIMIENTO DE DPI", self)
        labelDomicilio.setStyleSheet("QLabel {background-color: gray; color:white; font-size: 14px; "
                                     "padding:5px; margin: 5px}")
        labelDomicilio.setAlignment(Qt.AlignCenter)
        labelDomicilio.setGeometry(26, 510, 466, 40)

        # ==================== Contraseña Portal QLABEL ======================
        labelContraseña = QLabel("CONTRASEÑA PORTAL DE LA SAT", self)
        labelContraseña.setStyleSheet("QLabel {background-color: gray; color:white; font-size: 14px; "
                                      "padding:5px; margin: 5px}")
        labelContraseña.setAlignment(Qt.AlignCenter)
        labelContraseña.setGeometry(500, 510, 466, 40)

        # ==================== NO. DE PROPIEDADES QLABEL ======================
        labelDomicilio = QLabel("¿CUÁNTAS EMPRESAS POSEE EL CLIENTE A REGISTRAR?", self)
        labelDomicilio.setStyleSheet("QLabel {background-color: gray; color:white; font-size: 14px; "
                                     "padding:5px; margin: 5px}")
        labelDomicilio.setAlignment(Qt.AlignCenter)
        labelDomicilio.setGeometry(25, 600, 940, 40)

        self.lineEditNIT = QLineEdit(self)
        self.lineEditNIT.setAlignment(Qt.AlignCenter)
        self.lineEditNIT.setFont(QFont('Arial', 11))
        self.lineEditNIT.setGeometry(225, 180, 739, 25)

        # ================== QLINEEDIT NOMBRE =====================

        self.lineEditNombre = QLineEdit(self)
        self.lineEditNombre.setAlignment(Qt.AlignCenter)
        self.lineEditNombre.setFont(QFont('Arial', 11))
        self.lineEditNombre.setGeometry(30, 285, 450, 25)
        self.lineEditNombre.setEnabled(False)

        # ================== QLINEEDIT APELLIDO =====================

        self.lineEditApellido = QLineEdit(self)
        self.lineEditApellido.setAlignment(Qt.AlignCenter)
        self.lineEditApellido.setFont(QFont('Arial', 11))
        self.lineEditApellido.setGeometry(504, 285, 455, 25)
        self.lineEditApellido.setEnabled(False)

        # ================== QLINEDIT DPI =====================

        self.lineEditDPI = QLineEdit(self)
        self.lineEditDPI.setAlignment(Qt.AlignCenter)
        self.lineEditDPI.setFont(QFont('Arial', 11))
        self.lineEditDPI.setGeometry(30, 375, 450, 25)
        self.lineEditDPI.setEnabled(False)

        # ================== QComboBox FECHA =====================

        self.qdia = QComboBox(self)
        for i in range(1, 32):
            if i == 15:
                self.qdia.setCurrentText(str(i))
            else:
                pass
            self.qdia.addItem(str(i))
        self.qdia.setGeometry(QRect(504, 375, 100, 25))
        self.qdia.setEnabled(False)

        self.qmes = QComboBox(self)
        meses = ('Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre',
                 'Noviembre', 'Diciembre')
        for mes in meses:
            self.qmes.addItem(mes)
        self.qmes.setGeometry(QRect(610, 375, 200, 25))
        self.qmes.setEnabled(False)

        self.qano = QComboBox(self)
        for i in range(1930, 2022):
            self.qano.addItem(str(i))
        self.qano.setGeometry(QRect(820, 375, 140, 25))
        self.qano.setEnabled(False)

        # ================== QLINEDIT TELEFONO =====================

        self.lineEditTelefono = QLineEdit(self)
        self.lineEditTelefono.setAlignment(Qt.AlignCenter)
        self.lineEditTelefono.setFont(QFont('Arial', 11))
        self.lineEditTelefono.setGeometry(30, 465, 450, 25)
        self.lineEditTelefono.setEnabled(False)

        # ================== QLINEDIT DIRECCION =====================

        self.lineEditDireccion = QLineEdit(self)
        self.lineEditDireccion.setAlignment(Qt.AlignCenter)
        self.lineEditDireccion.setFont(QFont('Arial', 11))
        self.lineEditDireccion.setGeometry(504, 465, 455, 25)
        self.lineEditDireccion.setEnabled(False)

        # ================== QLINEDIT VENCIMIENTO DPI =====================

        self.qdiadpi = QComboBox(self)
        for i in range(1, 32):
            self.qdiadpi.addItem(str(i))
        self.qdiadpi.setGeometry(QRect(30, 555, 100, 25))
        self.qdiadpi.setEnabled(False)

        self.qmesdpi = QComboBox(self)
        meses = ('Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre',
                 'Noviembre', 'Diciembre')
        for mes in meses:
            self.qmesdpi.addItem(mes)
        self.qmesdpi.setGeometry(QRect(136, 555, 200, 25))
        self.qmesdpi.setEnabled(False)

        self.qanodpi = QComboBox(self)
        for i in range(2021, 2036):
            self.qanodpi.addItem(str(i))
        self.qanodpi.setGeometry(QRect(346, 555, 140, 25))
        self.qanodpi.setEnabled(False)

        self.lineEditPassword = QLineEdit(self)
        self.lineEditPassword.setAlignment(Qt.AlignCenter)
        self.lineEditPassword.setFont(QFont('Arial', 11))
        self.lineEditPassword.setGeometry(504, 555, 456, 25)
        self.lineEditPassword.setEnabled(False)

        # ================== QLINEDIT TABLA EMPRESAS =====================

        labelDomicilio = QLabel("1.", self)
        labelDomicilio.setStyleSheet("QLabel {color:black; font-size: 14px; "
                                     "padding:5px; margin: 5px}")
        labelDomicilio.setAlignment(Qt.AlignCenter)
        labelDomicilio.setGeometry(-200, 675, 466, 40)

        self.lineEditNombreEmpresa1 = QLineEdit(self)
        self.lineEditNombreEmpresa1.setAlignment(Qt.AlignCenter)
        self.lineEditNombreEmpresa1.setFont(QFont('Arial', 11))
        self.lineEditNombreEmpresa1.setGeometry(50, 680, 350, 25)
        self.lineEditNombreEmpresa1.setEnabled(False)

        self.lineEditDescripcionEmpresa1 = QLineEdit(self)
        self.lineEditDescripcionEmpresa1.setAlignment(Qt.AlignLeft)
        self.lineEditDescripcionEmpresa1.setFont(QFont('Arial', 10))
        self.lineEditDescripcionEmpresa1.setGeometry(415, 680, 545, 25)
        self.lineEditDescripcionEmpresa1.setEnabled(False)

        labelDomicilio = QLabel("2.", self)
        labelDomicilio.setStyleSheet("QLabel {color:black; font-size: 14px; "
                                     "padding:5px; margin: 5px}")
        labelDomicilio.setAlignment(Qt.AlignCenter)
        labelDomicilio.setGeometry(-200, 715, 466, 40)

        self.lineEditNombreEmpresa2 = QLineEdit(self)
        self.lineEditNombreEmpresa2.setAlignment(Qt.AlignCenter)
        self.lineEditNombreEmpresa2.setFont(QFont('Arial', 11))
        self.lineEditNombreEmpresa2.setGeometry(50, 720, 350, 25)
        self.lineEditNombreEmpresa2.setEnabled(False)

        self.lineEditDescripcionEmpresa2 = QLineEdit(self)
        self.lineEditDescripcionEmpresa2.setAlignment(Qt.AlignLeft)
        self.lineEditDescripcionEmpresa2.setFont(QFont('Arial', 10))
        self.lineEditDescripcionEmpresa2.setGeometry(415, 720, 545, 25)
        self.lineEditDescripcionEmpresa2.setEnabled(False)

        labelDomicilio = QLabel("3.", self)
        labelDomicilio.setStyleSheet("QLabel {color:black; font-size: 14px; "
                                     "padding:5px; margin: 5px}")
        labelDomicilio.setAlignment(Qt.AlignCenter)
        labelDomicilio.setGeometry(-200, 755, 466, 40)

        self.lineEditNombreEmpresa3 = QLineEdit(self)
        self.lineEditNombreEmpresa3.setAlignment(Qt.AlignCenter)
        self.lineEditNombreEmpresa3.setFont(QFont('Arial', 11))
        self.lineEditNombreEmpresa3.setGeometry(50, 760, 350, 25)
        self.lineEditNombreEmpresa3.setEnabled(False)

        self.lineEditDescripcionEmpresa3 = QLineEdit(self)
        self.lineEditDescripcionEmpresa3.setAlignment(Qt.AlignLeft)
        self.lineEditDescripcionEmpresa3.setFont(QFont('Arial', 10))
        self.lineEditDescripcionEmpresa3.setGeometry(415, 760, 545, 25)
        self.lineEditDescripcionEmpresa3.setEnabled(False)

        labelNombreEmpresa = QLabel("Nombre de la Empresa", self)
        labelNombreEmpresa.setStyleSheet("QLabel {color:black; font-size: 14px; "
                                         "padding:5px; margin: 5px}")
        labelNombreEmpresa.setAlignment(Qt.AlignCenter)
        labelNombreEmpresa.setGeometry(0, 640, 466, 40)

        labelDescripcionEmpresa = QLabel("Descripción de la Empresa", self)
        labelDescripcionEmpresa.setStyleSheet("QLabel {color:black; font-size: 14px; "
                                              "padding:5px; margin: 5px}")
        labelDescripcionEmpresa.setAlignment(Qt.AlignCenter)
        labelDescripcionEmpresa.setGeometry(470, 640, 466, 40)

        botonBuscar = QPushButton("Seleccionar", self)
        botonBuscar.setGeometry(370, 800, 250, 75)
        botonBuscar.setStyleSheet("background-color: gray; color: white; font-size: 25px;")
        botonBuscar.clicked.connect(self.Buscar)

    def Buscar(self):
        if self.lineEditNIT.text():
            try:
                nuevo_NIT = str(self.lineEditNIT.text())
                registros = OficinaDAO2.seleccionarpersonas(nuevo_NIT)
                foto = QPixmap()
                for registro in registros:
                    foto.loadFromData(registro[0], "PNG", Qt.AutoColor)
                    self.labelImagen.setPixmap(foto)
                    nombres = str(registro[1])
                    apellidos = str(registro[2])
                    fecha = str(registro[3])
                    dpi = str(registro[4])
                    telefono = str(registro[5])
                    direccion = str(registro[6])
                    fecha_dpi = str(registro[7])
                    password = str(registro[8])
                self.lineEditNombre.setText(nombres)
                self.lineEditApellido.setText(apellidos)
                self.lineEditDPI.setText(dpi)
                self.lineEditTelefono.setText(telefono)
                self.lineEditDireccion.setText(direccion)
                self.lineEditPassword.setText(password)
                lista_fechaDPI = fecha_dpi.split(sep='-')
                anio, mes_primitivo, dia = lista_fechaDPI
                if mes_primitivo == '01':
                    mes = 'Enero'
                elif mes_primitivo == '02':
                    mes = 'Febrero'
                elif mes_primitivo == '03':
                    mes = 'Marzo'
                elif mes_primitivo == '04':
                    mes = 'Abril'
                elif mes_primitivo == '05':
                    mes = 'Mayo'
                elif mes_primitivo == '06':
                    mes = 'Junio'
                elif mes_primitivo == '07':
                    mes = 'Julio'
                elif mes_primitivo == '08':
                    mes = 'Agosto'
                elif mes_primitivo == '09':
                    mes = 'Septiembre'
                elif mes_primitivo == '10':
                    mes = 'Octubre'
                elif mes_primitivo == '11':
                    mes = 'Noviembre'
                elif mes_primitivo == '12':
                    mes = 'Diciembre'
                else:
                    mes = ''
                self.qanodpi.setCurrentText(anio)
                self.qmesdpi.setCurrentText(mes)
                self.qdiadpi.setCurrentText(dia)
                lista_fecha = fecha.split(sep='-')
                anio, mes_primitivo, dia = lista_fecha
                if mes_primitivo == '01':
                    mes = 'Enero'
                elif mes_primitivo == '02':
                    mes = 'Febrero'
                elif mes_primitivo == '03':
                    mes = 'Marzo'
                elif mes_primitivo == '04':
                    mes = 'Abril'
                elif mes_primitivo == '05':
                    mes = 'Mayo'
                elif mes_primitivo == '06':
                    mes = 'Junio'
                elif mes_primitivo == '07':
                    mes = 'Julio'
                elif mes_primitivo == '08':
                    mes = 'Agosto'
                elif mes_primitivo == '09':
                    mes = 'Septiembre'
                elif mes_primitivo == '10':
                    mes = 'Octubre'
                elif mes_primitivo == '11':
                    mes = 'Noviembre'
                elif mes_primitivo == '12':
                    mes = 'Diciembre'
                else:
                    mes = ''
                self.qano.setCurrentText(anio)
                self.qmes.setCurrentText(mes)
                self.qdia.setCurrentText(dia)
                empresas = OficinaDAO2.seleccionarempresas(nuevo_NIT)
                flat_list = []
                for item in empresas:
                    flat_list += item
                largo_lista = len(flat_list)

                if largo_lista == 2:
                    nom1, desc1 = flat_list
                    self.lineEditNombreEmpresa1.setText(nom1)
                    self.lineEditDescripcionEmpresa1.setText(desc1)
                    self.lineEditNombreEmpresa2.setText("")
                    self.lineEditDescripcionEmpresa2.setText("")
                    self.lineEditNombreEmpresa3.setText("")
                    self.lineEditDescripcionEmpresa3.setText("")
                elif largo_lista == 4:
                    nom1, desc1, nom2, desc2 = flat_list
                    self.lineEditNombreEmpresa1.setText(nom1)
                    self.lineEditDescripcionEmpresa1.setText(desc1)
                    self.lineEditNombreEmpresa2.setText(nom2)
                    self.lineEditDescripcionEmpresa2.setText(desc2)
                    self.lineEditNombreEmpresa3.setText("")
                    self.lineEditDescripcionEmpresa3.setText("")
                elif largo_lista == 6:
                    nom1, desc1, nom2, desc2, nom3, desc3 = flat_list
                    self.lineEditNombreEmpresa1.setText(nom1)
                    self.lineEditDescripcionEmpresa1.setText(desc1)
                    self.lineEditNombreEmpresa2.setText(nom2)
                    self.lineEditDescripcionEmpresa2.setText(desc2)
                    self.lineEditNombreEmpresa3.setText(nom3)
                    self.lineEditDescripcionEmpresa3.setText(desc3)
                else:
                    self.lineEditNombreEmpresa1.setText("")
                    self.lineEditDescripcionEmpresa1.setText("")
                    self.lineEditNombreEmpresa2.setText("")
                    self.lineEditDescripcionEmpresa2.setText("")
                    self.lineEditNombreEmpresa3.setText("")
                    self.lineEditDescripcionEmpresa3.setText("")
            except Exception:
                QMessageBox.information(self, 'No se ha encontrado al cliente',
                                        'No se ha encontrado al cliente dentro del \n'
                                        'registro actual de clientes.')

            # if empresaslen == 1:
            #     lista_empresas_1 = empresas.split(sep=',')
            #     empresa_1, descrip_1 = lista_empresas_1
            #     self.lineEditNombreEmpresa1.setText(empresa_1)
            #     self.lineEditDescripcionEmpresa1.setText(descrip_1)

            # ================= WIDGETS QPUSHBUTTON ====================
        else:
            QMessageBox.information(self, 'Ingrese un valor valido',
                                    'El NIT que ha ingresado no es valido, ingrese \n'
                                    'un valor correcto.')


class ventanaConsultaDPI(QDialog):
    def __init__(self, parent=None):
        super(ventanaConsultaDPI, self).__init__(parent)

        self.setWindowTitle("Consulta Documento Personal de Identificación - SIAC")
        self.setWindowIcon(QIcon("siac.ico"))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setFixedSize(740, 348)

        self.initUI()

    def initUI(self):

        # ================== WIDGET  QTableWidget ==================

        self.tabla = QTableWidget(self)

        # Deshabilitar edición
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Deshabilitar el comportamiento de arrastrar y soltar
        self.tabla.setDragDropOverwriteMode(False)

        # Seleccionar toda la fila
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Seleccionar una fila a la vez
        self.tabla.setSelectionMode(QAbstractItemView.SingleSelection)

        # Especifica dónde deben aparecer los puntos suspensivos "..." cuando se muestran
        # textos que no encajan
        self.tabla.setTextElideMode(Qt.ElideRight)  # Qt.ElideNone

        # Establecer el ajuste de palabras del texto
        self.tabla.setWordWrap(False)

        # Deshabilitar clasificación
        self.tabla.setSortingEnabled(False)

        # Establecer el número de columnas
        self.tabla.setColumnCount(6)

        # Establecer el número de filas
        self.tabla.setRowCount(0)

        # Alineación del texto del encabezado
        self.tabla.horizontalHeader().setDefaultAlignment(Qt.AlignHCenter | Qt.AlignVCenter |
                                                          Qt.AlignCenter)

        # Deshabilitar resaltado del texto del encabezado al seleccionar una fila
        self.tabla.horizontalHeader().setHighlightSections(False)

        # Hacer que la última sección visible del encabezado ocupa todo el espacio disponible
        self.tabla.horizontalHeader().setStretchLastSection(True)

        # Ocultar encabezado vertical
        self.tabla.verticalHeader().setVisible(False)

        # Dibujar el fondo usando colores alternados
        self.tabla.setAlternatingRowColors(True)

        # Establecer altura de las filas
        self.tabla.verticalHeader().setDefaultSectionSize(20)

        # self.tabla.verticalHeader().setHighlightSections(True)

        nombreColumnas = ("Numero de \n Cliente", "Nombre del \n Cliente", "Apellido del \n Cliente",
                          "Telefono de \n Contacto", "Dias de \n Vigencia de DPI", "Fecha de \n vencimiento")

        # Establecer las etiquetas de encabezado horizontal usando etiquetas
        self.tabla.setHorizontalHeaderLabels(nombreColumnas)

        # Menú contextual
        self.tabla.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabla.customContextMenuRequested.connect(self.menuContextual)

        # Establecer ancho de las columnas
        for indice, ancho in enumerate((80, 120, 120, 110, 150), start=0):
            self.tabla.setColumnWidth(indice, ancho)

        self.tabla.resize(700, 240)
        self.tabla.move(20, 56)

        # =================== WIDGETS QPUSHBUTTON ==================

        botonMostrarDatos = QPushButton("Mostrar datos", self)
        botonMostrarDatos.setStyleSheet("background-color: gray; color: white;")
        botonMostrarDatos.setFixedWidth(140)
        botonMostrarDatos.move(20, 20)

        menu = QMenu()
        for indice, columna in enumerate(nombreColumnas, start=0):
            accion = QAction(columna, menu)
            accion.setCheckable(True)
            accion.setChecked(True)
            accion.setData(indice)

            menu.addAction(accion)

        botonMostrarOcultar = QPushButton("Motrar/ocultar columnas", self)
        botonMostrarOcultar.setFixedWidth(180)
        botonMostrarOcultar.setMenu(menu)
        botonMostrarOcultar.setStyleSheet("background-color: gray; color: white;")
        botonMostrarOcultar.move(170, 20)

        botonEliminarFila = QPushButton("Eliminar fila", self)
        botonEliminarFila.setFixedWidth(100)
        botonEliminarFila.setStyleSheet("background-color: gray; color: white;")
        botonEliminarFila.move(530, 20)

        botonLimpiar = QPushButton("Limpiar", self)
        botonLimpiar.setFixedWidth(80)
        botonLimpiar.setStyleSheet("background-color: gray; color: white;")
        botonLimpiar.move(640, 20)

        botonCerrar = QPushButton("Cerrar", self)
        botonCerrar.setStyleSheet("background-color: gray; color: white;")
        botonCerrar.setFixedWidth(80)
        botonCerrar.move(640, 306)

        # ======================== EVENTOS =========================

        botonMostrarDatos.clicked.connect(self.datosTabla)
        botonEliminarFila.clicked.connect(self.eliminarFila)
        botonLimpiar.clicked.connect(self.limpiarTabla)
        botonCerrar.clicked.connect(self.close)

        menu.triggered.connect(self.mostrarOcultar)

        # ======================= FUNCIONES ============================

    def datosTabla(self):
        datos = OficinaDAO2.dias_dpi()

        self.tabla.clearContents()

        row = 0
        for endian in datos:
            self.tabla.setRowCount(row + 1)

            idDato = QTableWidgetItem(endian[0])
            idDato.setTextAlignment(4)

            self.tabla.setItem(row, 0, idDato)
            self.tabla.setItem(row, 1, QTableWidgetItem(endian[1]))
            self.tabla.setItem(row, 2, QTableWidgetItem(endian[2]))
            self.tabla.setItem(row, 3, QTableWidgetItem(endian[3]))
            self.tabla.setItem(row, 4, QTableWidgetItem(endian[4]))
            self.tabla.setItem(row, 5, QTableWidgetItem(endian[5]))

            row += 1

    def mostrarOcultar(self, accion):
        columna = accion.data()

        if accion.isChecked():
            self.tabla.setColumnHidden(columna, False)
        else:
            self.tabla.setColumnHidden(columna, True)

    def eliminarFila(self):
        filaSeleccionada = self.tabla.selectedItems()

        if filaSeleccionada:
            fila = filaSeleccionada[0].row()
            self.tabla.removeRow(fila)

            self.tabla.clearSelection()
        else:
            QMessageBox.critical(self, "Eliminar fila", "Seleccione una fila.   ",
                                 QMessageBox.Ok)

    def limpiarTabla(self):
        self.tabla.clearContents()
        self.tabla.setRowCount(0)

    def menuContextual(self, posicion):
        indices = self.tabla.selectedIndexes()

        if indices:
            menu = QMenu()

            itemsGrupo = QActionGroup(self)
            itemsGrupo.setExclusive(True)

            menu.addAction(QAction("Copiar todo", itemsGrupo))

            columnas = [self.tabla.horizontalHeaderItem(columna).text()
                        for columna in range(self.tabla.columnCount())
                        if not self.tabla.isColumnHidden(columna)]

            copiarIndividual = menu.addMenu("Copiar individual")
            for indice, item in enumerate(columnas, start=0):
                accion = QAction(item, itemsGrupo)
                accion.setData(indice)

                copiarIndividual.addAction(accion)

            itemsGrupo.triggered.connect(self.copiarTableWidgetItem)

            menu.exec_(self.tabla.viewport().mapToGlobal(posicion))

    def copiarTableWidgetItem(self, accion):
        filaSeleccionada = [dato.text() for dato in self.tabla.selectedItems()]

        if accion.text() == "Copiar todo":
            filaSeleccionada = tuple(filaSeleccionada)
        else:
            filaSeleccionada = filaSeleccionada[accion.data()]

        print(filaSeleccionada)

        return

class ventanaConsultaGeneral(QDialog):
    def __init__(self, parent=None):
        super(ventanaConsultaGeneral, self).__init__(parent)

        self.setWindowTitle("Consulta General de Clientes - SIAC")
        self.setWindowIcon(QIcon("siac.ico"))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setFixedSize(740, 440)

        self.initUI()

    def initUI(self):

        # ================== WIDGET  QTableWidget ==================

        self.tabla = QTableWidget(self)

        # Deshabilitar edición
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Deshabilitar el comportamiento de arrastrar y soltar
        self.tabla.setDragDropOverwriteMode(False)

        # Seleccionar toda la fila
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Seleccionar una fila a la vez
        self.tabla.setSelectionMode(QAbstractItemView.SingleSelection)

        # Especifica dónde deben aparecer los puntos suspensivos "..." cuando se muestran
        # textos que no encajan
        self.tabla.setTextElideMode(Qt.ElideRight)  # Qt.ElideNone

        # Establecer el ajuste de palabras del texto
        self.tabla.setWordWrap(False)

        # Deshabilitar clasificación
        self.tabla.setSortingEnabled(False)

        # Establecer el número de columnas
        self.tabla.setColumnCount(7)

        # Establecer el número de filas
        self.tabla.setRowCount(0)

        # Alineación del texto del encabezado
        self.tabla.horizontalHeader().setDefaultAlignment(Qt.AlignHCenter | Qt.AlignVCenter |
                                                          Qt.AlignCenter)

        # Deshabilitar resaltado del texto del encabezado al seleccionar una fila
        self.tabla.horizontalHeader().setHighlightSections(False)

        # Hacer que la última sección visible del encabezado ocupa todo el espacio disponible
        self.tabla.horizontalHeader().setStretchLastSection(True)

        # Ocultar encabezado vertical
        self.tabla.verticalHeader().setVisible(False)

        # Dibujar el fondo usando colores alternados
        self.tabla.setAlternatingRowColors(True)

        # Establecer altura de las filas
        self.tabla.verticalHeader().setDefaultSectionSize(20)

        # self.tabla.verticalHeader().setHighlightSections(True)

        nombreColumnas = ("Numero de \n Cliente", "Nombre del \n Cliente", "Apellido del \n Cliente",
                          "DPI del \n Cliente", "Telefono de \n Contacto", "NIT del \n cliente", "Contraseña \n del cliente")

        # Establecer las etiquetas de encabezado horizontal usando etiquetas
        self.tabla.setHorizontalHeaderLabels(nombreColumnas)

        # Menú contextual
        self.tabla.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabla.customContextMenuRequested.connect(self.menuContextual)

        # Establecer ancho de las columnas
        for indice, ancho in enumerate((90, 120, 120, 100, 80, 80, 80), start=0):
            self.tabla.setColumnWidth(indice, ancho)

        self.tabla.resize(700, 340)
        self.tabla.move(20, 56)

        # =================== WIDGETS QPUSHBUTTON ==================

        botonMostrarDatos = QPushButton("Mostrar datos", self)
        botonMostrarDatos.setStyleSheet("background-color: gray; color: white;")
        botonMostrarDatos.setFixedWidth(140)
        botonMostrarDatos.move(20, 20)

        menu = QMenu()
        for indice, columna in enumerate(nombreColumnas, start=0):
            accion = QAction(columna, menu)
            accion.setCheckable(True)
            accion.setChecked(True)
            accion.setData(indice)

            menu.addAction(accion)

        botonMostrarOcultar = QPushButton("Motrar/ocultar columnas", self)
        botonMostrarOcultar.setFixedWidth(180)
        botonMostrarOcultar.setMenu(menu)
        botonMostrarOcultar.setStyleSheet("background-color: gray; color: white;")
        botonMostrarOcultar.move(170, 20)

        botonEliminarFila = QPushButton("Eliminar fila", self)
        botonEliminarFila.setFixedWidth(100)
        botonEliminarFila.setStyleSheet("background-color: gray; color: white;")
        botonEliminarFila.move(530, 20)

        botonLimpiar = QPushButton("Limpiar", self)
        botonLimpiar.setFixedWidth(80)
        botonLimpiar.setStyleSheet("background-color: gray; color: white;")
        botonLimpiar.move(640, 20)

        botonCerrar = QPushButton("Cerrar", self)
        botonCerrar.setStyleSheet("background-color: gray; color: white;")
        botonCerrar.setFixedWidth(80)
        botonCerrar.move(640, 406)

        # ======================== EVENTOS =========================

        botonMostrarDatos.clicked.connect(self.datosTabla)
        botonEliminarFila.clicked.connect(self.eliminarFila)
        botonLimpiar.clicked.connect(self.limpiarTabla)
        botonCerrar.clicked.connect(self.close)

        menu.triggered.connect(self.mostrarOcultar)

        # ======================= FUNCIONES ============================

    def datosTabla(self):
        datos = OficinaDAO2.CONSULTA_GENERAL()

        self.tabla.clearContents()

        row = 0
        for endian in datos:
            self.tabla.setRowCount(row + 1)

            idDato = QTableWidgetItem(endian[0])
            idDato.setTextAlignment(4)

            self.tabla.setItem(row, 0, idDato)
            self.tabla.setItem(row, 1, QTableWidgetItem(endian[1]))
            self.tabla.setItem(row, 2, QTableWidgetItem(endian[2]))
            self.tabla.setItem(row, 3, QTableWidgetItem(endian[3]))
            self.tabla.setItem(row, 4, QTableWidgetItem(endian[4]))
            self.tabla.setItem(row, 5, QTableWidgetItem(endian[5]))
            self.tabla.setItem(row, 6, QTableWidgetItem(endian[6]))

            row += 1

    def mostrarOcultar(self, accion):
        columna = accion.data()

        if accion.isChecked():
            self.tabla.setColumnHidden(columna, False)
        else:
            self.tabla.setColumnHidden(columna, True)

    def eliminarFila(self):
        filaSeleccionada = self.tabla.selectedItems()

        if filaSeleccionada:
            fila = filaSeleccionada[0].row()
            self.tabla.removeRow(fila)

            self.tabla.clearSelection()
        else:
            QMessageBox.critical(self, "Eliminar fila", "Seleccione una fila.   ",
                                 QMessageBox.Ok)

    def limpiarTabla(self):
        self.tabla.clearContents()
        self.tabla.setRowCount(0)

    def menuContextual(self, posicion):
        indices = self.tabla.selectedIndexes()

        if indices:
            menu = QMenu()

            itemsGrupo = QActionGroup(self)
            itemsGrupo.setExclusive(True)

            menu.addAction(QAction("Copiar todo", itemsGrupo))

            columnas = [self.tabla.horizontalHeaderItem(columna).text()
                        for columna in range(self.tabla.columnCount())
                        if not self.tabla.isColumnHidden(columna)]

            copiarIndividual = menu.addMenu("Copiar individual")
            for indice, item in enumerate(columnas, start=0):
                accion = QAction(item, itemsGrupo)
                accion.setData(indice)

                copiarIndividual.addAction(accion)

            itemsGrupo.triggered.connect(self.copiarTableWidgetItem)

            menu.exec_(self.tabla.viewport().mapToGlobal(posicion))

    def copiarTableWidgetItem(self, accion):
        filaSeleccionada = [dato.text() for dato in self.tabla.selectedItems()]

        if accion.text() == "Copiar todo":
            filaSeleccionada = tuple(filaSeleccionada)
        else:
            filaSeleccionada = filaSeleccionada[accion.data()]

        print(filaSeleccionada)

        return

class ventanaActualizacion(QDialog):
    def __init__(self, parent=None):
        super(ventanaActualizacion, self).__init__(parent)

        self.setWindowTitle("Actualizacion Clientes Registrados - SIAC")
        self.setWindowIcon(QIcon("siac.ico"))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setFixedSize(1000, 900)

        self.initUI()

    def NingunaEmpresa(self):
        self.lineEditDescripcionEmpresa1.setDisabled(True)
        self.lineEditDescripcionEmpresa2.setDisabled(True)
        self.lineEditDescripcionEmpresa3.setDisabled(True)
        self.lineEditNombreEmpresa1.setDisabled(True)
        self.lineEditNombreEmpresa2.setDisabled(True)
        self.lineEditNombreEmpresa3.setDisabled(True)
        self.boton1.setChecked(False)
        self.boton2.setChecked(False)
        self.boton3.setChecked(False)

    def UnaEmpresa(self):
        self.lineEditDescripcionEmpresa1.setDisabled(False)
        self.lineEditDescripcionEmpresa2.setDisabled(True)
        self.lineEditDescripcionEmpresa3.setDisabled(True)
        self.lineEditNombreEmpresa1.setDisabled(False)
        self.lineEditNombreEmpresa2.setDisabled(True)
        self.lineEditNombreEmpresa3.setDisabled(True)
        self.botonN.setChecked(False)
        self.boton2.setChecked(False)
        self.boton3.setChecked(False)

    def DosEmpresas(self):
        self.lineEditDescripcionEmpresa1.setDisabled(False)
        self.lineEditDescripcionEmpresa2.setDisabled(False)
        self.lineEditDescripcionEmpresa3.setDisabled(True)
        self.lineEditNombreEmpresa1.setDisabled(False)
        self.lineEditNombreEmpresa2.setDisabled(False)
        self.lineEditNombreEmpresa3.setDisabled(True)
        self.botonN.setChecked(False)
        self.boton1.setChecked(False)
        self.boton3.setChecked(False)

    def TresEmpresas(self):
        self.lineEditDescripcionEmpresa1.setDisabled(False)
        self.lineEditDescripcionEmpresa2.setDisabled(False)
        self.lineEditDescripcionEmpresa3.setDisabled(False)
        self.lineEditNombreEmpresa1.setDisabled(False)
        self.lineEditNombreEmpresa2.setDisabled(False)
        self.lineEditNombreEmpresa3.setDisabled(False)
        self.botonN.setChecked(False)
        self.boton1.setChecked(False)
        self.boton2.setChecked(False)

    def initUI(self):
        self.labelImagen = QLabelClickable(self)
        self.labelImagen.setGeometry(30, 25, 168, 180)
        self.labelImagen.setToolTip("Imagen")
        self.labelImagen.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("font-weight:bold;")

        self.labelImagen.setStyleSheet("QLabel {background-color: white; border: 1px solid "
                                       "#01DFD7; border-radius: 2px;}")

        self.labelImagen.setAlignment(Qt.AlignCenter)

        labelNombreEmpresa = QLabel("ACTUALIZACION DE CLIENTES", self)
        labelNombreEmpresa.setStyleSheet("QLabel {color:black; font-size: 45px; "
                                         "padding:5px; margin: 5px; font-family: serif}")
        labelNombreEmpresa.setAlignment(Qt.AlignCenter)
        labelNombreEmpresa.setGeometry(240, 30, 710, 100)
        # ==================== NIT QLABEL ======================

        labelNIT = QLabel("NUMERO DE IDENTIFICACION TRIBUTARIA (NIT)", self)
        labelNIT.setStyleSheet("QLabel {background-color: gray; color:white; font-size: 14px; "
                               "padding:5px; margin: 5px}")
        labelNIT.setAlignment(Qt.AlignCenter)
        labelNIT.setGeometry(220, 135, 750, 40)

        # ==================== NOMBRE QLABEL ======================
        labelNombre = QLabel("NOMBRE DE USUARIO", self)
        labelNombre.setStyleSheet("QLabel {background-color: gray; color:white; font-size: 14px; "
                                  "padding:5px; margin: 5px}")
        labelNombre.setAlignment(Qt.AlignCenter)
        labelNombre.setGeometry(26, 240, 460, 40)

        # ==================== APELLIDO QLABEL ======================
        labelApellido = QLabel("APELLIDO DE USUARIO", self)
        labelApellido.setStyleSheet("QLabel {background-color: gray; color:white; font-size: 14px; "
                                    "padding:5px; margin: 5px}")
        labelApellido.setAlignment(Qt.AlignCenter)
        labelApellido.setGeometry(500, 240, 466, 40)

        # ==================== DPI QLABEL ======================
        labelDPI = QLabel("DOCUMENTO PERSONAL DE IDENTIFICACIÓN (DPI)", self)
        labelDPI.setStyleSheet("QLabel {background-color: gray; color:white; font-size: 14px; "
                               "padding:5px; margin: 5px}")
        labelDPI.setAlignment(Qt.AlignCenter)
        labelDPI.setGeometry(26, 330, 460, 40)

        # ==================== Fecha QLABEL ======================
        labelfecha = QLabel("FECHA DE NACIMIENTO", self)
        labelfecha.setStyleSheet("QLabel {background-color: gray; color:white; font-size: 14px; "
                                 "padding:5px; margin: 5px}")
        labelfecha.setAlignment(Qt.AlignCenter)
        labelfecha.setGeometry(500, 330, 466, 40)

        # ==================== Telefono QLABEL ======================
        labelTelefono = QLabel("NO. DE TELEFONO", self)
        labelTelefono.setStyleSheet("QLabel {background-color: gray; color:white; font-size: 14px; "
                                    "padding:5px; margin: 5px}")
        labelTelefono.setAlignment(Qt.AlignCenter)
        labelTelefono.setGeometry(26, 420, 460, 40)

        # ==================== Direccion QLABEL ======================
        labelDomicilio = QLabel("DIRECCION DE DOMICILIO", self)
        labelDomicilio.setStyleSheet("QLabel {background-color: gray; color:white; font-size: 14px; "
                                     "padding:5px; margin: 5px}")
        labelDomicilio.setAlignment(Qt.AlignCenter)
        labelDomicilio.setGeometry(500, 420, 466, 40)

        # ==================== Fecha de Vencimiento DPI QLABEL ======================
        labelDomicilio = QLabel("FECHA DE VENCIMIENTO DE DPI", self)
        labelDomicilio.setStyleSheet("QLabel {background-color: gray; color:white; font-size: 14px; "
                                     "padding:5px; margin: 5px}")
        labelDomicilio.setAlignment(Qt.AlignCenter)
        labelDomicilio.setGeometry(26, 510, 466, 40)

        # ==================== Contraseña Portal QLABEL ======================
        labelContraseña = QLabel("CONTRASEÑA PORTAL DE LA SAT", self)
        labelContraseña.setStyleSheet("QLabel {background-color: gray; color:white; font-size: 14px; "
                                      "padding:5px; margin: 5px}")
        labelContraseña.setAlignment(Qt.AlignCenter)
        labelContraseña.setGeometry(500, 510, 466, 40)

        # ==================== NO. DE PROPIEDADES QLABEL ======================
        labelDomicilio = QLabel("¿CUÁNTAS EMPRESAS POSEE EL CLIENTE A REGISTRAR?", self)
        labelDomicilio.setStyleSheet("QLabel {background-color: gray; color:white; font-size: 14px; "
                                     "padding:5px; margin: 5px}")
        labelDomicilio.setAlignment(Qt.AlignCenter)
        labelDomicilio.setGeometry(25, 600, 940, 40)

        self.lineEditNIT = QLineEdit(self)
        self.lineEditNIT.setAlignment(Qt.AlignCenter)
        self.lineEditNIT.setFont(QFont('Arial', 11))
        self.lineEditNIT.setGeometry(225, 180, 739, 25)

        # ================== QLINEEDIT NOMBRE =====================

        self.lineEditNombre = QLineEdit(self)
        self.lineEditNombre.setAlignment(Qt.AlignCenter)
        self.lineEditNombre.setFont(QFont('Arial', 11))
        self.lineEditNombre.setGeometry(30, 285, 450, 25)
        self.lineEditNombre.setEnabled(False)

        # ================== QLINEEDIT APELLIDO =====================

        self.lineEditApellido = QLineEdit(self)
        self.lineEditApellido.setAlignment(Qt.AlignCenter)
        self.lineEditApellido.setFont(QFont('Arial', 11))
        self.lineEditApellido.setGeometry(504, 285, 455, 25)
        self.lineEditApellido.setEnabled(False)

        # ================== QLINEDIT DPI =====================

        self.lineEditDPI = QLineEdit(self)
        self.lineEditDPI.setAlignment(Qt.AlignCenter)
        self.lineEditDPI.setFont(QFont('Arial', 11))
        self.lineEditDPI.setGeometry(30, 375, 450, 25)
        self.lineEditDPI.setEnabled(False)

        # ================== QComboBox FECHA =====================

        self.qdia = QComboBox(self)
        for i in range(1, 32):
            if i == 15:
                self.qdia.setCurrentText(str(i))
            else:
                pass
            self.qdia.addItem(str(i))
        self.qdia.setGeometry(QRect(504, 375, 100, 25))
        self.qdia.setEnabled(False)

        self.qmes = QComboBox(self)
        meses = ('Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre',
                 'Noviembre', 'Diciembre')
        for mes in meses:
            self.qmes.addItem(mes)
        self.qmes.setGeometry(QRect(610, 375, 200, 25))
        self.qmes.setEnabled(False)

        self.qano = QComboBox(self)
        for i in range(1930, 2022):
            self.qano.addItem(str(i))
        self.qano.setGeometry(QRect(820, 375, 140, 25))
        self.qano.setEnabled(False)

        # ================== QLINEDIT TELEFONO =====================

        self.lineEditTelefono = QLineEdit(self)
        self.lineEditTelefono.setAlignment(Qt.AlignCenter)
        self.lineEditTelefono.setFont(QFont('Arial', 11))
        self.lineEditTelefono.setGeometry(30, 465, 450, 25)
        self.lineEditTelefono.setEnabled(False)

        # ================== QLINEDIT DIRECCION =====================

        self.lineEditDireccion = QLineEdit(self)
        self.lineEditDireccion.setAlignment(Qt.AlignCenter)
        self.lineEditDireccion.setFont(QFont('Arial', 11))
        self.lineEditDireccion.setGeometry(504, 465, 455, 25)
        self.lineEditDireccion.setEnabled(False)

        # ================== QLINEDIT VENCIMIENTO DPI =====================

        self.qdiadpi = QComboBox(self)
        for i in range(1, 32):
            self.qdiadpi.addItem(str(i))
        self.qdiadpi.setGeometry(QRect(30, 555, 100, 25))
        self.qdiadpi.setEnabled(False)

        self.qmesdpi = QComboBox(self)
        meses = ('Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre',
                 'Noviembre', 'Diciembre')
        for mes in meses:
            self.qmesdpi.addItem(mes)
        self.qmesdpi.setGeometry(QRect(136, 555, 200, 25))
        self.qmesdpi.setEnabled(False)

        self.qanodpi = QComboBox(self)
        for i in range(2021, 2036):
            self.qanodpi.addItem(str(i))
        self.qanodpi.setGeometry(QRect(346, 555, 140, 25))
        self.qanodpi.setEnabled(False)

        self.lineEditPassword = QLineEdit(self)
        self.lineEditPassword.setAlignment(Qt.AlignCenter)
        self.lineEditPassword.setFont(QFont('Arial', 11))
        self.lineEditPassword.setGeometry(504, 555, 456, 25)
        self.lineEditPassword.setEnabled(False)

        # ================== QLINEDIT TABLA EMPRESAS =====================

        self.lineEditNombreEmpresa1 = QLineEdit(self)
        self.lineEditNombreEmpresa1.setAlignment(Qt.AlignCenter)
        self.lineEditNombreEmpresa1.setFont(QFont('Arial', 11))
        self.lineEditNombreEmpresa1.setGeometry(50, 680, 350, 25)
        self.lineEditNombreEmpresa1.setEnabled(False)

        self.lineEditDescripcionEmpresa1 = QLineEdit(self)
        self.lineEditDescripcionEmpresa1.setAlignment(Qt.AlignLeft)
        self.lineEditDescripcionEmpresa1.setFont(QFont('Arial', 10))
        self.lineEditDescripcionEmpresa1.setGeometry(415, 680, 545, 25)
        self.lineEditDescripcionEmpresa1.setEnabled(False)

        self.lineEditNombreEmpresa2 = QLineEdit(self)
        self.lineEditNombreEmpresa2.setAlignment(Qt.AlignCenter)
        self.lineEditNombreEmpresa2.setFont(QFont('Arial', 11))
        self.lineEditNombreEmpresa2.setGeometry(50, 720, 350, 25)
        self.lineEditNombreEmpresa2.setEnabled(False)

        self.lineEditDescripcionEmpresa2 = QLineEdit(self)
        self.lineEditDescripcionEmpresa2.setAlignment(Qt.AlignLeft)
        self.lineEditDescripcionEmpresa2.setFont(QFont('Arial', 10))
        self.lineEditDescripcionEmpresa2.setGeometry(415, 720, 545, 25)
        self.lineEditDescripcionEmpresa2.setEnabled(False)

        self.lineEditNombreEmpresa3 = QLineEdit(self)
        self.lineEditNombreEmpresa3.setAlignment(Qt.AlignCenter)
        self.lineEditNombreEmpresa3.setFont(QFont('Arial', 11))
        self.lineEditNombreEmpresa3.setGeometry(50, 760, 350, 25)
        self.lineEditNombreEmpresa3.setEnabled(False)

        self.lineEditDescripcionEmpresa3 = QLineEdit(self)
        self.lineEditDescripcionEmpresa3.setAlignment(Qt.AlignLeft)
        self.lineEditDescripcionEmpresa3.setFont(QFont('Arial', 10))
        self.lineEditDescripcionEmpresa3.setGeometry(415, 760, 545, 25)
        self.lineEditDescripcionEmpresa3.setEnabled(False)

        labelNombreEmpresa = QLabel("Nombre de la Empresa", self)
        labelNombreEmpresa.setStyleSheet("QLabel {color:black; font-size: 14px; "
                                         "padding:5px; margin: 5px}")
        labelNombreEmpresa.setAlignment(Qt.AlignCenter)
        labelNombreEmpresa.setGeometry(0, 640, 466, 40)

        labelDescripcionEmpresa = QLabel("Descripción de la Empresa", self)
        labelDescripcionEmpresa.setStyleSheet("QLabel {color:black; font-size: 14px; "
                                              "padding:5px; margin: 5px}")
        labelDescripcionEmpresa.setAlignment(Qt.AlignCenter)
        labelDescripcionEmpresa.setGeometry(470, 640, 466, 40)

        buttonBuscar = QPushButton("Buscar", self)
        buttonBuscar.setCursor(Qt.PointingHandCursor)
        buttonBuscar.setGeometry(220, 820, 250, 50)
        buttonBuscar.setStyleSheet("background-color: gray; color: white; font-size: 25px;")
        buttonBuscar.clicked.connect(self.Guardar)

        buttonActualizar = QPushButton("Actualizar", self)
        buttonActualizar.setCursor(Qt.PointingHandCursor)
        buttonActualizar.setGeometry(480, 820, 250, 50)
        buttonActualizar.setStyleSheet("background-color: gray; color: white; font-size: 25px;")
        buttonActualizar.clicked.connect(self.Actualizar)

        self.botonN = QRadioButton("Ninguno", self)
        self.botonN.setGeometry(20, 650, 80, 30)
        self.botonN.setFont(QFont('Arial', 10))
        self.botonN.toggled.connect(self.NingunaEmpresa)
        self.botonN.setChecked(False)

        self.boton1 = QRadioButton("1", self)
        self.boton1.setGeometry(20, 675, 100, 30)
        self.boton1.setFont(QFont('Arial', 10))
        self.boton1.toggled.connect(self.UnaEmpresa)
        self.boton1.setChecked(False)

        self.boton2 = QRadioButton("2", self)
        self.boton2.setGeometry(20, 715, 120, 30)
        self.boton2.setFont(QFont('Arial', 10))
        self.boton2.toggled.connect(self.DosEmpresas)
        self.boton2.setChecked(False)

        self.boton3 = QRadioButton("3", self)
        self.boton3.setGeometry(20, 755, 140, 30)
        self.boton3.setFont(QFont('Arial', 10))
        self.boton3.toggled.connect(self.TresEmpresas)
        self.boton3.setChecked(False)

    def Guardar(self):
        if self.lineEditNIT.text():
            try:
                nuevo_NIT = str(self.lineEditNIT.text())
                registros = OficinaDAO2.seleccionarpersonas(nuevo_NIT)
                foto = QPixmap()
                for registro in registros:
                    foto.loadFromData(registro[0], "PNG", Qt.AutoColor)
                    self.labelImagen.setPixmap(foto)
                    nombres = str(registro[1])
                    apellidos = str(registro[2])
                    fecha = str(registro[3])
                    dpi = str(registro[4])
                    telefono = str(registro[5])
                    direccion = str(registro[6])
                    fecha_dpi = str(registro[7])
                    contra = str(registro[8])
                self.lineEditNombre.setText(nombres)
                self.lineEditApellido.setText(apellidos)
                self.lineEditDPI.setText(dpi)
                self.lineEditTelefono.setText(telefono)
                self.lineEditDireccion.setText(direccion)
                self.lineEditPassword.setText(contra)
                lista_fechaDPI = fecha_dpi.split(sep='-')
                anio, mes_primitivo, dia = lista_fechaDPI
                if mes_primitivo == '01':
                    mes = 'Enero'
                elif mes_primitivo == '02':
                    mes = 'Febrero'
                elif mes_primitivo == '03':
                    mes = 'Marzo'
                elif mes_primitivo == '04':
                    mes = 'Abril'
                elif mes_primitivo == '05':
                    mes = 'Mayo'
                elif mes_primitivo == '06':
                    mes = 'Junio'
                elif mes_primitivo == '07':
                    mes = 'Julio'
                elif mes_primitivo == '08':
                    mes = 'Agosto'
                elif mes_primitivo == '09':
                    mes = 'Septiembre'
                elif mes_primitivo == '10':
                    mes = 'Octubre'
                elif mes_primitivo == '11':
                    mes = 'Noviembre'
                elif mes_primitivo == '12':
                    mes = 'Diciembre'
                else:
                    mes = ''
                self.qanodpi.setCurrentText(anio)
                self.qmesdpi.setCurrentText(mes)
                self.qdiadpi.setCurrentText(dia)
                lista_fecha = fecha.split(sep='-')
                anio, mes_primitivo, dia = lista_fecha
                if mes_primitivo == '01':
                    mes = 'Enero'
                elif mes_primitivo == '02':
                    mes = 'Febrero'
                elif mes_primitivo == '03':
                    mes = 'Marzo'
                elif mes_primitivo == '04':
                    mes = 'Abril'
                elif mes_primitivo == '05':
                    mes = 'Mayo'
                elif mes_primitivo == '06':
                    mes = 'Junio'
                elif mes_primitivo == '07':
                    mes = 'Julio'
                elif mes_primitivo == '08':
                    mes = 'Agosto'
                elif mes_primitivo == '09':
                    mes = 'Septiembre'
                elif mes_primitivo == '10':
                    mes = 'Octubre'
                elif mes_primitivo == '11':
                    mes = 'Noviembre'
                elif mes_primitivo == '12':
                    mes = 'Diciembre'
                else:
                    mes = ''
                self.qano.setCurrentText(anio)
                self.qmes.setCurrentText(mes)
                self.qdia.setCurrentText(dia)
                empresas = OficinaDAO2.seleccionarempresas(nuevo_NIT)
                flat_list = []
                for item in empresas:
                    flat_list += item
                largo_lista = len(flat_list)

                if largo_lista == 2:
                    nom1, desc1 = flat_list
                    self.lineEditNombreEmpresa1.setText(nom1)
                    self.lineEditDescripcionEmpresa1.setText(desc1)
                    self.lineEditNombreEmpresa2.setText("")
                    self.lineEditDescripcionEmpresa2.setText("")
                    self.lineEditNombreEmpresa3.setText("")
                    self.lineEditDescripcionEmpresa3.setText("")
                elif largo_lista == 4:
                    nom1, desc1, nom2, desc2 = flat_list
                    self.lineEditNombreEmpresa1.setText(nom1)
                    self.lineEditDescripcionEmpresa1.setText(desc1)
                    self.lineEditNombreEmpresa2.setText(nom2)
                    self.lineEditDescripcionEmpresa2.setText(desc2)
                    self.lineEditNombreEmpresa3.setText("")
                    self.lineEditDescripcionEmpresa3.setText("")
                elif largo_lista == 6:
                    nom1, desc1, nom2, desc2, nom3, desc3 = flat_list
                    self.lineEditNombreEmpresa1.setText(nom1)
                    self.lineEditDescripcionEmpresa1.setText(desc1)
                    self.lineEditNombreEmpresa2.setText(nom2)
                    self.lineEditDescripcionEmpresa2.setText(desc2)
                    self.lineEditNombreEmpresa3.setText(nom3)
                    self.lineEditDescripcionEmpresa3.setText(desc3)
                else:
                    self.lineEditNombreEmpresa1.setText("")
                    self.lineEditDescripcionEmpresa1.setText("")
                    self.lineEditNombreEmpresa2.setText("")
                    self.lineEditDescripcionEmpresa2.setText("")
                    self.lineEditNombreEmpresa3.setText("")
                    self.lineEditDescripcionEmpresa3.setText("")
                self.labelImagen.setEnabled(True)
                self.lineEditNombre.setEnabled(True)
                self.lineEditApellido.setEnabled(True)
                self.lineEditDPI.setEnabled(True)
                self.qdia.setEnabled(True)
                self.qmes.setEnabled(True)
                self.qano.setEnabled(True)
                self.lineEditTelefono.setEnabled(True)
                self.lineEditDireccion.setEnabled(True)
                self.qdiadpi.setEnabled(True)
                self.qmesdpi.setEnabled(True)
                self.qanodpi.setEnabled(True)
                self.botonN.setEnabled(True)
                self.boton1.setEnabled(True)
                self.boton2.setEnabled(True)
                self.boton3.setEnabled(True)
                self.lineEditPassword.setEnabled(True)
            except Exception:
                QMessageBox.information(self, 'Registro no Encontrado',
                                        'No hemos encontrado registro del NIT que ha ingresado. \n'
                                        'Por favor, intente nuevamente.\n ')
        else:
            QMessageBox.information(self, 'NIT no valido',
                                    'No hemos encontrado registro del NIT que ha ingresado. \n'
                                    'Esto sucede gracias a que el NIT que ha ingresado no es\n '
                                    'valido. Por favor, intente nuevamente.')

    def Actualizar(self):
        if self.lineEditNIT.text():
            try:
                nuevo_nit = str(self.lineEditNIT.text())
                nuevo_nombres = str(self.lineEditNombre.text())
                nuevo_apellidos = str(self.lineEditApellido.text())
                nueva_contra = str(self.lineEditPassword.text())
                dia = str(self.qdia.currentText())
                mes_primitivo = str(self.qmes.currentText())
                if mes_primitivo == 'Enero':
                    mes = str('01')
                elif mes_primitivo == 'Febrero':
                    mes = str('02')
                elif mes_primitivo == 'Marzo':
                    mes = str('03')
                elif mes_primitivo == 'Abril':
                    mes = str('04')
                elif mes_primitivo == 'Mayo':
                    mes = str('05')
                elif mes_primitivo == 'Junio':
                    mes = str('06')
                elif mes_primitivo == 'Julio':
                    mes = str('07')
                elif mes_primitivo == 'Agosto':
                    mes = str('08')
                elif mes_primitivo == 'Septiembre':
                    mes = str('09')
                elif mes_primitivo == 'Octubre':
                    mes = str('10')
                elif mes_primitivo == 'Noviembre':
                    mes = str('11')
                elif mes_primitivo == 'Diciembre':
                    mes = str('12')
                else:
                    mes = str('06')
                ano = str(self.qano.currentText())
                fecha_cumple = str(dia + '/' + mes + '/' + ano)
                nuevo_dpi = str(self.lineEditDPI.text())
                nuevo_telefono = str(self.lineEditTelefono.text())
                nueva_direccion = str(self.lineEditDireccion.text())
                dia_dpi = str(self.qdiadpi.currentText())
                mes_primitivo2 = str(self.qmesdpi.currentText())
                if mes_primitivo2 == 'Enero':
                    mes2 = str('01')
                elif mes_primitivo2 == 'Febrero':
                    mes2 = str('02')
                elif mes_primitivo2 == 'Marzo':
                    mes2 = str('03')
                elif mes_primitivo2 == 'Abril':
                    mes2 = str('04')
                elif mes_primitivo2 == 'Mayo':
                    mes2 = str('05')
                elif mes_primitivo2 == 'Junio':
                    mes2 = str('06')
                elif mes_primitivo2 == 'Julio':
                    mes2 = str('07')
                elif mes_primitivo2 == 'Agosto':
                    mes2 = str('08')
                elif mes_primitivo2 == 'Septiembre':
                    mes2 = str('09')
                elif mes_primitivo2 == 'Octubre':
                    mes2 = str('10')
                elif mes_primitivo2 == 'Noviembre':
                    mes2 = str('11')
                elif mes_primitivo2 == 'Diciembre':
                    mes2 = str('12')
                else:
                    mes2 = '06'
                ano_dpi = str(self.qanodpi.currentText())
                fecha_vencimiento = str(dia_dpi + '/' + mes2 + '/' + ano_dpi)
                nombre1 = str(self.lineEditNombreEmpresa1.text())
                nombre2 = str(self.lineEditNombreEmpresa2.text())
                nombre3 = str(self.lineEditNombreEmpresa3.text())
                descripcion1 = str(self.lineEditDescripcionEmpresa1.text())
                descripcion2 = str(self.lineEditDescripcionEmpresa2.text())
                descripcion3 = str(self.lineEditDescripcionEmpresa3.text())
                imagen = self.labelImagen.pixmap()
                if imagen:
                    bArray = QByteArray()
                    bufer = QBuffer(bArray)
                    bufer.open(QIODevice.WriteOnly)
                    bufer.close()
                    imagen.save(bufer, "PNG")
                    byte_data = bArray.data()
                else:
                    bArray = ""
                persona0 = Oficina(Nombres=nuevo_nombres, Apellidos=nuevo_apellidos,
                                   Fecha_Nacimiento=fecha_cumple, DPI=nuevo_dpi, Telefono=nuevo_telefono,
                                   Direccion=nueva_direccion, fecha_dpi=fecha_vencimiento, Password=nueva_contra,
                                   Imagen=byte_data,NIT=nuevo_nit)
                OficinaDAO2.actualizarpersonas(persona0)
                OficinaDAO2.eliminarempresas(nuevo_nit)
                if self.botonN.isChecked():
                    pass
                elif self.boton1.isChecked():
                    empresa0 = Empresa(nom_empresa=nombre1, desc_empresa=descripcion1, NIT=nuevo_nit)
                    OficinaDAO2.actualizarempresas(empresa0)
                elif self.boton2.isChecked():
                    empresa0 = Empresa(nom_empresa=nombre1, desc_empresa=descripcion1, NIT=nuevo_nit)
                    OficinaDAO2.actualizarempresas(empresa0)
                    empresa1 = Empresa(nom_empresa=nombre2, desc_empresa=descripcion2, NIT=nuevo_nit)
                    OficinaDAO2.actualizarempresas(empresa1)
                elif self.boton3.isChecked():
                    empresa0 = Empresa(nom_empresa=nombre1, desc_empresa=descripcion1, NIT=nuevo_nit)
                    OficinaDAO2.actualizarempresas(empresa0)
                    empresa1 = Empresa(nom_empresa=nombre2, desc_empresa=descripcion2, NIT=nuevo_nit)
                    OficinaDAO2.actualizarempresas(empresa1)
                    empresa2 = Empresa(nom_empresa=nombre3, desc_empresa=descripcion3, NIT=nuevo_nit)
                    OficinaDAO2.actualizarempresas(empresa2)
                self.labelImagen.clear()
                self.lineEditNombre.clear()
                self.lineEditApellido.clear()
                self.lineEditNIT.clear()
                self.qdia.setCurrentText('1')
                self.qmes.setCurrentText('Enero')
                self.qmes.setCurrentText('1950')
                self.lineEditDPI.clear()
                self.lineEditTelefono.clear()
                self.lineEditDireccion.clear()
                self.qdiadpi.setCurrentText('1')
                self.qmesdpi.setCurrentText('Enero')
                self.qanodpi.setCurrentText('2021')
                self.lineEditNombreEmpresa1.clear()
                self.lineEditNombreEmpresa2.clear()
                self.lineEditNombreEmpresa3.clear()
                self.lineEditDescripcionEmpresa1.clear()
                self.lineEditDescripcionEmpresa2.clear()
                self.lineEditDescripcionEmpresa3.clear()
                self.botonN.setChecked(True)
                self.lineEditPassword.clear()
                QMessageBox.information(self, 'Registro Actualizado',
                                        'El registro que ha enviado se  \n'
                                        'ha actualizado correctamente.')
            except Exception as e:
                QMessageBox.information(self, 'Registro No Actualizable',
                                        'El registro que ha enviado no  \n'
                                        'se ha actualizado correctamente.')
        else:
            QMessageBox.information(self, 'NIT vacio',
                                    'El cuadro de texto del NIT se encuentra  \n'
                                    'vacio y no puede actualizarse.')


class ventanaEliminar(QDialog):
    def __init__(self, parent=None):
        super(ventanaEliminar, self).__init__(parent)

        self.setWindowTitle("Eliminacion de Clientes Registrados - SIAC")
        self.setWindowIcon(QIcon("siac.ico"))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setFixedSize(960, 440)

        self.initUI()

    def initUI(self):

        self.setStyleSheet("font-weight: bold;")

        # ======================= WIDGETS ==========================
        self.labelImagen = QLabelClickable(self)
        self.labelImagen.setGeometry(30, 25, 168, 180)
        self.labelImagen.setToolTip("Imagen")
        self.labelImagen.setCursor(Qt.PointingHandCursor)

        self.labelImagen.setStyleSheet("QLabel {background-color: white; border: 1px solid "
                                       "#01DFD7; border-radius: 2px;}")

        self.labelImagen.setAlignment(Qt.AlignCenter)

        labelNombreEmpresa = QLabel("ELIMINAR CLIENTES", self)
        labelNombreEmpresa.setStyleSheet("QLabel {color:black; font-size: 40px; "
                                         "padding:5px; margin: 5px; font-family: serif}")
        labelNombreEmpresa.setAlignment(Qt.AlignCenter)
        labelNombreEmpresa.setGeometry(240, 30, 710, 100)

        labelNIT = QLabel("NUMERO DE IDENTIFICACION TRIBUTARIA (NIT)", self)
        labelNIT.setStyleSheet("QLabel {background-color: gray; color:white; font-size: 14px; "
                               "padding:5px; margin: 5px}")
        labelNIT.setAlignment(Qt.AlignCenter)
        labelNIT.setGeometry(220, 135, 720, 40)

        # ==================== NOMBRE QLABEL ======================
        labelNombre = QLabel("NOMBRE DE USUARIO", self)
        labelNombre.setStyleSheet("QLabel {background-color: gray; color:white; font-size: 14px; "
                                  "padding:5px; margin: 5px}")
        labelNombre.setAlignment(Qt.AlignCenter)
        labelNombre.setGeometry(26, 240, 440, 40)

        # ==================== APELLIDO QLABEL ======================
        labelApellido = QLabel("APELLIDO DE USUARIO", self)
        labelApellido.setStyleSheet("QLabel {background-color: gray; color:white; font-size: 14px; "
                                    "padding:5px; margin: 5px}")
        labelApellido.setAlignment(Qt.AlignCenter)
        labelApellido.setGeometry(475, 240, 466, 40)

        self.lineEditNIT = QLineEdit(self)
        self.lineEditNIT.setAlignment(Qt.AlignCenter)
        self.lineEditNIT.setFont(QFont('Arial', 11))
        self.lineEditNIT.setGeometry(225, 180, 710, 25)

        # ================== QLINEEDIT NOMBRE =====================

        self.lineEditNombre = QLineEdit(self)
        self.lineEditNombre.setAlignment(Qt.AlignCenter)
        self.lineEditNombre.setFont(QFont('Arial', 11))
        self.lineEditNombre.setGeometry(30, 285, 430, 25)
        self.lineEditNombre.setEnabled(False)

        # ================== QLINEEDIT APELLIDO =====================

        self.lineEditApellido = QLineEdit(self)
        self.lineEditApellido.setAlignment(Qt.AlignCenter)
        self.lineEditApellido.setFont(QFont('Arial', 11))
        self.lineEditApellido.setGeometry(480, 285, 455, 25)
        self.lineEditApellido.setEnabled(False)

        buttonGuardar = QPushButton("Confirmar", self)
        buttonGuardar.setCursor(Qt.PointingHandCursor)
        buttonGuardar.setGeometry(280, 350, 200, 75)
        buttonGuardar.setStyleSheet("background-color: gray; color: white; font-size: 25px;")
        buttonGuardar.clicked.connect(self.Buscar)

        buttonEliminar = QPushButton("Eliminar", self)
        buttonEliminar.setCursor(Qt.PointingHandCursor)
        buttonEliminar.setGeometry(510, 350, 200, 75)
        buttonEliminar.setStyleSheet("background-color: gray; color: white; font-size: 25px;")
        buttonEliminar.clicked.connect(self.Eliminar)

    def Buscar(self):
        try:
            if self.lineEditNIT.text():
                nuevo_NIT = str(self.lineEditNIT.text())
                registros = OficinaDAO2.seleccionarpersonas(nuevo_NIT)
                foto = QPixmap()
                for registro in registros:
                    foto.loadFromData(registro[0], "PNG", Qt.AutoColor)
                    self.labelImagen.setPixmap(foto)
                    nombres = str(registro[1])
                    apellidos = str(registro[2])
                self.lineEditNombre.setText(nombres)
                self.lineEditApellido.setText(apellidos)
            else:
                QMessageBox.information(self, 'Ingrese un valor valido a buscar',
                                        'El registro que ha enviado no es valido, se encuentra vacio \n'
                                        'y no se puede buscar en el registro de clientes.')
                self.lineEditNombre.setText('')
                self.lineEditNIT.setText('')
                self.lineEditApellido.setText('')
        except Exception:
            QMessageBox.information(self, 'No se ha encontrado al cliente',
                                    'No se ha encontrado al cliente dentro del \n'
                                    'registro actual de clientes.')
            self.lineEditNombre.setText('')
            self.lineEditNIT.setText('')
            self.lineEditApellido.setText('')
            self.labelImagen.clear()

    def Eliminar(self):
        try:
            if self.lineEditNIT.text():
                buscar_nit = self.lineEditNIT.text()
                OficinaDAO2.eliminarclientes(buscar_nit)
                OficinaDAO2.eliminarempresas(buscar_nit)
                self.lineEditNombre.setText('')
                self.lineEditNIT.setText('')
                self.lineEditApellido.setText('')
                self.labelImagen.clear()
                QMessageBox.information(self, 'Registro Eliminado',
                                        'Se ha eliminado correctamente el \n'
                                        'registro actual del cliente.')
            else:
                QMessageBox.information(self, 'Ingrese un valor valido a buscar',
                                        'El registro que ha enviado no es valido, se encuentra vacio \n'
                                        'y no se puede eliminar del registro de clientes.')
                self.lineEditNombre.setText('')
                self.lineEditNIT.setText('')
                self.lineEditApellido.setText('')
                self.labelImagen.clear()
        except Exception:
            QMessageBox.information(self, 'No se ha podido eliminar',
                                    'No se ha encontrado al cliente dentro del \n'
                                    'registro actual de clientes.')


# ================================================================

if __name__ == '__main__':
    suppress_qt_warnings()
    import sys

    aplicacion = QApplication(sys.argv)

    trayIcon = QSystemTrayIcon(QIcon('favicon.ico'),parent=aplicacion)
    trayIcon.setToolTip('SIAC')
    trayIcon.show()

    ventana = ventanaPrincipal()
    ventana.show()

    sys.exit(aplicacion.exec_())
