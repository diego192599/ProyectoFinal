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