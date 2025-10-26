import sqlite3
from datetime import datetime

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
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Venta(
            id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            id_cliente INTEGER,
            id_empleado INTEGER,
            total REAL,
            FOREIGN KEY(id_cliente) REFERENCES Cliente(id_cliente),
            FOREIGN KEY(id_empleado) REFERENCES Empleado(id_empleado)
        )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS DetalleVenta(
            id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
            id_venta INTEGER,
            codigo_producto INTEGER,
            cantidad INTEGER,
            precio REAL,
            subtotal REAL,
            FOREIGN KEY(id_venta) REFERENCES Venta(id_venta),
            FOREIGN KEY(codigo_producto) REFERENCES Producto(codigo_producto)
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
        nombre = input("Nombre: ")
        precio = float(input("Precio: "))
        stock = int(input("Stock inicial: "))
        limite_stock = input("Límite stock (vacío sin límite): ")
        limite_stock = int(limite_stock) if limite_stock else None
        imagen = input("Ruta imagen: ")
        self.bd.ejecutar("INSERT INTO Producto(id_categoria,nombre,precio,stock,limite_stock,imagen) VALUES(?,?,?,?,?,?)",
                         (id_categoria,nombre,precio,stock,limite_stock,imagen))
        print("Producto agregado")

    def mostrar(self):
        res = self.bd.consultar("SELECT * FROM Producto")
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
        salario = float(input("Salario base: "))
        self.bd.ejecutar("INSERT INTO Empleado(nombre,telefono,correo,salario) VALUES(?,?,?,?)",
                         (nombre,telefono,correo,salario))
        print("Empleado agregado")

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
        print("Proveedor agregado")

    def mostrar(self):
        res = self.bd.consultar("SELECT * FROM Proveedor")
        for r in res:
            print(r)

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