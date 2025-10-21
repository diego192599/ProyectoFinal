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
