import sqlite3
from datetime import datetime

DB_NAME = "sistema.db"

class ConexionBD:
    def __init__(self, archivo):
        self.conexion = sqlite3.connect(archivo)
        self.cursor = self.conexion.cursor()
        self.crear_tablas()

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
            contraseña TEXT NOT NULL
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
    def __init__(self, nombre, usuario, contrasena):
        self.nombre = nombre
        self.usuario = usuario
        self.contrasena = contrasena

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

    def agregar(self):
        nombre = input("Nombre: ")
        usuario = input("Usuario: ")
        contrasena = input("Contraseña: ")
        self.bd.ejecutar("INSERT INTO Usuario(nombre,usuario,contraseña) VALUES(?,?,?)",
                         (nombre,usuario,contrasena))
        print("Usuario registrado con éxito.")

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

