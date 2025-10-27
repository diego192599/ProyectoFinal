import sys
import sqlite3
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit,
    QVBoxLayout, QMessageBox,QInputDialog, QHBoxLayout, QStackedLayout
)
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtCore import Qt

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
            codigo_producto INTEGER PRIMARY KEY AUTOINCREMENT,
            id_categoria INTEGER,
            nombre TEXT NOT NULL,
            precio REAL,
            stock INTEGER,
            limite_stock INTEGER,
            imagen TEXT,
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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER,
            fecha TEXT,
            total REAL,
            id_empleado INTEGER,
            FOREIGN KEY(id_cliente) REFERENCES Cliente(id_cliente),
            FOREIGN KEY(id_empleado) REFERENCES Empleado(id_empleado)
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS DetalleVenta(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_venta INTEGER,
            id_producto INTEGER,
            cantidad INTEGER,
            precio_unitario REAL,
            subtotal REAL,
            FOREIGN KEY(id_venta) REFERENCES Venta(id),
            FOREIGN KEY(id_producto) REFERENCES Producto(codigo_producto)
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Compra(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_proveedor INTEGER,
            fecha TEXT,
            total REAL,
            FOREIGN KEY(id_proveedor) REFERENCES Proveedor(id_proveedor)
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS DetalleCompra(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_compra INTEGER,
            id_producto INTEGER,
            cantidad INTEGER,
            precio_unitario REAL,
            subtotal REAL,
            FOREIGN KEY(id_compra) REFERENCES Compra(id),
            FOREIGN KEY(id_producto) REFERENCES Producto(codigo_producto)
        )""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS ListaUtiles(
            id_lista INTEGER PRIMARY KEY AUTOINCREMENT,
            grado TEXT,
            id_cliente INTEGER,
            FOREIGN KEY(id_cliente) REFERENCES Cliente(id_cliente)
        )""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS DetalleListaUtiles(
            id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
            id_lista INTEGER,
            codigo_producto INTEGER,
            cantidad INTEGER,
            FOREIGN KEY(id_lista) REFERENCES ListaUtiles(id_lista),
            FOREIGN KEY(codigo_producto) REFERENCES Producto(codigo_producto)
        )""")

        self.conexion.commit()

    def ejecutar(self, query, params=()):
        self.cursor.execute(query, params)
        self.conexion.commit()

    def consultar(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

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
    def __init__(self, nombre, usuario, contrasena,tipo):
        self.nombre = nombre
        self.usuario = usuario
        self.contrasena = contrasena
        self.tipo = tipo


class Compra:
    def __init__(self, id_proveedor,fecha,total):
        self.id_proveedor = id_proveedor
        self.fecha = fecha
        self.total = total

class DetalleCompra:
    def __init__(self, id_compra, id_producto, cantidad, precio_unitario, subtotal):
        self.id_compra = id_compra
        self.id_producto = id_producto
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.subtotal = subtotal


class Venta:
    def __init__(self, id_cliente, fecha, total, id_empleado=None):
        self.id_cliente = id_cliente
        self.fecha = fecha
        self.total = total
        self.id_empleado = id_empleado

class DetalleVenta:
    def __init__(self, id_venta, id_producto, cantidad, precio_unitario, subtotal):
        self.id_venta = id_venta
        self.id_producto = id_producto
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.subtotal = subtotal


class GestionUsuario:
    def __init__(self, bd):
        self.bd = bd

    def agregar(self, parent=None):  # parent es la ventana que lo llama
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

class VentanaTipoUsuario(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Selecciona tipo de usuario")
        self.resize(400, 250)
        self._aplicar_estilos()
        self._construir_ui()

    def _aplicar_estilos(self):
        self.setStyleSheet("""
            QWidget { background-color: #f2f6fa; font-family: 'Segoe UI'; }
            QPushButton {
                background-color: #007bff;
                color: white;
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #0056b3; }
        """)

    def _construir_ui(self):
        v = QVBoxLayout()
        titulo = QLabel("Bienvenido a Librería ABC")
        titulo.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_padres = QPushButton("Padres de familia")
        btn_padres.clicked.connect(self._abrir_padres)

        btn_admin = QPushButton("Administrador / Empleado")
        btn_admin.clicked.connect(self._abrir_admin)

        v.addStretch()
        v.addWidget(titulo)
        v.addSpacing(20)
        v.addWidget(btn_padres)
        v.addWidget(btn_admin)
        v.addStretch()
        self.setLayout(v)

    def _abrir_padres(self):
        self.hide()
        self.padres = VentanaLoginPadres()
        self.padres.show()

    def _abrir_admin(self):
        self.hide()
        self.admin = VentanaLoginAdmin()
        self.admin.show()

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
            self.padres_principal = VentanaPadres(self.bd,filas[0][0])
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
        self.setWindowTitle("Padres de familia - Librería ABC")
        self.resize(600, 400)
        self._aplicar_estilos()
        self._construir_ui()

    def _aplicar_estilos(self):
        self.setStyleSheet("""
            QWidget { background-color: #f0f2f5; font-family: 'Segoe UI'; }
            QLabel#titulo {
                font-size: 24px;
                font-weight: bold;
                color: #333;
            }
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                  stop:0 #6cace4, stop:1 #1c3f95);
                color: white;
                border-radius: 12px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                  stop:0 #1c3f95, stop:1 #6cace4);
            }
        """)

    def _construir_ui(self):
        v = QVBoxLayout()
        v.setSpacing(20)

        # Logo
        logo = QLabel()
        pixmap = QPixmap("logo.png")
        logo.setPixmap(pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(logo)

        titulo = QLabel("Bienvenido, padre de familia")
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(titulo)

        # Botones
        btn_catalogo = QPushButton(" Ver catálogo")
        btn_catalogo.clicked.connect(lambda: print("Mostrar catálogo"))

        btn_listado = QPushButton(" Crear mi listado de útiles")
        btn_listado.clicked.connect(lambda: self._abrir_listado_utiles())

        btn_cerrar = QPushButton(" Cerrar sesión")
        btn_cerrar.clicked.connect(self.close)

        for b in [btn_catalogo, btn_listado, btn_cerrar]:
            v.addWidget(b)

        v.addStretch()
        self.setLayout(v)

    def _abrir_listado_utiles(self):
        self.ventana_listado = VentanaCrearLista(self.bd)
        self.ventana_listado.show()

class VentanaAdmin(QWidget):
    def __init__(self, bd, mostrar_login=None):
        super().__init__()
        self.bd = bd
        self.mostrar_login = mostrar_login  # Función para mostrar login
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
            "listas": PantallaCrearLista(self.bd)
        }
        for w in self.pantallas.values():
            self.stacked_layout.addWidget(w)

        botones = [
            ("Agregar categoría", lambda: self._cambiar_pantalla("categoria")),
            ("Agregar producto", lambda: self._cambiar_pantalla("producto")),
            ("Agregar cliente", lambda: self._cambiar_pantalla("cliente")),
            ("Agregar empleado", lambda: self._cambiar_pantalla("empleado")),
            ("Agregar proveedor", lambda: self._cambiar_pantalla("proveedor")),
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
        v = QVBoxLayout()
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
        self.txt_imagen = QLineEdit()
        self.txt_imagen.setPlaceholderText("Ruta imagen (opcional)")
        btn_agregar = QPushButton("Agregar producto")
        btn_agregar.clicked.connect(self._agregar_producto)
        for w in [self.txt_id_categoria, self.txt_nombre, self.txt_precio,
                  self.txt_stock, self.txt_limite, self.txt_imagen, btn_agregar]:
            v.addWidget(w)
        self.setLayout(v)

    def _agregar_producto(self):
        try:
            id_categoria = int(self.txt_id_categoria.text().strip())
            nombre = self.txt_nombre.text().strip()
            precio = float(self.txt_precio.text().strip())
            stock = int(self.txt_stock.text().strip())
            limite_stock = self.txt_limite.text().strip()
            limite_stock = int(limite_stock) if limite_stock else None
            imagen = self.txt_imagen.text().strip()
            if not nombre:
                raise ValueError("Nombre vacío")
        except ValueError as e:
            QMessageBox.warning(self, "Error", f"Datos inválidos: {e}")
            return
        self.bd.ejecutar(
            "INSERT INTO Producto(id_categoria,nombre,precio,stock,limite_stock,imagen) VALUES(?,?,?,?,?,?)",
            (id_categoria, nombre, precio, stock, limite_stock, imagen)
        )
        QMessageBox.information(self, "Éxito", "Producto agregado correctamente")
        self.txt_id_categoria.clear()
        self.txt_nombre.clear()
        self.txt_precio.clear()
        self.txt_stock.clear()
        self.txt_limite.clear()
        self.txt_imagen.clear()

class PantallaAgregarCliente(QWidget):
    def __init__(self, bd):
        super().__init__()
        self.bd = bd
        v = QVBoxLayout()
        self.txt_nombre = QLineEdit(); self.txt_nombre.setPlaceholderText("Nombre")
        self.txt_telefono = QLineEdit(); self.txt_telefono.setPlaceholderText("Teléfono")
        self.txt_correo = QLineEdit(); self.txt_correo.setPlaceholderText("Correo")
        btn_agregar = QPushButton("Agregar cliente"); btn_agregar.clicked.connect(self._agregar_cliente)
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
        self.txt_nombre.clear(); self.txt_telefono.clear(); self.txt_correo.clear()

class PantallaAgregarEmpleado(QWidget):
    def __init__(self, bd):
        super().__init__()
        self.bd = bd
        v = QVBoxLayout()
        self.txt_nombre = QLineEdit(); self.txt_nombre.setPlaceholderText("Nombre")
        self.txt_telefono = QLineEdit(); self.txt_telefono.setPlaceholderText("Teléfono")
        self.txt_correo = QLineEdit(); self.txt_correo.setPlaceholderText("Correo")
        self.txt_salario = QLineEdit(); self.txt_salario.setPlaceholderText("Salario")
        btn_agregar = QPushButton("Agregar empleado"); btn_agregar.clicked.connect(self._agregar_empleado)
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
        self.txt_nombre.clear(); self.txt_telefono.clear(); self.txt_correo.clear(); self.txt_salario.clear()

class PantallaAgregarProveedor(QWidget):
    def __init__(self, bd):
        super().__init__()
        self.bd = bd
        v = QVBoxLayout()
        self.txt_nombre = QLineEdit(); self.txt_nombre.setPlaceholderText("Nombre")
        self.txt_empresa = QLineEdit(); self.txt_empresa.setPlaceholderText("Empresa")
        self.txt_telefono = QLineEdit(); self.txt_telefono.setPlaceholderText("Teléfono")
        btn_agregar = QPushButton("Agregar proveedor"); btn_agregar.clicked.connect(self._agregar_proveedor)
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
        self.txt_nombre.clear(); self.txt_empresa.clear(); self.txt_telefono.clear()



if __name__ == "__main__":
    app = QApplication(sys.argv)

    tipo_usuario = VentanaTipoUsuario()
    tipo_usuario.show()

    sys.exit(app.exec())

