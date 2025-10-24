class Proveedor:
    def __init__(self, nombre, contacto):
        self.nombre = nombre
        self.contacto = contacto

    @staticmethod
    def _conn():
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        conn.execute("""
            CREATE TABLE IF NOT EXISTS proveedores (
                id_proveedor INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                contacto TEXT
            );
        """)
        conn.commit()
        return conn

    def guardar(self):
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO proveedores (nombre, contacto) VALUES (?, ?)",
                (self.nombre, self.contacto)
            )
        print(f"Proveedor '{self.nombre}' guardado con éxito.")

    @staticmethod
    def listar():
        with Proveedor._conn() as conn:
            cur = conn.execute("SELECT * FROM proveedores")
            filas = cur.fetchall()
            if not filas:
                print("No hay proveedores registrados.")
                return
            print("\n--- LISTADO DE PROVEEDORES ---")
            for f in filas:
                print(f"ID: {f['id_proveedor']} | Nombre: {f['nombre']} | Contacto: {f['contacto']}")

    @staticmethod
    def modificar():
        ide = input("Ingrese ID del proveedor a modificar: ")
        with Proveedor._conn() as conn:
            cur = conn.execute("SELECT * FROM proveedores WHERE id_proveedor = ?", (ide,))
            fila = cur.fetchone()
            if not fila:
                print("No se encontró el proveedor.")
                return
            nombre = input(f"Nuevo nombre [{fila['nombre']}]: ") or fila['nombre']
            contacto = input(f"Nuevo contacto [{fila['contacto']}]: ") or fila['contacto']
            conn.execute("UPDATE proveedores SET nombre=?, contacto=? WHERE id_proveedor=?",
                         (nombre, contacto, ide))
        print("Proveedor actualizado con éxito.")

    @staticmethod
    def eliminar():
        ide = input("Ingrese ID del proveedor a eliminar: ")
        with Proveedor._conn() as conn:
            cur = conn.execute("DELETE FROM proveedores WHERE id_proveedor = ?", (ide,))
            if cur.rowcount == 0:
                print("No se encontró el proveedor.")
            else:
                print("Proveedor eliminado con éxito.")

