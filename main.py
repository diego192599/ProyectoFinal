import sys
import sqlite3
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit,
    QVBoxLayout, QMessageBox,QInputDialog, QHBoxLayout
)
from PySide6.QtGui import QFont, QPixmap, QIcon
from PySide6.QtCore import Qt, QSize

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

        # Insertar en la BD
        self.bd.ejecutar(
            "INSERT INTO Usuario(nombre,usuario,contrasena,tipo) VALUES(?,?,?,?)",
            (nombre.strip(), usuario.strip(), contrasena.strip(), "admin")  # o "padre", según contexto
        )
        QMessageBox.information(parent, "Éxito", "Usuario registrado con éxito.")

    def listar(self):
        filas = self.bd.consultar("SELECT * FROM Usuario")
        for f in filas:
            print(f"ID:{f[0]} | Nombre:{f[1]} | Usuario:{f[2]}")


class GestionCategorias:
    def __init__(self, bd):
        self.bd = bd

    def agregar(self):
        nombre = input("Nombre categoría: ")
        self.bd.ejecutar("INSERT INTO Categoria(nombre) VALUES(?)", (nombre,))
        print("Categoría agregada")

    def mostrar(self):
        res = self.bd.consultar("SELECT * FROM Categoria")
        for r in res:
            print(r)

class GestionProductos:
    def __init__(self, bd):
        self.bd = bd

    def agregar(self):
        id_categoria = input("ID categoría: ")
        nombre = input("Nombre producto: ")
        precio = float(input("Precio: "))
        stock = int(input("Stock: "))
        limite_stock = input("Límite stock: ")
        limite_stock = int(limite_stock) if limite_stock else None
        imagen = input("Ruta imagen: ")
        self.bd.ejecutar(
            "INSERT INTO Producto(id_categoria,nombre,precio,stock,limite_stock,imagen) VALUES(?,?,?,?,?,?)",
            (id_categoria, nombre, precio, stock, limite_stock, imagen))
        print("Producto agregado correctamente.")

    def mostrar(self):
        res = self.bd.consultar("SELECT * FROM Producto")
        if not res:
            print("No hay productos.")
            return
        for r in res:
            print(r)

class GestionClientes:
    def __init__(self, bd):
        self.bd = bd

    def agregar(self):
        nombre = input("Nombre: ")
        telefono = input("Teléfono: ")
        correo = input("Correo: ")
        self.bd.ejecutar("INSERT INTO Cliente(nombre,telefono,correo,total_compras,descuento) VALUES(?,?,?,?,?)",
                         (nombre,telefono,correo,0,0))
        print("Cliente agregado")

    def mostrar(self):
        res = self.bd.consultar("SELECT * FROM Cliente")
        for r in res:
            print(r)

class GestionEmpleados:
    def __init__(self, bd):
        self.bd = bd

    def agregar(self):
        nombre = input("Nombre: ")
        telefono = input("Teléfono: ")
        correo = input("Correo: ")
        salario = float(input("Salario: "))
        self.bd.ejecutar("INSERT INTO Empleado(nombre,telefono,correo,salario) VALUES(?,?,?,?)",
                         (nombre,telefono,correo,salario))
        print("Empleado agregado correctamente.")

    def mostrar(self):
        res = self.bd.consultar("SELECT * FROM Empleado")
        for r in res:
            print(r)

class GestionProveedores:
    def __init__(self, bd):
        self.bd = bd

    def agregar(self):
        nombre = input("Nombre: ")
        empresa = input("Empresa: ")
        telefono = input("Teléfono: ")
        self.bd.ejecutar("INSERT INTO Proveedor(nombre,empresa,telefono) VALUES(?,?,?)",
                         (nombre,empresa,telefono))
        print("Proveedor agregado con éxito.")

    def listar(self):
        filas = self.bd.consultar("SELECT * FROM Proveedor")
        if not filas:
            print("No hay proveedores.")
            return
        for f in filas:
            print(f"ID:{f[0]} | Nombre:{f[1]} | Empresa:{f[2]} | Teléfono:{f[3]}")

    def eliminar(self):
        ide = input("ID proveedor a eliminar: ")
        self.bd.ejecutar("DELETE FROM Proveedor WHERE id_proveedor=?", (ide,))
        print("Proveedor eliminado.")


class GestionListaUtiles:
    def __init__(self, bd):
        self.bd = bd

    def crear_lista(self):
        grado = input("Grado: ")
        id_cliente = input("ID Cliente: ")
        self.bd.ejecutar("INSERT INTO ListaUtiles(grado,id_cliente) VALUES(?,?)",(grado,id_cliente))
        print("Lista creada")

    def agregar_item(self):
        id_lista = input("ID Lista útiles: ")
        codigo = input("Código producto: ")
        cantidad = int(input("Cantidad: "))
        self.bd.ejecutar("INSERT INTO DetalleListaUtiles(id_lista,codigo_producto,cantidad) VALUES(?,?,?)",
                         (id_lista,codigo,cantidad))
        print("Item agregado")

    def mostrar(self):
        res = self.bd.consultar("SELECT * FROM ListaUtiles")
        for r in res:
            print(r)


class GestionCompra:
    def __init__(self, bd):
        self.bd = bd

    def registrar(self):
        id_proveedor = input("ID proveedor: ")
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total = float(input("Total compra: "))
        self.bd.ejecutar("INSERT INTO Compra(id_proveedor,fecha,total) VALUES(?,?,?)",
                         (id_proveedor, fecha, total))
        print("Compra registrada correctamente.")

    def listar(self):
        filas = self.bd.consultar("SELECT * FROM Compra")
        for f in filas:
            print(f"ID:{f[0]} | Proveedor:{f[1]} | Fecha:{f[2]} | Total:{f[3]}")


