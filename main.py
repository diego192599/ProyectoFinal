import sys
import sqlite3
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit,
    QVBoxLayout, QMessageBox,QInputDialog, QHBoxLayout, QStackedLayout, QListWidget,
    QListWidgetItem
)
from PySide6.QtGui import QFont
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
        # CORREGIDO: Nombre consistente de tablas
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

        # CORREGIDO: Referencias correctas en tablas
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
        self.setWindowTitle("Padres de Familia")
        self.resize(600, 400)
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
        self.btn_listado.clicked.connect(self.mostrar_listado)
        self.btn_cerrar.clicked.connect(self.cerrar_sesion)

        for btn in [self.btn_catalogo, self.btn_listado, self.btn_cerrar]:
            self.panel_botones.addWidget(btn)
        self.panel_botones.addStretch()
        self.main_layout.addLayout(self.panel_botones)

        self.panel_contenido = QVBoxLayout()
        self.main_layout.addLayout(self.panel_contenido)
        self.panel_contenido.addWidget(QLabel(f"Bienvenido, Padre ID {self.id_usuario}"))

    def mostrar_listado(self):
        self._limpiar_panel()
        self.panel_contenido.addWidget(QLabel("Mi Listado de Útiles:"))

        self.lista_mis_utiles = QListWidget()
        for item in self.lista_seleccionados:
            self.lista_mis_utiles.addItem(QListWidgetItem(item))
        self.panel_contenido.addWidget(self.lista_mis_utiles)


        self.btn_agregar = QPushButton("Agregar útil del catálogo")
        self.btn_agregar.clicked.connect(self.agregar_util)
        self.panel_contenido.addWidget(self.btn_agregar)

    def agregar_util(self):
        productos = ["Cuaderno", "Lápiz", "Borrador", "Colores", "Mochila", "Regla"]
        item, ok = QInputDialog.getItem(self, "Agregar útil", "Selecciona un útil:", productos, 0, False)
        if ok and item:
            if item not in self.lista_seleccionados:
                self.lista_seleccionados.append(item)
                self.lista_mis_utiles.addItem(QListWidgetItem(item))
            else:
                QMessageBox.information(self, "Info", "El útil ya está en tu listado.")

    def mostrar_catalogo(self):
        self._limpiar_panel()
        self.panel_contenido.addWidget(QLabel("Catálogo de Útiles:"))

        self.cursor = self.bd.conexion.cursor()
        self.cursor.execute("SELECT id_producto, nombre, stock, precio FROM Producto")
        productos = self.cursor.fetchall()

        self.lista_productos = QListWidget()
        for p in productos:
            self.lista_productos.addItem(f"{p[1]} - Stock: {p[2]} - Q{p[3]}")

        self.panel_contenido.addWidget(self.lista_productos)

        self.btn_comprar = QPushButton("Comprar útil seleccionado")
        self.btn_comprar.clicked.connect(lambda: self.comprar_util_padre(productos))
        self.panel_contenido.addWidget(self.btn_comprar)

    def comprar_util_padre(self, productos):
        item = self.lista_productos.currentItem()
        if not item:
            QMessageBox.warning(self, "Aviso", "Selecciona un producto.")
            return

        idx = self.lista_productos.currentRow()
        id_producto, nombre, stock, precio = productos[idx]

        if stock <= 0:
            QMessageBox.warning(self, "Sin stock", f"No hay stock de {nombre}.")
            return

        cantidad = 1
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            # CORREGIDO: Usar sistema de VENTAS para padres que compran
            # Crear una venta
            self.bd.ejecutar(
                "INSERT INTO Venta (id_cliente, fecha, total, id_empleado) VALUES (?, ?, ?, ?)",
                (self.id_usuario, fecha, precio, 1)  # id_empleado temporal
            )
            id_venta = self.bd.cursor.lastrowid

            # Crear detalle de venta
            self.bd.ejecutar(
                "INSERT INTO DetalleVenta (id_venta, id_producto, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?)",
                (id_venta, id_producto, cantidad, precio, cantidad * precio)
            )

            # Actualizar stock (disminuir stock para ventas)
            self.bd.ejecutar(
                "UPDATE Producto SET stock = stock - ? WHERE id_producto = ?",
                (cantidad, id_producto)
            )

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Error en la base de datos: {e}")
            return

        QMessageBox.information(self, "Compra realizada", f"Has comprado {cantidad} {nombre}(s).")
        self.mostrar_catalogo()

    def cerrar_sesion(self):
        self.close()

    def _limpiar_panel(self):
        for i in reversed(range(self.panel_contenido.count())):
            widget = self.panel_contenido.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

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
        self.txt_id_producto = QLineEdit(); self.txt_id_producto.setPlaceholderText("ID Producto")
        self.txt_cantidad = QLineEdit(); self.txt_cantidad.setPlaceholderText("Cantidad")
        self.txt_precio = QLineEdit(); self.txt_precio.setPlaceholderText("Precio unitario")
        btn_agregar = QPushButton("Agregar producto"); btn_agregar.clicked.connect(self._agregar_producto)
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
        self.txt_id_producto.clear(); self.txt_cantidad.clear(); self.txt_precio.clear()

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
            self.bd.ejecutar("INSERT INTO DetalleCompra(id_compra,id_producto,cantidad,precio) VALUES(?,?,?,?)", (id_compra, idp, cant, precio))
            self.bd.ejecutar("UPDATE Producto SET stock = stock + ? WHERE id_producto=?", (cant, idp))
        QMessageBox.information(self, "Éxito", f"Compra registrada con ID {id_compra}")
        self.productos_compra.clear(); self.txt_id_proveedor.clear(); self.lbl_productos.setText("Productos agregados:\n")

class PantallaCrearLista(QWidget):
    def __init__(self, bd):
        super().__init__()
        self.bd = bd
        layout = QVBoxLayout()

        self.txt_grado = QLineEdit(); self.txt_grado.setPlaceholderText("Grado")
        self.txt_id_cliente = QLineEdit(); self.txt_id_cliente.setPlaceholderText("ID Cliente")
        btn_crear = QPushButton("Crear lista"); btn_crear.clicked.connect(self._crear_lista)

        for w in [self.txt_grado, self.txt_id_cliente, btn_crear]:
            layout.addWidget(w)
        self.setLayout(layout)

    def _crear_lista(self):
        grado = self.txt_grado.text().strip()
        id_cliente = self.txt_id_cliente.text().strip()
        if not grado or not id_cliente:
            QMessageBox.warning(self, "Error", "Llena todos los campos")
            return
        try: id_cliente = int(id_cliente)
        except:
            QMessageBox.warning(self, "Error", "ID Cliente inválido")
            return
        self.bd.ejecutar("INSERT INTO ListaUtiles(grado,id_cliente) VALUES(?,?)", (grado, id_cliente))
        QMessageBox.information(self, "Éxito", "Lista creada correctamente")
        self.txt_grado.clear(); self.txt_id_cliente.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    tipo_usuario = VentanaTipoUsuario()
    tipo_usuario.show()

    sys.exit(app.exec())