class Producto:
    def __init__(self, nombre, descripcion, precio, stock, proveedor_id=None):
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio = precio
        self.stock = stock
        self.proveedor_id = proveedor_id

    @staticmethod
    def _conn():
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        conn.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                precio REAL NOT NULL,
                stock INTEGER NOT NULL,
                proveedor_id INTEGER,
                FOREIGN KEY (proveedor_id) REFERENCES proveedores(id_proveedor)
            );
        """)
        conn.commit()
        return conn

    def guardar(self):
        with self._conn() as conn:
            conn.execute("""
                INSERT INTO productos (nombre, descripcion, precio, stock, proveedor_id)
                VALUES (?, ?, ?, ?, ?)
            """, (self.nombre, self.descripcion, self.precio, self.stock, self.proveedor_id))
        print(f"Producto '{self.nombre}' guardado con éxito.")

    @staticmethod
    def listar():
        with Producto._conn() as conn:
            cur = conn.execute("""
                SELECT p.id_producto, p.nombre, p.descripcion, p.precio, p.stock,
                       pr.nombre AS proveedor
                FROM productos p
                LEFT JOIN proveedores pr ON p.proveedor_id = pr.id_proveedor
            """)
            filas = cur.fetchall()
            if not filas:
                print("No hay productos registrados.")
                return
            print("\n--- LISTADO DE PRODUCTOS ---")
            for f in filas:
                print(f"ID: {f['id_producto']} | Nombre: {f['nombre']} | Descripción: {f['descripcion']} | "
                      f"Precio: Q{f['precio']} | Stock: {f['stock']} | Proveedor: {f['proveedor']}")

    @staticmethod
    def modificar():
        ide = input("Ingrese ID del producto a modificar: ")
        with Producto._conn() as conn:
            cur = conn.execute("SELECT * FROM productos WHERE id_producto = ?", (ide,))
            fila = cur.fetchone()
            if not fila:
                print("No se encontró el producto.")
                return
            nombre = input(f"Nuevo nombre [{fila['nombre']}]: ") or fila['nombre']
            descripcion = input(f"Nueva descripción [{fila['descripcion']}]: ") or fila['descripcion']
            precio = input(f"Nuevo precio [{fila['precio']}]: ") or fila['precio']
            stock = input(f"Nuevo stock [{fila['stock']}]: ") or fila['stock']
            conn.execute("""
                UPDATE productos
                SET nombre=?, descripcion=?, precio=?, stock=?
                WHERE id_producto=?
            """, (nombre, descripcion, precio, stock, ide))
        print("Producto actualizado con éxito.")

    @staticmethod
    def eliminar():
        ide = input("Ingrese ID del producto a eliminar: ")
        with Producto._conn() as conn:
            cur = conn.execute("DELETE FROM productos WHERE id_producto = ?", (ide,))
            if cur.rowcount == 0:
                print("No se encontró el producto.")
            else:
                print("Producto eliminado con éxito.")

class Empleado:
    def __init__(self, nombre, puesto, salario):
        self.nombre = nombre
        self.puesto = puesto
        self.salario = salario

    @staticmethod
    def _conn():
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        conn.execute("""
            CREATE TABLE IF NOT EXISTS empleados (
                id_empleado INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                puesto TEXT,
                salario REAL
            );
        """)
        conn.commit()
        return conn

    def guardar(self):
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO empleados (nombre, puesto, salario) VALUES (?, ?, ?)",
                (self.nombre, self.puesto, self.salario)
            )
        print(f"Empleado '{self.nombre}' guardado con éxito.")

    @staticmethod
    def listar():
        with Empleado._conn() as conn:
            cur = conn.execute("SELECT * FROM empleados")
            filas = cur.fetchall()
            if not filas:
                print("No hay empleados registrados.")
                return
            print("\n--- LISTADO DE EMPLEADOS ---")
            for f in filas:
                print(f"ID: {f['id_empleado']} | Nombre: {f['nombre']} | Puesto: {f['puesto']} | Salario: {f['salario']}")

    @staticmethod
    def modificar():
        ide = input("Ingrese ID del empleado a modificar: ")
        with Empleado._conn() as conn:
            cur = conn.execute("SELECT * FROM empleados WHERE id_empleado = ?", (ide,))
            fila = cur.fetchone()
            if not fila:
                print("No se encontró el empleado.")
                return
            nombre = input(f"Nuevo nombre [{fila['nombre']}]: ") or fila['nombre']
            puesto = input(f"Nuevo puesto [{fila['puesto']}]: ") or fila['puesto']
            salario = input(f"Nuevo salario [{fila['salario']}]: ") or fila['salario']
            conn.execute("UPDATE empleados SET nombre=?, puesto=?, salario=? WHERE id_empleado=?",
                         (nombre, puesto, salario, ide))
        print("Empleado actualizado con éxito.")

    @staticmethod
    def eliminar():
        ide = input("Ingrese ID del empleado a eliminar: ")
        with Empleado._conn() as conn:
            cur = conn.execute("DELETE FROM empleados WHERE id_empleado = ?", (ide,))
            if cur.rowcount == 0:
                print("No se encontró el empleado.")
            else:
                print("Empleado eliminado con éxito.")


class Usuario:
    def __init__(self, nombre, usuario, contraseña):
        self.nombre = nombre
        self.usuario = usuario
        self.contraseña = contraseña

    @staticmethod
    def _conn():
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        conn.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                usuario TEXT NOT NULL UNIQUE,
                contraseña TEXT NOT NULL
            );
        """)
        conn.commit()
        return conn

    def guardar(self):
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO usuarios (nombre, usuario, contraseña) VALUES (?, ?, ?)",
                (self.nombre, self.usuario, self.contraseña)
            )
        print(f"Usuario '{self.usuario}' registrado con éxito.")

    @staticmethod
    def listar():
        with Usuario._conn() as conn:
            cur = conn.execute("SELECT * FROM usuarios")
            filas = cur.fetchall()
            if not filas:
                print("No hay usuarios registrados.")
                return
            print("\n--- LISTADO DE USUARIOS ---")
            for f in filas:
                print(f"ID: {f['id_usuario']} | Nombre: {f['nombre']} | Usuario: {f['usuario']}")

    @staticmethod
    def modificar():
        ide = input("Ingrese ID del usuario a modificar: ")
        with Usuario._conn() as conn:
            cur = conn.execute("SELECT * FROM usuarios WHERE id_usuario = ?", (ide,))
            fila = cur.fetchone()
            if not fila:
                print("No se encontró el usuario.")
                return
            nombre = input(f"Nuevo nombre [{fila['nombre']}]: ") or fila['nombre']
            usuario = input(f"Nuevo usuario [{fila['usuario']}]: ") or fila['usuario']
            contraseña = input(f"Nueva contraseña [{fila['contraseña']}]: ") or fila['contraseña']
            conn.execute("UPDATE usuarios SET nombre=?, usuario=?, contraseña=? WHERE id_usuario=?",
                         (nombre, usuario, contraseña, ide))
        print("Usuario actualizado con éxito.")

    @staticmethod
    def eliminar():
        ide = input("Ingrese ID del usuario a eliminar: ")
        with Usuario._conn() as conn:
            cur = conn.execute("DELETE FROM usuarios WHERE id_usuario = ?", (ide,))
            if cur.rowcount == 0:
                print("No se encontró el usuario.")
            else:
                print("Usuario eliminado con éxito.")