class GestionDetallesCompra:
    def __init__(self, bd):
        self.bd = bd

    def agregar_detalle(self, id_compra, id_producto, cantidad, precio_unitario):
        subtotal = cantidad * precio_unitario
        self.bd.ejecutar(
            "INSERT INTO DetalleCompra(id_compra, id_producto, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?)",
            (id_compra, id_producto, cantidad, precio_unitario, subtotal))
        print("Detalle de compra agregado")

    def mostrar(self):
        res = self.bd.consultar("SELECT * FROM DetalleCompra")
        for r in res:
            print(r)


class GestionVentas:
    def __init__(self, bd):
        self.bd = bd

    def registrar_venta(self, id_cliente, fecha, total, id_empleado=None):
        self.bd.ejecutar(
            "INSERT INTO Venta(id_cliente, fecha, total, id_empleado) VALUES (?, ?, ?, ?)",
            (id_cliente, fecha, total, id_empleado))
        print("Venta registrada")

    def mostrar(self):
        res = self.bd.consultar("SELECT * FROM Venta")
        for r in res:
            print(r)


class GestionDetallesVenta:
    def __init__(self, bd):
        self.bd = bd

    def agregar_detalle(self, id_venta, id_producto, cantidad, precio_unitario):
        subtotal = cantidad * precio_unitario
        self.bd.ejecutar(
            "INSERT INTO DetalleVenta(id_venta, id_producto, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?)",
            (id_venta, id_producto, cantidad, precio_unitario, subtotal))
        print("Detalle de venta agregado")

    def mostrar(self):
        res = self.bd.consultar("SELECT * FROM DetalleVenta")
        for r in res:
            print(r)

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
            self.padres_principal = VentanaPadres(filas[0][0])
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

        btn_volver = QPushButton("Volver")
        btn_volver.clicked.connect(self._volver)

        v.addWidget(lbl)
        v.addWidget(self.txt_usuario)
        v.addWidget(self.txt_contra)
        v.addWidget(btn_ingresar)
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
            self.admin_principal = VentanaAdmin()
            self.admin_principal.show()
        else:
            QMessageBox.critical(self, "Error", "Usuario o contraseña incorrectos.")

    def _volver(self):
        self.close()
        self.tipo_usuario = VentanaTipoUsuario()
        self.tipo_usuario.show()

class VentanaPadres(QWidget):
    def __init__(self,id_usuario):
        super().__init__()
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

        logo = QLabel()
        pixmap = QPixmap("logo.png")
        logo.setPixmap(pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(logo)

        titulo = QLabel("Bienvenido, padre de familia")
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(titulo)

        btn_catalogo = QPushButton(" Ver catálogo")
        btn_catalogo.setIcon(QIcon("icons/catalogo.png"))  # Icono opcional
        btn_catalogo.setIconSize(QSize(32,32))
        btn_catalogo.clicked.connect(lambda: print("Mostrar catálogo"))

        btn_listado = QPushButton(" Crear mi listado de útiles")
        btn_listado.setIcon(QIcon("icons/listado.png"))
        btn_listado.setIconSize(QSize(32,32))
        btn_listado.clicked.connect(lambda: print("Crear listado"))

        btn_cerrar = QPushButton(" Cerrar sesión")
        btn_cerrar.setIcon(QIcon("icons/salir.png"))
        btn_cerrar.setIconSize(QSize(32,32))
        btn_cerrar.clicked.connect(self.close)

        v.addWidget(btn_catalogo)
        v.addWidget(btn_listado)
        v.addWidget(btn_cerrar)
        v.addStretch()

        self.setLayout(v)

class VentanaAdmin(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Administrador - Librería ABC")
        self.resize(800, 600)
        self._aplicar_estilos()
        self._construir_ui()

    def _aplicar_estilos(self):
        self.setStyleSheet("""
            QWidget { background-color: #f0f2f5; font-family: 'Segoe UI'; }
            QLabel#titulo {
                font-size: 26px;
                font-weight: bold;
                color: #222;
            }
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                  stop:0 #f7941d, stop:1 #f15a24);
                color: white;
                border-radius: 12px;
                padding: 14px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                  stop:0 #f15a24, stop:1 #f7941d);
            }
        """)

    def _construir_ui(self):
        v = QVBoxLayout()
        v.setSpacing(25)

        # Logo
        logo = QLabel()
        pixmap = QPixmap("logo.png")  # Coloca tu logo aquí
        logo.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(logo)

        # Título
        titulo = QLabel("Panel de administración")
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(titulo)

        # Botones
        btn_productos = QPushButton(" Gestionar productos")
        btn_productos.setIcon(QIcon("icons/producto.png"))
        btn_productos.setIconSize(QSize(32,32))
        btn_productos.clicked.connect(lambda: print("Gestionar productos"))

        btn_listas = QPushButton(" Gestionar listas de útiles")
        btn_listas.setIcon(QIcon("icons/lista.png"))
        btn_listas.setIconSize(QSize(32,32))
        btn_listas.clicked.connect(lambda: print("Gestionar listas"))

        btn_cerrar = QPushButton(" Cerrar sesión")
        btn_cerrar.setIcon(QIcon("icons/salir.png"))
        btn_cerrar.setIconSize(QSize(32,32))
        btn_cerrar.clicked.connect(self.close)

        v.addWidget(btn_productos)
        v.addWidget(btn_listas)
        v.addWidget(btn_cerrar)
        v.addStretch()

        self.setLayout(v)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    tipo_usuario = VentanaTipoUsuario()
    tipo_usuario.show()

    sys.exit(app.exec())

