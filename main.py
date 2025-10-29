import sys
import os
import sqlite3
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit,
    QVBoxLayout, QMessageBox, QInputDialog, QHBoxLayout,
    QStackedLayout, QListWidget, QListWidgetItem, QFileDialog,
    QSpinBox,QTableWidget, QTableWidgetItem, QComboBox,QScrollArea
)
from PySide6.QtGui import QFont, QPixmap,QColor
from PySide6.QtCore import Qt
import base64

DB_FILE = "sistema.db"


class ConexionBD:
    def __init__(self, archivo):
        self.conexion = sqlite3.connect(archivo)
        self.cursor = self.conexion.cursor()
        self.crear_tablas()

    def cerrar(self):
        self.conexion.close()

    def crear_tablas(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Categoria(
            id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL
        )""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Producto(
            id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
            id_categoria INTEGER,
            nombre TEXT NOT NULL,
            precio REAL,
            stock INTEGER,
            limite_stock INTEGER,
            imagen BLOB,
            tipo_imagen TEXT,
            FOREIGN KEY(id_categoria) REFERENCES Categoria(id_categoria)
        )""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Cliente(
            id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            telefono TEXT,
            correo TEXT,
            total_compras REAL,
            descuento REAL
        )""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Empleado(
            id_empleado INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            telefono TEXT,
            correo TEXT,
            salario REAL
        )""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Proveedor(
            id_proveedor INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            empresa TEXT,
            telefono TEXT
        )""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Usuario(
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            usuario TEXT NOT NULL UNIQUE,
            contrasena TEXT NOT NULL,
            tipo TEXT NOT NULL
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Venta(
            id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER,
            fecha TEXT,
            total REAL,
            id_empleado INTEGER,
            FOREIGN KEY(id_cliente) REFERENCES Cliente(id_cliente),
            FOREIGN KEY(id_empleado) REFERENCES Empleado(id_empleado)
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS DetalleVenta(
            id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
            id_venta INTEGER,
            id_producto INTEGER,
            cantidad INTEGER,
            precio_unitario REAL,
            subtotal REAL,
            FOREIGN KEY(id_venta) REFERENCES Venta(id_venta),
            FOREIGN KEY(id_producto) REFERENCES Producto(id_producto)
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Compra(
            id_compra INTEGER PRIMARY KEY AUTOINCREMENT,
            id_proveedor INTEGER,
            fecha TEXT,
            total REAL,
            FOREIGN KEY(id_proveedor) REFERENCES Proveedor(id_proveedor)
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS DetalleCompra(
            id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
            id_compra INTEGER,
            id_producto INTEGER,
            cantidad INTEGER,
            precio_unitario REAL,
            subtotal REAL,
            FOREIGN KEY(id_compra) REFERENCES Compra(id_compra),
            FOREIGN KEY(id_producto) REFERENCES Producto(id_producto)
        )
        """)

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS ListaUtiles(
            id_lista INTEGER PRIMARY KEY AUTOINCREMENT,
            grado TEXT,
            id_cliente INTEGER,
            FOREIGN KEY(id_cliente) REFERENCES Cliente(id_cliente)
        )""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS DetalleListaUtiles(
            id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
            id_lista INTEGER,
            id_producto INTEGER,
            cantidad INTEGER,
            FOREIGN KEY(id_lista) REFERENCES ListaUtiles(id_lista),
            FOREIGN KEY(id_producto) REFERENCES Producto(id_producto)
        )""")

        self.conexion.commit()

    def ejecutar(self, query, params=()):
        self.cursor.execute(query, params)
        self.conexion.commit()

    def consultar(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()


class ManejadorImagenes:
    @staticmethod
    def imagen_a_blob(ruta_imagen):
        try:
            if not os.path.exists(ruta_imagen):
                return None, None

            extension = os.path.splitext(ruta_imagen)[1].lower()

            with open(ruta_imagen, 'rb') as file:
                blob_data = file.read()

            return blob_data, extension
        except Exception as e:
            print(f"Error al convertir imagen: {e}")
            return None, None

    @staticmethod
    def blob_a_imagen(blob_data, tipo_imagen):
        try:
            if blob_data is None:
                return QPixmap()

            pixmap = QPixmap()
            pixmap.loadFromData(blob_data)
            return pixmap
        except Exception as e:
            print(f"Error al cargar imagen desde blob: {e}")
            return QPixmap()

    @staticmethod
    def obtener_imagen_predeterminada():
        pixmap = QPixmap(100, 100)
        pixmap.fill(Qt.GlobalColor.lightGray)
        return pixmap


class Categoria:
    def __init__(self, nombre):
        self.nombre = nombre


class Producto:
    def __init__(self, id_categoria, nombre, precio, stock, limite_stock, imagen):
        self.id_categoria = id_categoria
        self.nombre = nombre
        self.precio = precio
        self.stock = stock
        self.limite_stock = limite_stock
        self.imagen = imagen


class Cliente:
    def __init__(self, nombre, telefono, correo, total_compras=0, descuento=0):
        self.nombre = nombre
        self.telefono = telefono
        self.correo = correo
        self.total_compras = total_compras
        self.descuento = descuento


class Empleado:
    def __init__(self, nombre, telefono, correo, salario):
        self.nombre = nombre
        self.telefono = telefono
        self.correo = correo
        self.salario = salario


class Proveedor:
    def __init__(self, nombre, empresa, telefono):
        self.nombre = nombre
        self.empresa = empresa
        self.telefono = telefono


class ListaUtiles:
    def __init__(self, grado, id_cliente):
        self.grado = grado
        self.id_cliente = id_cliente


class Usuario:
    def __init__(self, nombre, usuario, contrasena, tipo):
        self.nombre = nombre
        self.usuario = usuario
        self.contrasena = contrasena
        self.tipo = tipo


class Compra:
    def __init__(self, id_compra=0, id_padre=0, fecha=None, total=0.0):
        self.id_compra = id_compra
        self.id_padre = id_padre
        self.fecha = fecha if fecha else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.total = total
        self.detalles = []  # Lista de objetos DetalleCompra

    def agregar_detalle(self, detalle):
        self.detalles.append(detalle)

    def calcular_total(self):
        self.total = sum(d.subtotal for d in self.detalles)


class DetalleCompra:
    def __init__(self, id_detalle=0, id_compra=0, id_producto=0, cantidad=0, precio_unitario=0.0):
        self.id_detalle = id_detalle
        self.id_compra = id_compra
        self.id_producto = id_producto
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.subtotal = cantidad * precio_unitario


class Venta:
    def __init__(self, id_venta=0, id_cliente=0, id_empleado=0, fecha=None, total=0.0):
        self.id_venta = id_venta
        self.id_cliente = id_cliente
        self.id_empleado = id_empleado
        self.fecha = fecha if fecha else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.total = total
        self.detalles = []

    def agregar_detalle(self, detalle):
        self.detalles.append(detalle)

    def calcular_total(self):
        self.total = sum(d.subtotal for d in self.detalles)


class DetalleVenta:
    def __init__(self, id_detalle=0, id_venta=0, id_producto=0, cantidad=0, precio_unitario=0.0):
        self.id_detalle = id_detalle
        self.id_venta = id_venta
        self.id_producto = id_producto
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.subtotal = cantidad * precio_unitario


class GestionUsuario:
    def __init__(self, bd):
        self.bd = bd

    def agregar(self, parent=None):
        nombre, ok1 = QInputDialog.getText(parent, "Registrar usuario", "Nombre:")
        if not ok1 or not nombre.strip():
            return

        usuario, ok2 = QInputDialog.getText(parent, "Registrar usuario", "Usuario:")
        if not ok2 or not usuario.strip():
            return

        contrasena, ok3 = QInputDialog.getText(parent, "Registrar usuario", "Contraseña:", QLineEdit.EchoMode.Password)
        if not ok3 or not contrasena.strip():
            return

        self.bd.ejecutar(
            "INSERT INTO Usuario(nombre,usuario,contrasena,tipo) VALUES(?,?,?,?)",
            (nombre.strip(), usuario.strip(), contrasena.strip(), "admin")
        )
        QMessageBox.information(parent, "Éxito", "Usuario registrado con éxito.")

    def listar(self):
        filas = self.bd.consultar("SELECT * FROM Usuario")
        for f in filas:
            print(f"ID:{f[0]} | Nombre:{f[1]} | Usuario:{f[2]}")


class ManejadorImagenes:
    @staticmethod
    def imagen_a_blob(ruta_imagen):

        try:
            if not os.path.exists(ruta_imagen):
                return None, None


            extension = os.path.splitext(ruta_imagen)[1].lower().replace('.', '')

            with open(ruta_imagen, 'rb') as file:
                blob_data = file.read()

            return blob_data, extension
        except Exception as e:
            print(f"Error al convertir imagen: {e}")
            return None, None

    @staticmethod
    def blob_a_imagen(blob_data, tipo_imagen):

        try:
            if blob_data is None:
                return QPixmap()

            pixmap = QPixmap()
            pixmap.loadFromData(blob_data)
            return pixmap
        except Exception as e:
            print(f"Error al cargar imagen desde blob: {e}")
            return QPixmap()

    @staticmethod
    def obtener_imagen_predeterminada():

        pixmap = QPixmap(100, 100)
        pixmap.fill(Qt.GlobalColor.lightGray)
        return pixmap


class VentanaTipoUsuario(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Selecciona tipo de usuario")
        self.showMaximized()  # Ocupa toda la pantalla
        self._aplicar_estilos()
        self._construir_ui()

    def _aplicar_estilos(self):
        self.setStyleSheet("""
            QWidget { 
                background-color: #f2f6fa; 
                font-family: 'Segoe UI'; 
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 13px;
                min-height: 32px;
            }
            QPushButton:hover { 
                background-color: #0056b3; 
            }
        """)

    def _construir_ui(self):
        v = QVBoxLayout()
        v.setContentsMargins(30, 30, 30, 30)
        v.setSpacing(15)

        titulo = QLabel("Bienvenido a Librería ABC")
        titulo.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("color: #2c3e50;")

        btn_padres = QPushButton("Padres de familia")
        btn_padres.clicked.connect(self._abrir_padres)
        btn_padres.setFixedWidth(200)  # Solo ancho fijo

        btn_admin = QPushButton("Administrador / Empleado")
        btn_admin.clicked.connect(self._abrir_admin)
        btn_admin.setFixedWidth(200)  # Solo ancho fijo

        v.addStretch()
        v.addWidget(titulo)
        v.addSpacing(20)
        v.addWidget(btn_padres, alignment=Qt.AlignmentFlag.AlignCenter)
        v.addWidget(btn_admin, alignment=Qt.AlignmentFlag.AlignCenter)
        v.addStretch()
        self.setLayout(v)

    def _abrir_padres(self):
        self.hide()
        self.padres = VentanaLoginPadres()
        self.padres.showMaximized()

    def _abrir_admin(self):
        self.hide()
        self.admin = VentanaLoginAdmin()
        self.admin.showMaximized()

class VentanaLoginPadres(QWidget):
    def __init__(self):
        super().__init__()
        self.bd = ConexionBD(DB_FILE)
        self.setWindowTitle("Login - Padres")
        self.resize(400, 250)
        self._construir_ui()

    def _construir_ui(self):
        v = QVBoxLayout()
        lbl = QLabel("Iniciar sesión - Padres")
        lbl.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.txt_usuario = QLineEdit()
        self.txt_usuario.setPlaceholderText("Usuario")
        self.txt_contra = QLineEdit()
        self.txt_contra.setPlaceholderText("Contraseña")
        self.txt_contra.setEchoMode(QLineEdit.EchoMode.Password)

        btn_ingresar = QPushButton("Ingresar")
        btn_ingresar.clicked.connect(self._login)

        btn_registrar = QPushButton("Registrarse")
        btn_registrar.clicked.connect(self._abrir_registro)

        btn_volver = QPushButton("Volver")
        btn_volver.clicked.connect(self._volver)

        v.addWidget(lbl)
        v.addWidget(self.txt_usuario)
        v.addWidget(self.txt_contra)
        v.addWidget(btn_ingresar)
        v.addWidget(btn_registrar)
        v.addWidget(btn_volver)
        self.setLayout(v)

    def _login(self):
        usuario = self.txt_usuario.text().strip()
        contra = self.txt_contra.text().strip()
        filas = self.bd.consultar(
            "SELECT * FROM Usuario WHERE usuario=? AND contrasena=? AND tipo='padre'",
            (usuario, contra)
        )
        if filas:
            QMessageBox.information(self, "Bienvenido", f"Hola {filas[0][1]}!")
            self.hide()
            self.padres_principal = VentanaPadres(self.bd, filas[0][0])
            self.padres_principal.show()
        else:
            QMessageBox.critical(self, "Error", "Usuario o contraseña incorrectos.")

    def _abrir_registro(self):
        self.hide()
        self.registro = VentanaRegistroPadres()
        self.registro.show()

    def _volver(self):
        self.close()
        self.tipo_usuario = VentanaTipoUsuario()
        self.tipo_usuario.show()


class VentanaRegistroPadres(QWidget):
    def __init__(self):
        super().__init__()
        self.bd = ConexionBD(DB_FILE)
        self.setWindowTitle("Registro - Padres")
        self.resize(400, 300)
        self._construir_ui()

    def _construir_ui(self):
        v = QVBoxLayout()
        lbl = QLabel("Crear cuenta nueva - Padres")
        lbl.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Nombre completo")

        self.txt_usuario = QLineEdit()
        self.txt_usuario.setPlaceholderText("Usuario")

        self.txt_contra = QLineEdit()
        self.txt_contra.setPlaceholderText("Contraseña")
        self.txt_contra.setEchoMode(QLineEdit.EchoMode.Password)

        btn_registrar = QPushButton("Registrar")
        btn_registrar.clicked.connect(self._registrar)

        btn_volver = QPushButton("Volver")
        btn_volver.clicked.connect(self._volver)

        v.addWidget(lbl)
        v.addWidget(self.txt_nombre)
        v.addWidget(self.txt_usuario)
        v.addWidget(self.txt_contra)
        v.addWidget(btn_registrar)
        v.addWidget(btn_volver)
        self.setLayout(v)

    def _registrar(self):
        nombre = self.txt_nombre.text().strip()
        usuario = self.txt_usuario.text().strip()
        contra = self.txt_contra.text().strip()
        if not nombre or not usuario or not contra:
            QMessageBox.warning(self, "Campos vacíos", "Llena todos los campos.")
            return
        existente = self.bd.consultar("SELECT * FROM Usuario WHERE usuario=?", (usuario,))
        if existente:
            QMessageBox.critical(self, "Error", "El usuario ya existe.")
            return
        self.bd.ejecutar(
            "INSERT INTO Usuario(nombre, usuario, contrasena, tipo) VALUES (?, ?, ?, 'padre')",
            (nombre, usuario, contra)
        )
        QMessageBox.information(self, "Éxito", "Cuenta creada correctamente.")
        self._volver()

    def _volver(self):
        self.close()
        self.login = VentanaLoginPadres()
        self.login.show()


class VentanaLoginAdmin(QWidget):
    def __init__(self):
        super().__init__()
        self.bd = ConexionBD(DB_FILE)
        self.setWindowTitle("Login - Admin/Empleado")
        self.resize(400, 250)
        self._construir_ui()

    def _construir_ui(self):
        v = QVBoxLayout()
        lbl = QLabel("Iniciar sesión - Admin/Empleado")
        lbl.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.txt_usuario = QLineEdit()
        self.txt_usuario.setPlaceholderText("Usuario")
        self.txt_contra = QLineEdit()
        self.txt_contra.setPlaceholderText("Contraseña")
        self.txt_contra.setEchoMode(QLineEdit.EchoMode.Password)

        btn_ingresar = QPushButton("Ingresar")
        btn_ingresar.clicked.connect(self._login)

        btn_registrar = QPushButton("Registrarse")
        btn_registrar.clicked.connect(self._abrir_registro)

        btn_volver = QPushButton("Volver")
        btn_volver.clicked.connect(self._volver)

        v.addWidget(lbl)
        v.addWidget(self.txt_usuario)
        v.addWidget(self.txt_contra)
        v.addWidget(btn_ingresar)
        v.addWidget(btn_registrar)
        v.addWidget(btn_volver)
        self.setLayout(v)

    def _login(self):
        usuario = self.txt_usuario.text().strip()
        contra = self.txt_contra.text().strip()
        filas = self.bd.consultar(
            "SELECT * FROM Usuario WHERE usuario=? AND contrasena=? AND tipo='admin'",
            (usuario, contra)
        )
        if filas:
            QMessageBox.information(self, "Bienvenido", f"Hola {filas[0][1]}!")
            self.hide()
            self.admin_principal = VentanaAdmin(self.bd)
            self.admin_principal.show()
        else:
            QMessageBox.critical(self, "Error", "Usuario o contraseña incorrectos.")

    def _abrir_registro(self):
        self.hide()
        self.registro_admin = VentanaRegistroAdmin()
        self.registro_admin.show()

    def _volver(self):
        self.close()
        self.tipo_usuario = VentanaTipoUsuario()
        self.tipo_usuario.show()


class VentanaRegistroAdmin(QWidget):
    def __init__(self):
        super().__init__()
        self.bd = ConexionBD(DB_FILE)
        self.setWindowTitle("Registro - Admin/Empleado")
        self.resize(400, 300)
        self._construir_ui()

    def _construir_ui(self):
        v = QVBoxLayout()
        lbl = QLabel("Crear cuenta nueva - Admin/Empleado")
        lbl.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Nombre completo")

        self.txt_usuario = QLineEdit()
        self.txt_usuario.setPlaceholderText("Usuario")

        self.txt_contra = QLineEdit()
        self.txt_contra.setPlaceholderText("Contraseña")
        self.txt_contra.setEchoMode(QLineEdit.EchoMode.Password)

        btn_registrar = QPushButton("Registrar")
        btn_registrar.clicked.connect(self._registrar)

        btn_volver = QPushButton("Volver")
        btn_volver.clicked.connect(self._volver)

        v.addWidget(lbl)
        v.addWidget(self.txt_nombre)
        v.addWidget(self.txt_usuario)
        v.addWidget(self.txt_contra)
        v.addWidget(btn_registrar)
        v.addWidget(btn_volver)
        self.setLayout(v)

    def _registrar(self):
        nombre = self.txt_nombre.text().strip()
        usuario = self.txt_usuario.text().strip()
        contra = self.txt_contra.text().strip()
        if not nombre or not usuario or not contra:
            QMessageBox.warning(self, "Campos vacíos", "Llena todos los campos.")
            return
        existente = self.bd.consultar("SELECT * FROM Usuario WHERE usuario=?", (usuario,))
        if existente:
            QMessageBox.critical(self, "Error", "El usuario ya existe.")
            return
        self.bd.ejecutar(
            "INSERT INTO Usuario(nombre, usuario, contrasena, tipo) VALUES (?, ?, ?, 'admin')",
            (nombre, usuario, contra)
        )
        QMessageBox.information(self, "Éxito", "Cuenta creada correctamente.")
        self._volver()

    def _volver(self):
        self.close()
        self.login = VentanaLoginAdmin()
        self.login.show()


class VentanaPadres(QWidget):
    def __init__(self, bd, id_usuario):
        super().__init__()
        self.bd = bd
        self.id_usuario = id_usuario
        self.setWindowTitle("Padres de Familia - Catálogo")
        self.resize(900, 3000)
        self.lista_seleccionados = []
        self._construir_ui()

    def _construir_ui(self):
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)

        self.panel_botones = QVBoxLayout()
        self.btn_catalogo = QPushButton("Ver Catálogo de Útiles")
        self.btn_listado = QPushButton("Crear mi Listado de Útiles")
        self.btn_cerrar = QPushButton("Cerrar Sesión")

        self.btn_catalogo.clicked.connect(self.mostrar_catalogo)
        self.btn_listado.clicked.connect(self.mostrar_listado)  # AQUÍ ESTÁ EL PROBLEMA
        self.btn_cerrar.clicked.connect(self.cerrar_sesion)

        for btn in [self.btn_catalogo, self.btn_listado, self.btn_cerrar]:
            self.panel_botones.addWidget(btn)
        self.panel_botones.addStretch()
        self.main_layout.addLayout(self.panel_botones)

        self.panel_contenido = QVBoxLayout()
        self.main_layout.addLayout(self.panel_contenido)

        usuario_info = self.bd.consultar("SELECT nombre FROM Usuario WHERE id_usuario=?", (self.id_usuario,))
        nombre_usuario = usuario_info[0][0] if usuario_info else "Usuario"
        lbl_bienvenida = QLabel(f"Bienvenido, {nombre_usuario}")
        lbl_bienvenida.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        self.panel_contenido.addWidget(lbl_bienvenida)

    def mostrar_catalogo(self):

        self._limpiar_panel()

        titulo = QLabel("Catálogo de Útiles Escolares")
        titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #2980b9; margin: 10px;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.panel_contenido.addWidget(titulo)

        try:
            productos = self.bd.consultar(
                "SELECT id_producto, nombre, stock, precio, imagen, tipo_imagen FROM Producto"
            )

            if not productos:
                lbl_vacio = QLabel("No hay productos disponibles en el catálogo.")
                lbl_vacio.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lbl_vacio.setStyleSheet("color: #7f8c8d; font-size: 14px; margin: 20px;")
                self.panel_contenido.addWidget(lbl_vacio)
                return


            from PySide6.QtWidgets import QScrollArea
            scroll_area = QScrollArea()
            scroll_widget = QWidget()
            scroll_layout = QVBoxLayout(scroll_widget)

            for producto in productos:
                id_producto, nombre, stock, precio, imagen_blob, tipo_imagen = producto

                # Crear widget para cada producto
                widget_producto = QWidget()
                widget_producto.setFixedHeight(120)
                widget_producto.setStyleSheet("""
                    QWidget {
                        border: 1px solid #bdc3c7;
                        border-radius: 8px;
                        margin: 5px;
                        background-color: white;
                    }
                    QWidget:hover {
                        border: 2px solid #3498db;
                        background-color: #f8f9fa;
                    }
                """)

                layout_producto = QHBoxLayout(widget_producto)
                layout_producto.setContentsMargins(10, 10, 10, 10)

                # Imagen del producto
                lbl_imagen = QLabel()
                lbl_imagen.setFixedSize(80, 80)
                lbl_imagen.setStyleSheet("border: 1px solid #ecf0f1; border-radius: 4px;")
                lbl_imagen.setAlignment(Qt.AlignmentFlag.AlignCenter)

                if imagen_blob:
                    pixmap = ManejadorImagenes.blob_a_imagen(imagen_blob, tipo_imagen)
                    if not pixmap.isNull():
                        pixmap = pixmap.scaled(75, 75, Qt.AspectRatioMode.KeepAspectRatio,
                                               Qt.TransformationMode.SmoothTransformation)
                        lbl_imagen.setPixmap(pixmap)
                    else:
                        lbl_imagen.setPixmap(ManejadorImagenes.obtener_imagen_predeterminada())
                else:

                    pixmap_default = ManejadorImagenes.obtener_imagen_predeterminada()
                    pixmap_default = pixmap_default.scaled(75, 75, Qt.AspectRatioMode.KeepAspectRatio)
                    lbl_imagen.setPixmap(pixmap_default)


                info_widget = QWidget()
                info_layout = QVBoxLayout(info_widget)
                info_layout.setSpacing(5)

                lbl_nombre = QLabel(nombre)
                lbl_nombre.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")

                lbl_precio = QLabel(f"Precio: Q{precio:.2f}")
                lbl_precio.setStyleSheet("font-size: 13px; color: #27ae60; font-weight: bold;")

                lbl_stock = QLabel(f"Stock disponible: {stock}")
                color_stock = "#e74c3c" if stock == 0 else "#f39c12" if stock < 5 else "#27ae60"
                lbl_stock.setStyleSheet(f"font-size: 12px; color: {color_stock};")

                info_layout.addWidget(lbl_nombre)
                info_layout.addWidget(lbl_precio)
                info_layout.addWidget(lbl_stock)
                info_layout.addStretch()


                btn_comprar = QPushButton("Comprar")
                btn_comprar.setFixedSize(80, 30)
                btn_comprar.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                    QPushButton:disabled {
                        background-color: #bdc3c7;
                        color: #7f8c8d;
                    }
                """)
                btn_comprar.clicked.connect(lambda checked, prod=producto: self._comprar_producto(prod))

                if stock == 0:
                    btn_comprar.setEnabled(False)
                    btn_comprar.setText("Sin Stock")

                layout_producto.addWidget(lbl_imagen)
                layout_producto.addWidget(info_widget, 1)
                layout_producto.addWidget(btn_comprar)

                scroll_layout.addWidget(widget_producto)

            scroll_area.setWidget(scroll_widget)
            scroll_area.setWidgetResizable(True)
            scroll_area.setStyleSheet("QScrollArea { border: none; }")
            self.panel_contenido.addWidget(scroll_area)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el catálogo: {str(e)}")

    def mostrar_listado(self):

        self._limpiar_panel()

        titulo = QLabel("Mi Listado de Útiles")
        titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #2980b9; margin: 10px;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.panel_contenido.addWidget(titulo)

        # Lista de útiles seleccionados
        self.lista_mis_utiles = QListWidget()
        self.lista_mis_utiles.setStyleSheet("""
            QListWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)


        for item in self.lista_seleccionados:
            self.lista_mis_utiles.addItem(item)

        self.panel_contenido.addWidget(self.lista_mis_utiles)


        layout_botones = QHBoxLayout()

        self.btn_agregar = QPushButton("➕ Agregar útil")
        self.btn_agregar.clicked.connect(self.agregar_util)
        self.btn_agregar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """)

        self.btn_eliminar = QPushButton(" Eliminar útil")
        self.btn_eliminar.clicked.connect(self.eliminar_util)
        self.btn_eliminar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)

        self.btn_limpiar = QPushButton("Limpiar lista")
        self.btn_limpiar.clicked.connect(self.limpiar_lista)
        self.btn_limpiar.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)

        layout_botones.addWidget(self.btn_agregar)
        layout_botones.addWidget(self.btn_eliminar)
        layout_botones.addWidget(self.btn_limpiar)

        self.panel_contenido.addLayout(layout_botones)

    def agregar_util(self):

        productos = ["Cuaderno", "Lápiz", "Borrador", "Colores", "Mochila", "Regla",
                     "Tijeras", "Pegamento", "Compás", "Transportador", "Calculadora"]

        item, ok = QInputDialog.getItem(
            self,
            "Agregar útil",
            "Selecciona un útil:",
            productos,
            0,
            False
        )

        if ok and item:
            if item not in self.lista_seleccionados:
                self.lista_seleccionados.append(item)
                self.lista_mis_utiles.addItem(item)
                QMessageBox.information(self, "Éxito", f"Se agregó '{item}' a tu listado.")
            else:
                QMessageBox.information(self, "Información", "El útil ya está en tu listado.")

    def eliminar_util(self):

        current_item = self.lista_mis_utiles.currentItem()
        if current_item:
            item_text = current_item.text()
            self.lista_seleccionados.remove(item_text)
            self.lista_mis_utiles.takeItem(self.lista_mis_utiles.currentRow())
            QMessageBox.information(self, "Éxito", f"Se eliminó '{item_text}' de tu listado.")
        else:
            QMessageBox.warning(self, "Advertencia", "Selecciona un útil para eliminar.")

    def limpiar_lista(self):

        if self.lista_seleccionados:
            respuesta = QMessageBox.question(
                self,
                "Confirmar limpieza",
                "¿Estás seguro de que quieres limpiar toda tu lista de útiles?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if respuesta == QMessageBox.StandardButton.Yes:
                self.lista_seleccionados.clear()
                self.lista_mis_utiles.clear()
                QMessageBox.information(self, "Éxito", "Lista limpiada correctamente.")
        else:
            QMessageBox.information(self, "Información", "La lista ya está vacía.")

    def _comprar_producto(self, producto):
        self.ventana_detalle = VentanaDetalleProducto(producto, self.bd, self.id_usuario)
        self.ventana_detalle.show()

    def cerrar_sesion(self):
        self.close()


    def _limpiar_panel(self):

        for i in reversed(range(self.panel_contenido.count())):
            item = self.panel_contenido.itemAt(i)
            if item.widget():
                item.widget().setParent(None)
            elif item.layout():
                # Limpiar layouts anidados
                for j in reversed(range(item.layout().count())):
                    nested_item = item.layout().itemAt(j)
                    if nested_item.widget():
                        nested_item.widget().setParent(None)

class VentanaAdmin(QWidget):
    def __init__(self, bd, mostrar_login=None):
        super().__init__()
        self.bd = bd
        self.mostrar_login = mostrar_login
        self.setWindowTitle("Administrador - Librería ABC")
        self.resize(1000, 600)
        self._construir_ui()

    def _construir_ui(self):
        main_layout = QVBoxLayout(self)
        titulo = QLabel("Panel de administración")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("font-size: 26px; font-weight: bold;")
        main_layout.addWidget(titulo)

        h_layout = QHBoxLayout()
        main_layout.addLayout(h_layout)

        v_botones = QVBoxLayout()
        h_layout.addLayout(v_botones, 1)

        self.stacked_layout = QStackedLayout()
        h_layout.addLayout(self.stacked_layout, 3)

        self.pantallas = {
            "categoria": PantallaAgregarCategoria(self.bd),
            "producto": PantallaAgregarProducto(self.bd),
            "cliente": PantallaAgregarCliente(self.bd),
            "empleado": PantallaAgregarEmpleado(self.bd),
            "proveedor": PantallaAgregarProveedor(self.bd),
            "ventas": PantallaNuevaVenta(self.bd),
            "Compra": PantallaNuevaCompra(self.bd),
            "listas": PantallaCrearLista(self.bd),
            "inventario": PantallaMostrarInventario(self.bd)  # NUEVA PANTALLA
        }
        for w in self.pantallas.values():
            self.stacked_layout.addWidget(w)

        botones = [
            ("Agregar categoría", lambda: self._cambiar_pantalla("categoria")),
            ("Agregar producto", lambda: self._cambiar_pantalla("producto")),
            ("Agregar productos ejemplo", self._agregar_productos_ejemplo),
            ("Ver Inventario", lambda: self._cambiar_pantalla("inventario")),  # NUEVO BOTÓN
            ("Agregar cliente", lambda: self._cambiar_pantalla("cliente")),
            ("Agregar empleado", lambda: self._cambiar_pantalla("empleado")),
            ("Agregar proveedor", lambda: self._cambiar_pantalla("proveedor")),
            ("Vender productos", lambda: self._cambiar_pantalla("ventas")),
            ("Cerrar sesión", self._abrir_login)
        ]

        for texto, func in botones:
            btn = QPushButton(texto)
            btn.setFixedHeight(40)
            btn.clicked.connect(func)
            v_botones.addWidget(btn)
        v_botones.addStretch()

        lbl_inicio = QLabel("Selecciona una opción del menú lateral")
        lbl_inicio.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stacked_layout.addWidget(lbl_inicio)
        self.stacked_layout.setCurrentWidget(lbl_inicio)

    def _agregar_productos_ejemplo(self):

        try:

            categorias = self.bd.consultar("SELECT id_categoria FROM Categoria WHERE nombre='Útiles Escolares'")

            if not categorias:

                self.bd.ejecutar("INSERT INTO Categoria (nombre) VALUES (?)", ("Útiles Escolares",))
                id_categoria = self.bd.cursor.lastrowid
            else:
                id_categoria = categorias[0][0]


            productos_ejemplo = [
                (id_categoria, "Cuaderno cuadriculado 100 hojas", 25.50, 50, 10),
                (id_categoria, "Lápices HB paquete x12", 15.00, 100, 20),
                (id_categoria, "Borradores blancos paquete x4", 8.00, 200, 30),
                (id_categoria, "Regla plástica 30cm", 12.00, 75, 15),
                (id_categoria, "Tajador doble con depósito", 10.50, 150, 25),
                (id_categoria, "Colores x24 piezas", 45.00, 30, 5),
                (id_categoria, "Tijeras escolares punta roma", 18.00, 60, 12),
                (id_categoria, "Pegamento en barra 40g", 9.50, 120, 20),
                (id_categoria, "Mochila escolar antigolpes", 350.00, 15, 3),
                (id_categoria, "Estuche para lápices", 65.00, 40, 8),
                (id_categoria, "Calculadora científica", 120.00, 25, 5),
                (id_categoria, "Diccionario español", 85.00, 20, 4),
                (id_categoria, "Compás de precisión", 35.00, 45, 10),
                (id_categoria, "Transportador 180°", 7.50, 80, 15),
                (id_categoria, "Block de hojas blancas", 30.00, 35, 8)
            ]


            productos_agregados = 0

            for id_cat, nombre, precio, stock, limite_stock in productos_ejemplo:

                existente = self.bd.consultar("SELECT id_producto FROM Producto WHERE nombre=?", (nombre,))

                if not existente:
                    self.bd.ejecutar(
                        "INSERT INTO Producto (id_categoria, nombre, precio, stock, limite_stock, imagen, tipo_imagen) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (id_cat, nombre, precio, stock, limite_stock, None, None)
                    )
                    productos_agregados += 1

            mensaje = f"Se agregaron {productos_agregados} productos de ejemplo exitosamente."
            if productos_agregados < len(productos_ejemplo):
                mensaje += f"\n{len(productos_ejemplo) - productos_agregados} productos ya existían."

            QMessageBox.information(self, "Productos de ejemplo", mensaje)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron agregar los productos de ejemplo:\n{str(e)}")

    def _cambiar_pantalla(self, key):
        widget = self.pantallas.get(key)
        if widget:
            self.stacked_layout.setCurrentWidget(widget)

    def _abrir_login(self):
        self.hide()
        self.mostrar_login = VentanaTipoUsuario()
        self.mostrar_login.show()


class PantallaAgregarCategoria(QWidget):
    def __init__(self, bd):
        super().__init__()
        self.bd = bd
        v = QVBoxLayout()
        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Nombre de la categoría")
        btn_agregar = QPushButton("Agregar")
        btn_agregar.clicked.connect(self._agregar_categoria)
        v.addWidget(self.txt_nombre)
        v.addWidget(btn_agregar)
        self.setLayout(v)

    def _agregar_categoria(self):
        nombre = self.txt_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Error", "Ingresa un nombre de categoría")
            return
        self.bd.ejecutar("INSERT INTO Categoria(nombre) VALUES(?)", (nombre,))
        QMessageBox.information(self, "Éxito", "Categoría agregada correctamente")
        self.txt_nombre.clear()


class PantallaAgregarProducto(QWidget):
    def __init__(self, bd):
        super().__init__()
        self.bd = bd
        self.ruta_imagen = None
        self.datos_imagen = None
        self.tipo_imagen = None
        self._construir_ui()

    def _construir_ui(self):
        v = QVBoxLayout()

        # Campos existentes
        self.txt_id_categoria = QLineEdit()
        self.txt_id_categoria.setPlaceholderText("ID categoría")
        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Nombre producto")
        self.txt_precio = QLineEdit()
        self.txt_precio.setPlaceholderText("Precio")
        self.txt_stock = QLineEdit()
        self.txt_stock.setPlaceholderText("Stock")
        self.txt_limite = QLineEdit()
        self.txt_limite.setPlaceholderText("Límite stock (opcional)")


        lbl_imagen = QLabel("Imagen del producto:")
        self.btn_seleccionar_imagen = QPushButton("Seleccionar Imagen")
        self.btn_seleccionar_imagen.clicked.connect(self._seleccionar_imagen)


        layout_boton_imagen = QHBoxLayout()
        layout_boton_imagen.addWidget(self.btn_seleccionar_imagen)
        layout_boton_imagen.addStretch()


        self.lbl_vista_previa = QLabel()
        self.lbl_vista_previa.setFixedSize(150, 150)
        self.lbl_vista_previa.setStyleSheet("""
            border: 2px dashed #ccc;
            background-color: #f9f9f9;
        """)
        self.lbl_vista_previa.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_vista_previa.setText("Vista previa\n(150x150 px)")
        self.lbl_vista_previa.setWordWrap(True)


        self.lbl_info_imagen = QLabel("No se ha seleccionado imagen")
        self.lbl_info_imagen.setStyleSheet("color: #666; font-size: 12px;")

        btn_agregar = QPushButton("Agregar producto")
        btn_agregar.clicked.connect(self._agregar_producto)


        widgets = [
            self.txt_id_categoria,
            self.txt_nombre,
            self.txt_precio,
            self.txt_stock,
            self.txt_limite,
            lbl_imagen,
            layout_boton_imagen,
            self.lbl_vista_previa,
            self.lbl_info_imagen,
            btn_agregar
        ]

        for w in widgets:
            if isinstance(w, QHBoxLayout):
                v.addLayout(w)
            else:
                v.addWidget(w)

        self.setLayout(v)

    def _seleccionar_imagen(self):

        ruta, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar imagen del producto",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.gif);;Todos los archivos (*)"
        )

        if ruta:
            self.ruta_imagen = ruta
            self.datos_imagen, self.tipo_imagen = ManejadorImagenes.imagen_a_blob(ruta)

            if self.datos_imagen:

                pixmap = ManejadorImagenes.blob_a_imagen(self.datos_imagen, self.tipo_imagen)
                if not pixmap.isNull():

                    pixmap = pixmap.scaled(140, 140, Qt.AspectRatioMode.KeepAspectRatio,
                                           Qt.TransformationMode.SmoothTransformation)
                    self.lbl_vista_previa.setPixmap(pixmap)

                    # Mostrar información del archivo
                    nombre_archivo = os.path.basename(ruta)
                    tamano_kb = len(self.datos_imagen) / 1024
                    self.lbl_info_imagen.setText(
                        f"Imagen: {nombre_archivo}\n"
                        f"Tipo: {self.tipo_imagen.upper()}\n"
                        f"Tamaño: {tamano_kb:.1f} KB"
                    )
                    self.lbl_info_imagen.setStyleSheet("color: green; font-size: 12px;")
                else:
                    self._mostrar_error_imagen("Error al cargar la imagen")
            else:
                self._mostrar_error_imagen("No se pudo cargar la imagen")

    def _mostrar_error_imagen(self, mensaje):

        self.lbl_vista_previa.setText("Error\ncargando\nimagen")
        self.lbl_info_imagen.setText(mensaje)
        self.lbl_info_imagen.setStyleSheet("color: red; font-size: 12px;")
        self.datos_imagen = None
        self.tipo_imagen = None

    def _agregar_producto(self):
        try:
            id_categoria = int(self.txt_id_categoria.text().strip())
            nombre = self.txt_nombre.text().strip()
            precio = float(self.txt_precio.text().strip())
            stock = int(self.txt_stock.text().strip())
            limite_stock = self.txt_limite.text().strip()
            limite_stock = int(limite_stock) if limite_stock else None

            if not nombre:
                raise ValueError("El nombre no puede estar vacío")

        except ValueError as e:
            QMessageBox.warning(self, "Error", f"Datos inválidos: {e}")
            return

        try:

            self.bd.ejecutar(
                "INSERT INTO Producto(id_categoria, nombre, precio, stock, limite_stock, imagen, tipo_imagen) VALUES(?,?,?,?,?,?,?)",
                (id_categoria, nombre, precio, stock, limite_stock, self.datos_imagen, self.tipo_imagen)
            )

            QMessageBox.information(self, "Éxito", "Producto agregado correctamente")
            self._limpiar_formulario()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Error al guardar en la base de datos: {e}")

    def _limpiar_formulario(self):

        self.txt_id_categoria.clear()
        self.txt_nombre.clear()
        self.txt_precio.clear()
        self.txt_stock.clear()
        self.txt_limite.clear()
        self.ruta_imagen = None
        self.datos_imagen = None
        self.tipo_imagen = None
        self.lbl_vista_previa.clear()
        self.lbl_vista_previa.setText("Vista previa\n(150x150 px)")
        self.lbl_info_imagen.setText("No se ha seleccionado imagen")
        self.lbl_info_imagen.setStyleSheet("color: #666; font-size: 12px;")


class PantallaAgregarCliente(QWidget):
    def __init__(self, bd):
        super().__init__()
        self.bd = bd
        v = QVBoxLayout()
        self.txt_nombre = QLineEdit();
        self.txt_nombre.setPlaceholderText("Nombre")
        self.txt_telefono = QLineEdit();
        self.txt_telefono.setPlaceholderText("Teléfono")
        self.txt_correo = QLineEdit();
        self.txt_correo.setPlaceholderText("Correo")
        btn_agregar = QPushButton("Agregar cliente");
        btn_agregar.clicked.connect(self._agregar_cliente)
        for w in [self.txt_nombre, self.txt_telefono, self.txt_correo, btn_agregar]:
            v.addWidget(w)
        self.setLayout(v)

    def _agregar_cliente(self):
        nombre = self.txt_nombre.text().strip()
        telefono = self.txt_telefono.text().strip()
        correo = self.txt_correo.text().strip()
        if not nombre or not telefono or not correo:
            QMessageBox.warning(self, "Error", "Llena todos los campos")
            return
        self.bd.ejecutar(
            "INSERT INTO Cliente(nombre,telefono,correo,total_compras,descuento) VALUES(?,?,?,?,?)",
            (nombre, telefono, correo, 0, 0)
        )
        QMessageBox.information(self, "Éxito", "Cliente agregado correctamente")
        self.txt_nombre.clear();
        self.txt_telefono.clear();
        self.txt_correo.clear()


class PantallaAgregarEmpleado(QWidget):
    def __init__(self, bd):
        super().__init__()
        self.bd = bd
        v = QVBoxLayout()
        self.txt_nombre = QLineEdit();
        self.txt_nombre.setPlaceholderText("Nombre")
        self.txt_telefono = QLineEdit();
        self.txt_telefono.setPlaceholderText("Teléfono")
        self.txt_correo = QLineEdit();
        self.txt_correo.setPlaceholderText("Correo")
        self.txt_salario = QLineEdit();
        self.txt_salario.setPlaceholderText("Salario")
        btn_agregar = QPushButton("Agregar empleado");
        btn_agregar.clicked.connect(self._agregar_empleado)
        for w in [self.txt_nombre, self.txt_telefono, self.txt_correo, self.txt_salario, btn_agregar]:
            v.addWidget(w)
        self.setLayout(v)

    def _agregar_empleado(self):
        try:
            nombre = self.txt_nombre.text().strip()
            telefono = self.txt_telefono.text().strip()
            correo = self.txt_correo.text().strip()
            salario = float(self.txt_salario.text().strip())
            if not nombre: raise ValueError("Nombre vacío")
        except ValueError as e:
            QMessageBox.warning(self, "Error", f"Datos inválidos: {e}")
            return
        self.bd.ejecutar(
            "INSERT INTO Empleado(nombre,telefono,correo,salario) VALUES(?,?,?,?)",
            (nombre, telefono, correo, salario)
        )
        QMessageBox.information(self, "Éxito", "Empleado agregado correctamente")
        self.txt_nombre.clear();
        self.txt_telefono.clear();
        self.txt_correo.clear();
        self.txt_salario.clear()


class PantallaAgregarProveedor(QWidget):
    def __init__(self, bd):
        super().__init__()
        self.bd = bd
        v = QVBoxLayout()
        self.txt_nombre = QLineEdit();
        self.txt_nombre.setPlaceholderText("Nombre")
        self.txt_empresa = QLineEdit();
        self.txt_empresa.setPlaceholderText("Empresa")
        self.txt_telefono = QLineEdit();
        self.txt_telefono.setPlaceholderText("Teléfono")
        btn_agregar = QPushButton("Agregar proveedor");
        btn_agregar.clicked.connect(self._agregar_proveedor)
        for w in [self.txt_nombre, self.txt_empresa, self.txt_telefono, btn_agregar]:
            v.addWidget(w)
        self.setLayout(v)

    def _agregar_proveedor(self):
        nombre = self.txt_nombre.text().strip()
        empresa = self.txt_empresa.text().strip()
        telefono = self.txt_telefono.text().strip()
        if not nombre or not empresa or not telefono:
            QMessageBox.warning(self, "Error", "Llena todos los campos")
            return
        self.bd.ejecutar(
            "INSERT INTO Proveedor(nombre,empresa,telefono) VALUES(?,?,?)",
            (nombre, empresa, telefono)
        )
        QMessageBox.information(self, "Éxito", "Proveedor agregado correctamente")
        self.txt_nombre.clear();
        self.txt_empresa.clear();
        self.txt_telefono.clear()


class VentanaCrearLista(QWidget):
    def __init__(self, bd):
        super().__init__()
        self.bd = bd
        self.setWindowTitle("Crear lista de útiles")
        self.resize(350, 200)
        self._construir_ui()

    def _construir_ui(self):
        v = QVBoxLayout()
        self.txt_grado = QLineEdit()
        self.txt_grado.setPlaceholderText("Grado")
        self.txt_id_cliente = QLineEdit()
        self.txt_id_cliente.setPlaceholderText("ID Cliente")
        btn_crear = QPushButton("Crear lista")
        btn_crear.clicked.connect(self._crear_lista)
        v.addWidget(self.txt_grado)
        v.addWidget(self.txt_id_cliente)
        v.addWidget(btn_crear)
        self.setLayout(v)

    def _crear_lista(self):
        grado = self.txt_grado.text().strip()
        id_cliente = self.txt_id_cliente.text().strip()
        if not grado or not id_cliente:
            QMessageBox.warning(self, "Error", "Llena todos los campos")
            return
        try:
            id_cliente = int(id_cliente)
        except:
            QMessageBox.warning(self, "Error", "ID Cliente inválido")
            return
        self.bd.ejecutar(
            "INSERT INTO ListaUtiles(grado,id_cliente) VALUES(?,?)",
            (grado, id_cliente)
        )
        QMessageBox.information(self, "Éxito", "Lista creada correctamente")
        self.close()


class VentanaNuevaVenta(QWidget):
    def __init__(self, bd):
        super().__init__()
        self.bd = bd
        self.setWindowTitle("Registrar Venta")
        self.resize(400, 400)
        self.productos_venta = []
        self._construir_ui()

    def _construir_ui(self):
        v = QVBoxLayout()

        self.txt_id_cliente = QLineEdit()
        self.txt_id_cliente.setPlaceholderText("ID Cliente")
        v.addWidget(self.txt_id_cliente)

        h_prod = QHBoxLayout()
        self.txt_id_producto = QLineEdit()
        self.txt_id_producto.setPlaceholderText("ID Producto")
        self.txt_cantidad = QLineEdit()
        self.txt_cantidad.setPlaceholderText("Cantidad")
        btn_agregar_producto = QPushButton("Agregar producto")
        btn_agregar_producto.clicked.connect(self._agregar_producto)
        h_prod.addWidget(self.txt_id_producto)
        h_prod.addWidget(self.txt_cantidad)
        h_prod.addWidget(btn_agregar_producto)
        v.addLayout(h_prod)

        self.lbl_productos = QLabel("Productos agregados:\n")
        v.addWidget(self.lbl_productos)

        btn_finalizar = QPushButton("Finalizar venta")
        btn_finalizar.clicked.connect(self._finalizar_venta)
        v.addWidget(btn_finalizar)

        self.setLayout(v)

    def _agregar_producto(self):
        try:
            id_prod = int(self.txt_id_producto.text().strip())
            cantidad = int(self.txt_cantidad.text().strip())
            if cantidad <= 0:
                raise ValueError
        except:
            QMessageBox.warning(self, "Error", "Datos de producto inválidos")
            return

        prod = self.bd.consultar("SELECT nombre, stock, precio FROM Producto WHERE id_producto=?", (id_prod,))
        if not prod:
            QMessageBox.warning(self, "Error", "Producto no existe")
            return
        nombre, stock, precio = prod[0]
        if cantidad > stock:
            QMessageBox.warning(self, "Error", f"Stock insuficiente ({stock} disponible)")
            return

        self.productos_venta.append((id_prod, cantidad, precio))
        self._actualizar_lista_productos()
        self.txt_id_producto.clear()
        self.txt_cantidad.clear()

    def _actualizar_lista_productos(self):
        texto = "Productos agregados:\n"
        for idp, cant, precio in self.productos_venta:
            texto += f"ID {idp} - Cant {cant} - Precio {precio}\n"
        self.lbl_productos.setText(texto)

    def _finalizar_venta(self):
        if not self.productos_venta:
            QMessageBox.warning(self, "Error", "No hay productos agregados")
            return
        try:
            id_cliente = int(self.txt_id_cliente.text().strip())
        except:
            QMessageBox.warning(self, "Error", "ID Cliente inválido")
            return

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.bd.ejecutar("INSERT INTO Venta(id_cliente, fecha) VALUES(?,?)", (id_cliente, fecha))
        id_venta = self.bd.cursor.lastrowid

        for idp, cant, precio in self.productos_venta:
            self.bd.ejecutar(
                "INSERT INTO DetalleVenta(id_venta,id_producto,cantidad,precio) VALUES(?,?,?,?)",
                (id_venta, idp, cant, precio)
            )
            self.bd.ejecutar(
                "UPDATE Producto SET stock = stock - ? WHERE id_producto=?",
                (cant, idp)
            )

        QMessageBox.information(self, "Éxito", f"Venta registrada con ID {id_venta}")
        self.close()


class VentanaNuevaCompra(QWidget):
    def __init__(self, bd):
        super().__init__()
        self.bd = bd
        self.setWindowTitle("Registrar Compra")
        self.resize(400, 400)
        self.productos_compra = []
        self._construir_ui()

    def _construir_ui(self):
        v = QVBoxLayout()

        self.txt_id_proveedor = QLineEdit()
        self.txt_id_proveedor.setPlaceholderText("ID Proveedor")
        v.addWidget(self.txt_id_proveedor)

        h_prod = QHBoxLayout()
        self.txt_id_producto = QLineEdit()
        self.txt_id_producto.setPlaceholderText("ID Producto")
        self.txt_cantidad = QLineEdit()
        self.txt_cantidad.setPlaceholderText("Cantidad")
        self.txt_precio = QLineEdit()
        self.txt_precio.setPlaceholderText("Precio unitario")
        btn_agregar_producto = QPushButton("Agregar producto")
        btn_agregar_producto.clicked.connect(self._agregar_producto)
        h_prod.addWidget(self.txt_id_producto)
        h_prod.addWidget(self.txt_cantidad)
        h_prod.addWidget(self.txt_precio)
        h_prod.addWidget(btn_agregar_producto)
        v.addLayout(h_prod)

        self.lbl_productos = QLabel("Productos agregados:\n")
        v.addWidget(self.lbl_productos)

        btn_finalizar = QPushButton("Finalizar compra")
        btn_finalizar.clicked.connect(self._finalizar_compra)
        v.addWidget(btn_finalizar)

        self.setLayout(v)

    def _agregar_producto(self):
        try:
            id_prod = int(self.txt_id_producto.text().strip())
            cantidad = int(self.txt_cantidad.text().strip())
            precio = float(self.txt_precio.text().strip())
            if cantidad <= 0 or precio <= 0:
                raise ValueError
        except:
            QMessageBox.warning(self, "Error", "Datos de producto inválidos")
            return

        self.productos_compra.append((id_prod, cantidad, precio))
        self._actualizar_lista_productos()
        self.txt_id_producto.clear()
        self.txt_cantidad.clear()
        self.txt_precio.clear()

    def _actualizar_lista_productos(self):
        texto = "Productos agregados:\n"
        for idp, cant, precio in self.productos_compra:
            texto += f"ID {idp} - Cant {cant} - Precio {precio}\n"
        self.lbl_productos.setText(texto)

    def _finalizar_compra(self):
        if not self.productos_compra:
            QMessageBox.warning(self, "Error", "No hay productos agregados")
            return
        try:
            id_proveedor = int(self.txt_id_proveedor.text().strip())
        except:
            QMessageBox.warning(self, "Error", "ID Proveedor inválido")
            return

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.bd.ejecutar("INSERT INTO Compra(id_proveedor, fecha) VALUES(?,?)", (id_proveedor, fecha))
        id_compra = self.bd.cursor.lastrowid

        for idp, cant, precio in self.productos_compra:
            self.bd.ejecutar(
                "INSERT INTO DetalleCompra(id_compra,id_producto,cantidad,precio) VALUES(?,?,?,?)",
                (id_compra, idp, cant, precio)
            )
            self.bd.ejecutar(
                "UPDATE Producto SET stock = stock + ? WHERE id_producto=?",
                (cant, idp)
            )

        QMessageBox.information(self, "Éxito", f"Compra registrada con ID {id_compra}")
        self.close()


class VentanaDetalleProducto(QWidget):
    def __init__(self, producto, bd, id_usuario):
        super().__init__()
        self.producto = producto
        self.bd = bd
        self.id_usuario = id_usuario
        self.setWindowTitle("Detalle del Producto")
        self.resize(300, 400)
        self._construir_ui()

    def _construir_ui(self):
        layout = QVBoxLayout()

        id_producto, nombre, stock, precio, imagen_blob, tipo_imagen = self.producto

        # Imagen grande
        lbl_imagen_grande = QLabel()
        lbl_imagen_grande.setFixedSize(200, 200)
        lbl_imagen_grande.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_imagen_grande.setStyleSheet("border: 1px solid gray;")

        if imagen_blob:
            pixmap = ManejadorImagenes.blob_a_imagen(imagen_blob, tipo_imagen)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
                lbl_imagen_grande.setPixmap(pixmap)
            else:
                lbl_imagen_grande.setPixmap(ManejadorImagenes.obtener_imagen_predeterminada())
        else:
            lbl_imagen_grande.setPixmap(ManejadorImagenes.obtener_imagen_predeterminada())

        # Información del producto
        lbl_nombre = QLabel(f"<h2>{nombre}</h2>")
        lbl_nombre.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_precio = QLabel(f"<b>Precio:</b> Q{precio:.2f}")
        lbl_stock = QLabel(f"<b>Stock disponible:</b> {stock}")


        layout_cantidad = QHBoxLayout()
        lbl_cantidad = QLabel("Cantidad:")
        self.spin_cantidad = QSpinBox()
        self.spin_cantidad.setMinimum(1)
        self.spin_cantidad.setMaximum(stock)
        self.spin_cantidad.setValue(1)
        layout_cantidad.addWidget(lbl_cantidad)
        layout_cantidad.addWidget(self.spin_cantidad)
        layout_cantidad.addStretch()


        layout_botones = QHBoxLayout()
        btn_comprar = QPushButton("Comprar Ahora")
        btn_comprar.setStyleSheet("background-color: #28a745; color: white; font-weight: bold;")
        btn_comprar.clicked.connect(self._comprar_producto)

        btn_carrito = QPushButton("Agregar al Carrito")
        btn_carrito.setStyleSheet("background-color: #007bff; color: white;")
        btn_carrito.clicked.connect(self._agregar_al_carrito)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.close)

        layout_botones.addWidget(btn_comprar)
        layout_botones.addWidget(btn_carrito)
        layout_botones.addWidget(btn_cancelar)


        self.lbl_total = QLabel(f"<h3>Total: Q{precio:.2f}</h3>")
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_total.setStyleSheet("color: #e74c3c; font-weight: bold;")


        self.spin_cantidad.valueChanged.connect(self._actualizar_total)


        layout.addWidget(lbl_imagen_grande)
        layout.addWidget(lbl_nombre)
        layout.addWidget(lbl_precio)
        layout.addWidget(lbl_stock)
        layout.addLayout(layout_cantidad)
        layout.addWidget(self.lbl_total)
        layout.addLayout(layout_botones)

        self.setLayout(layout)

    def _actualizar_total(self):

        _, _, _, precio, _, _ = self.producto
        cantidad = self.spin_cantidad.value()
        total = precio * cantidad
        self.lbl_total.setText(f"<h3>Total: Q{total:.2f}</h3>")

    def _comprar_producto(self):

        id_producto, nombre, stock, precio, _, _ = self.producto
        cantidad = self.spin_cantidad.value()


        if cantidad > stock:
            QMessageBox.warning(self, "Stock insuficiente",
                                f"No hay suficiente stock. Disponible: {stock}")
            return


        total = precio * cantidad
        respuesta = QMessageBox.question(
            self,
            "Confirmar Compra",
            f"¿Confirmar compra de {cantidad} {nombre}(s)?\n"
            f"Precio unitario: Q{precio:.2f}\n"
            f"Total: Q{total:.2f}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            try:

                fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


                self.bd.ejecutar(
                    "INSERT INTO Venta (id_cliente, fecha, total, id_empleado) VALUES (?, ?, ?, ?)",
                    (self.id_usuario, fecha, total, 1)  # id_empleado temporal = 1
                )
                id_venta = self.bd.cursor.lastrowid


                self.bd.ejecutar(
                    "INSERT INTO DetalleVenta (id_venta, id_producto, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?)",
                    (id_venta, id_producto, cantidad, precio, total)
                )


                self.bd.ejecutar(
                    "UPDATE Producto SET stock = stock - ? WHERE id_producto = ?",
                    (cantidad, id_producto)
                )


                try:
                    self.bd.ejecutar(
                        "UPDATE Cliente SET total_compras = total_compras + ? WHERE id_cliente = ?",
                        (total, self.id_usuario)
                    )
                except:
                    pass

                QMessageBox.information(
                    self,
                    "Compra Exitosa",
                    f"¡Compra realizada con éxito!\n"
                    f"Producto: {nombre}\n"
                    f"Cantidad: {cantidad}\n"
                    f"Total: Q{total:.2f}\n"
                    f"Número de venta: {id_venta}"
                )

                self.close()

            except sqlite3.Error as e:
                QMessageBox.critical(
                    self,
                    "Error en la compra",
                    f"No se pudo completar la compra:\n{str(e)}"
                )

    def _agregar_al_carrito(self):
        """Lógica para agregar producto al carrito de compras"""
        id_producto, nombre, stock, precio, _, _ = self.producto
        cantidad = self.spin_cantidad.value()

        if cantidad > stock:
            QMessageBox.warning(self, "Stock insuficiente",
                                f"No hay suficiente stock. Disponible: {stock}")
            return

        total = precio * cantidad

        QMessageBox.information(
            self,
            "Producto agregado",
            f"Se agregó al carrito:\n"
            f"Producto: {nombre}\n"
            f"Cantidad: {cantidad}\n"
            f"Total: Q{total:.2f}\n\n"
            f"Nota: Esta funcionalidad está en desarrollo."
        )


class PantallaNuevaVenta(QWidget):
    def __init__(self, bd):
        super().__init__()
        self.bd = bd
        v = QVBoxLayout()
        self.lista_productos = QListWidget()
        btn_vender = QPushButton("Vender producto seleccionado")
        btn_vender.clicked.connect(self.vender_producto)
        v.addWidget(QLabel("Inventario de Productos"))
        v.addWidget(self.lista_productos)
        v.addWidget(btn_vender)
        self.setLayout(v)
        self.cargar_productos()

    def cargar_productos(self):
        self.lista_productos.clear()
        cursor = self.bd.conexion.cursor()
        cursor.execute("SELECT id_producto, nombre, stock, precio FROM Producto")
        self.productos = cursor.fetchall()
        for p in self.productos:
            self.lista_productos.addItem(f"{p[1]} - Stock: {p[2]} - Q{p[3]}")

    def vender_producto(self):
        item = self.lista_productos.currentItem()
        if not item:
            QMessageBox.warning(self, "Aviso", "Selecciona un producto.")
            return

        idx = self.lista_productos.currentRow()
        id_producto, nombre, stock, precio = self.productos[idx]

        if stock <= 0:
            QMessageBox.warning(self, "Sin stock", f"No hay stock de {nombre}.")
            return

        cursor = self.bd.conexion.cursor()
        cursor.execute("UPDATE Productos SET stock = stock - 1 WHERE id_producto = ?", (id_producto,))
        self.bd.conexion.commit()
        QMessageBox.information(self, "Venta realizada", f"Se vendió 1 {nombre}.")
        self.cargar_productos()


class PantallaNuevaCompra(QWidget):
    def __init__(self, bd):
        super().__init__()
        self.bd = bd
        self.productos_compra = []
        layout = QVBoxLayout()

        self.txt_id_proveedor = QLineEdit()
        self.txt_id_proveedor.setPlaceholderText("ID Proveedor")
        layout.addWidget(self.txt_id_proveedor)

        # Agregar productos
        h = QHBoxLayout()
        self.txt_id_producto = QLineEdit();
        self.txt_id_producto.setPlaceholderText("ID Producto")
        self.txt_cantidad = QLineEdit();
        self.txt_cantidad.setPlaceholderText("Cantidad")
        self.txt_precio = QLineEdit();
        self.txt_precio.setPlaceholderText("Precio unitario")
        btn_agregar = QPushButton("Agregar producto");
        btn_agregar.clicked.connect(self._agregar_producto)
        for w in [self.txt_id_producto, self.txt_cantidad, self.txt_precio, btn_agregar]: h.addWidget(w)
        layout.addLayout(h)

        # Lista de productos agregados
        self.lbl_productos = QLabel("Productos agregados:\n")
        layout.addWidget(self.lbl_productos)

        # Botón finalizar compra
        btn_final = QPushButton("Finalizar compra")
        btn_final.clicked.connect(self._finalizar_compra)
        layout.addWidget(btn_final)

        self.setLayout(layout)

    def _agregar_producto(self):
        try:
            id_prod = int(self.txt_id_producto.text().strip())
            cantidad = int(self.txt_cantidad.text().strip())
            precio = float(self.txt_precio.text().strip())
            if cantidad <= 0 or precio <= 0: raise ValueError
        except:
            QMessageBox.warning(self, "Error", "Datos de producto inválidos")
            return
        self.productos_compra.append((id_prod, cantidad, precio))
        self._actualizar_lista()
        self.txt_id_producto.clear();
        self.txt_cantidad.clear();
        self.txt_precio.clear()

    def _actualizar_lista(self):
        texto = "Productos agregados:\n"
        for idp, cant, precio in self.productos_compra:
            texto += f"ID {idp} - Cant {cant} - Precio {precio}\n"
        self.lbl_productos.setText(texto)

    def _finalizar_compra(self):
        if not self.productos_compra:
            QMessageBox.warning(self, "Error", "No hay productos agregados")
            return
        try:
            id_proveedor = int(self.txt_id_proveedor.text().strip())
        except:
            QMessageBox.warning(self, "Error", "ID Proveedor inválido")
            return
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.bd.ejecutar("INSERT INTO Compra(id_proveedor, fecha) VALUES(?,?)", (id_proveedor, fecha))
        id_compra = self.bd.cursor.lastrowid
        for idp, cant, precio in self.productos_compra:
            self.bd.ejecutar("INSERT INTO DetalleCompra(id_compra,id_producto,cantidad,precio) VALUES(?,?,?,?)",
                             (id_compra, idp, cant, precio))
            self.bd.ejecutar("UPDATE Producto SET stock = stock + ? WHERE id_producto=?", (cant, idp))
        QMessageBox.information(self, "Éxito", f"Compra registrada con ID {id_compra}")
        self.productos_compra.clear();
        self.txt_id_proveedor.clear();
        self.lbl_productos.setText("Productos agregados:\n")


class PantallaCrearLista(QWidget):
    def __init__(self, bd):
        super().__init__()
        self.bd = bd
        layout = QVBoxLayout()

        self.txt_grado = QLineEdit();
        self.txt_grado.setPlaceholderText("Grado")
        self.txt_id_cliente = QLineEdit();
        self.txt_id_cliente.setPlaceholderText("ID Cliente")
        btn_crear = QPushButton("Crear lista");
        btn_crear.clicked.connect(self._crear_lista)

        for w in [self.txt_grado, self.txt_id_cliente, btn_crear]:
            layout.addWidget(w)
        self.setLayout(layout)

    def _crear_lista(self):
        grado = self.txt_grado.text().strip()
        id_cliente = self.txt_id_cliente.text().strip()
        if not grado or not id_cliente:
            QMessageBox.warning(self, "Error", "Llena todos los campos")
            return
        try:
            id_cliente = int(id_cliente)
        except:
            QMessageBox.warning(self, "Error", "ID Cliente inválido")
            return
        self.bd.ejecutar("INSERT INTO ListaUtiles(grado,id_cliente) VALUES(?,?)", (grado, id_cliente))
        QMessageBox.information(self, "Éxito", "Lista creada correctamente")
        self.txt_grado.clear();
        self.txt_id_cliente.clear()


class PantallaMostrarInventario(QWidget):
    def __init__(self, bd):
        super().__init__()
        self.bd = bd
        self._construir_ui()
        self.cargar_inventario()

    def _construir_ui(self):
        layout = QVBoxLayout()

        # Título
        titulo = QLabel("Inventario de Productos")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin: 10px;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)

        # Controles de búsqueda y filtros
        controles_layout = QHBoxLayout()

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Buscar producto...")
        self.txt_buscar.textChanged.connect(self.filtrar_inventario)

        self.combo_categoria = QComboBox()
        self.combo_categoria.addItem("Todas las categorías", 0)
        self.combo_categoria.currentIndexChanged.connect(self.filtrar_inventario)

        self.btn_actualizar = QPushButton("🔄 Actualizar")
        self.btn_actualizar.clicked.connect(self.cargar_inventario)

        self.btn_exportar = QPushButton("📊 Exportar Reporte")
        self.btn_exportar.clicked.connect(self.exportar_reporte)

        controles_layout.addWidget(QLabel("Buscar:"))
        controles_layout.addWidget(self.txt_buscar)
        controles_layout.addWidget(QLabel("Categoría:"))
        controles_layout.addWidget(self.combo_categoria)
        controles_layout.addWidget(self.btn_actualizar)
        controles_layout.addWidget(self.btn_exportar)
        controles_layout.addStretch()

        layout.addLayout(controles_layout)

        # Tabla de inventario
        self.tabla_inventario = QTableWidget()
        self.tabla_inventario.setColumnCount(8)
        self.tabla_inventario.setHorizontalHeaderLabels([
            "ID", "Nombre", "Categoría", "Precio", "Stock",
            "Límite Stock", "Estado", "Acciones"
        ])

        # Configurar tabla
        self.tabla_inventario.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_inventario.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_inventario.setAlternatingRowColors(True)
        self.tabla_inventario.horizontalHeader().setStretchLastSection(True)

        # Ajustar anchos de columnas
        self.tabla_inventario.setColumnWidth(0, 50)  # ID
        self.tabla_inventario.setColumnWidth(1, 200)  # Nombre
        self.tabla_inventario.setColumnWidth(2, 120)  # Categoría
        self.tabla_inventario.setColumnWidth(3, 80)  # Precio
        self.tabla_inventario.setColumnWidth(4, 70)  # Stock
        self.tabla_inventario.setColumnWidth(5, 90)  # Límite
        self.tabla_inventario.setColumnWidth(6, 100)  # Estado

        layout.addWidget(self.tabla_inventario)

        # Estadísticas
        self.lbl_estadisticas = QLabel()
        self.lbl_estadisticas.setStyleSheet("font-size: 14px; color: #7f8c8d; margin: 5px;")
        layout.addWidget(self.lbl_estadisticas)

        self.setLayout(layout)

    def cargar_categorias(self):
        """Carga las categorías en el combobox"""
        self.combo_categoria.clear()
        self.combo_categoria.addItem("Todas las categorías", 0)

        categorias = self.bd.consultar("SELECT id_categoria, nombre FROM Categoria ORDER BY nombre")
        for id_cat, nombre in categorias:
            self.combo_categoria.addItem(nombre, id_cat)

    def cargar_inventario(self):
        """Carga todos los productos en la tabla"""
        try:
            # Cargar categorías primero
            self.cargar_categorias()

            # Consulta para obtener productos con información de categoría
            query = """
                SELECT 
                    p.id_producto, p.nombre, c.nombre as categoria, 
                    p.precio, p.stock, p.limite_stock,
                    p.imagen, p.tipo_imagen
                FROM Producto p
                LEFT JOIN Categoria c ON p.id_categoria = c.id_categoria
                ORDER BY p.nombre
            """

            productos = self.bd.consultar(query)

            self.tabla_inventario.setRowCount(len(productos))
            self.productos_completos = productos  # Guardar para filtros

            for row, producto in enumerate(productos):
                id_producto, nombre, categoria, precio, stock, limite_stock, imagen, tipo_imagen = producto

                # Determinar estado del stock
                if stock == 0:
                    estado = "SIN STOCK"
                    color_estado = "#e74c3c"
                elif stock <= (limite_stock or 5):
                    estado = "BAJO STOCK"
                    color_estado = "#f39c12"
                else:
                    estado = "DISPONIBLE"
                    color_estado = "#27ae60"

                # Llenar la tabla
                self.tabla_inventario.setItem(row, 0, QTableWidgetItem(str(id_producto)))
                self.tabla_inventario.setItem(row, 1, QTableWidgetItem(nombre))
                self.tabla_inventario.setItem(row, 2, QTableWidgetItem(categoria or "Sin categoría"))
                self.tabla_inventario.setItem(row, 3, QTableWidgetItem(f"Q{precio:.2f}"))
                self.tabla_inventario.setItem(row, 4, QTableWidgetItem(str(stock)))
                self.tabla_inventario.setItem(row, 5, QTableWidgetItem(str(limite_stock or "N/A")))

                # Celda de estado con color
                item_estado = QTableWidgetItem(estado)
                item_estado.setForeground(QColor(color_estado))
                self.tabla_inventario.setItem(row, 6, item_estado)

                # Botones de acción
                widget_acciones = QWidget()
                layout_acciones = QHBoxLayout(widget_acciones)
                layout_acciones.setContentsMargins(5, 2, 5, 2)

                btn_editar = QPushButton("✏️")
                btn_editar.setToolTip("Editar producto")
                btn_editar.setFixedSize(30, 25)
                btn_editar.setStyleSheet(
                    "QPushButton { background-color: #3498db; color: white; border: none; border-radius: 3px; }")
                btn_editar.clicked.connect(lambda checked, prod_id=id_producto: self.editar_producto(prod_id))

                btn_eliminar = QPushButton("🗑️")
                btn_eliminar.setToolTip("Eliminar producto")
                btn_eliminar.setFixedSize(30, 25)
                btn_eliminar.setStyleSheet(
                    "QPushButton { background-color: #e74c3c; color: white; border: none; border-radius: 3px; }")
                btn_eliminar.clicked.connect(lambda checked, prod_id=id_producto: self.eliminar_producto(prod_id))

                layout_acciones.addWidget(btn_editar)
                layout_acciones.addWidget(btn_eliminar)
                layout_acciones.addStretch()

                self.tabla_inventario.setCellWidget(row, 7, widget_acciones)

            # Actualizar estadísticas
            self.actualizar_estadisticas(productos)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el inventario:\n{str(e)}")

    def filtrar_inventario(self):
        """Filtra los productos según los criterios de búsqueda"""
        try:
            texto_buscar = self.txt_buscar.text().lower()
            categoria_id = self.combo_categoria.currentData()

            productos_filtrados = []
            for producto in self.productos_completos:
                id_producto, nombre, categoria, precio, stock, limite_stock, imagen, tipo_imagen = producto

                # Filtro por texto
                coincide_texto = (texto_buscar in nombre.lower() or
                                  texto_buscar in str(id_producto) or
                                  texto_buscar in (categoria or "").lower())

                # Filtro por categoría
                coincide_categoria = (categoria_id == 0 or
                                      (producto[2] and categoria_id == self.obtener_id_categoria(producto[2])))

                if coincide_texto and coincide_categoria:
                    productos_filtrados.append(producto)

            # Actualizar tabla con productos filtrados
            self.tabla_inventario.setRowCount(len(productos_filtrados))
            for row, producto in enumerate(productos_filtrados):
                for col, valor in enumerate(producto[:7]):  # Solo las primeras 7 columnas
                    if col == 3:  # Precio
                        self.tabla_inventario.setItem(row, col, QTableWidgetItem(f"Q{valor:.2f}"))
                    else:
                        self.tabla_inventario.setItem(row, col, QTableWidgetItem(str(valor)))

            self.actualizar_estadisticas(productos_filtrados)

        except Exception as e:
            print(f"Error al filtrar: {e}")

    def obtener_id_categoria(self, nombre_categoria):
        """Obtiene el ID de categoría por nombre"""
        categorias = self.bd.consultar("SELECT id_categoria FROM Categoria WHERE nombre=?", (nombre_categoria,))
        return categorias[0][0] if categorias else 0

    def actualizar_estadisticas(self, productos):
        """Actualiza las estadísticas del inventario"""
        total_productos = len(productos)
        total_stock = sum(producto[4] for producto in productos)
        sin_stock = sum(1 for producto in productos if producto[4] == 0)
        bajo_stock = sum(1 for producto in productos if 0 < producto[4] <= (producto[5] or 5))
        valor_total = sum(producto[3] * producto[4] for producto in productos)

        estadisticas = (
            f"📊 Estadísticas: {total_productos} productos | "
            f"Stock total: {total_stock} unidades | "
            f"Sin stock: {sin_stock} | "
            f"Bajo stock: {bajo_stock} | "
            f"Valor total: Q{valor_total:,.2f}"
        )
        self.lbl_estadisticas.setText(estadisticas)

    def editar_producto(self, id_producto):
        """Abre diálogo para editar producto"""
        QMessageBox.information(self, "Editar Producto",
                                f"Funcionalidad en desarrollo.\nEditar producto ID: {id_producto}")

    def eliminar_producto(self, id_producto):
        """Elimina un producto del inventario"""
        respuesta = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Estás seguro de que quieres eliminar este producto (ID: {id_producto})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            try:
                self.bd.ejecutar("DELETE FROM Producto WHERE id_producto=?", (id_producto,))
                QMessageBox.information(self, "Éxito", "Producto eliminado correctamente")
                self.cargar_inventario()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar el producto:\n{str(e)}")

    def exportar_reporte(self):
        """Exporta un reporte del inventario"""
        try:
            # Aquí podrías implementar la exportación a CSV o PDF
            QMessageBox.information(self, "Exportar Reporte",
                                    "Funcionalidad de exportación en desarrollo.\n"
                                    "Se exportaría el inventario actual a CSV/PDF.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo exportar el reporte:\n{str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    tipo_usuario = VentanaTipoUsuario()
    tipo_usuario.show()

    sys.exit(app.exec())