class Compra:
    def __init__(self, id_proveedor, fecha, total):
        self.id_proveedor = id_proveedor
        self.fecha = fecha
        self.total = total

    @staticmethod
    def _conn():
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        conn.execute("""
            CREATE TABLE IF NOT EXISTS compras (
                id_compra INTEGER PRIMARY KEY AUTOINCREMENT,
                id_proveedor INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                total REAL NOT NULL
            );
        """)
        conn.commit()
        return conn

    def guardar(self):
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO compras (id_proveedor, fecha, total) VALUES (?, ?, ?)",
                (self.id_proveedor, self.fecha, self.total)
            )
        print(f"Compra registrada con éxito (Proveedor ID: {self.id_proveedor}).")

    @staticmethod
    def listar():
        with Compra._conn() as conn:
            cur = conn.execute("SELECT * FROM compras")
            filas = cur.fetchall()
            if not filas:
                print("No hay compras registradas.")
                return
            print("\n--- LISTADO DE COMPRAS ---")
            for f in filas:
                print(f"ID: {f['id_compra']} | Proveedor: {f['id_proveedor']} | Fecha: {f['fecha']} | Total: {f['total']}")

    @staticmethod
    def eliminar():
        ide = input("Ingrese ID de la compra a eliminar: ")
        with Compra._conn() as conn:
            cur = conn.execute("DELETE FROM compras WHERE id_compra = ?", (ide,))
            if cur.rowcount == 0:
                print("No se encontró la compra.")
            else:
                print("Compra eliminada con éxito.")


class DetalleCompra:
    def __init__(self, id_compra, id_producto, cantidad, precio_unitario):
        self.id_compra = id_compra
        self.id_producto = id_producto
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.subtotal = cantidad * precio_unitario

    @staticmethod
    def _conn():
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        conn.execute("""
            CREATE TABLE IF NOT EXISTS detalle_compra (
                id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
                id_compra INTEGER NOT NULL,
                id_producto INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                subtotal REAL NOT NULL
            );
        """)
        conn.commit()
        return conn

    def guardar(self):
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO detalle_compra (id_compra, id_producto, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?)",
                (self.id_compra, self.id_producto, self.cantidad, self.precio_unitario, self.subtotal)
            )
        print(f"Detalle agregado a compra #{self.id_compra}. Subtotal: Q{self.subtotal}")

class Venta:
    def __init__(self, id_empleado, fecha, total):
        self.id_empleado = id_empleado
        self.fecha = fecha
        self.total = total

    @staticmethod
    def _conn():
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
                id_empleado INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                total REAL NOT NULL
            );
        """)
        conn.commit()
        return conn

    def guardar(self):
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO ventas (id_empleado, fecha, total) VALUES (?, ?, ?)",
                (self.id_empleado, self.fecha, self.total)
            )
        print(f"Venta registrada con éxito (Empleado ID: {self.id_empleado}).")

    @staticmethod
    def listar():
        with Venta._conn() as conn:
            cur = conn.execute("SELECT * FROM ventas")
            filas = cur.fetchall()
            if not filas:
                print("No hay ventas registradas.")
                return
            print("\n--- LISTADO DE VENTAS ---")
            for f in filas:
                print(f"ID: {f['id_venta']} | Empleado: {f['id_empleado']} | Fecha: {f['fecha']} | Total: {f['total']}")

    @staticmethod
    def eliminar():
        ide = input("Ingrese ID de la venta a eliminar: ")
        with Venta._conn() as conn:
            cur = conn.execute("DELETE FROM ventas WHERE id_venta = ?", (ide,))
            if cur.rowcount == 0:
                print("No se encontró la venta.")
            else:
                print("Venta eliminada con éxito.")


class DetalleVenta:
    def __init__(self, id_venta, id_producto, cantidad, precio_unitario):
        self.id_venta = id_venta
        self.id_producto = id_producto
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.subtotal = cantidad * precio_unitario

    @staticmethod
    def _conn():
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        conn.execute("""
            CREATE TABLE IF NOT EXISTS detalle_venta (
                id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
                id_venta INTEGER NOT NULL,
                id_producto INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                subtotal REAL NOT NULL
            );
        """)
        conn.commit()
        return conn

    def guardar(self):
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?)",
                (self.id_venta, self.id_producto, self.cantidad, self.precio_unitario, self.subtotal)
            )
        print(f"Detalle agregado a venta #{self.id_venta}. Subtotal: Q{self.subtotal}")



