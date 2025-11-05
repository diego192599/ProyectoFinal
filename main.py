import sys
import os
import sys
import sys
import sqlite3
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit,
    QVBoxLayout, QMessageBox, QInputDialog, QHBoxLayout,
    QStackedLayout, QListWidget, QListWidgetItem, QFileDialog,
    QSpinBox, QScrollArea, QTableWidget, QTableWidgetItem, QComboBox,
    QFrame, QGridLayout, QGroupBox, QFormLayout, QCheckBox
)
from PySide6.QtGui import QFont, QPixmap, QColor, QIcon
from PySide6.QtCore import Qt, QSize
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


class ManejadorRecursos:
    @staticmethod
    def obtener_imagen_producto(nombre_imagen, ancho=100, alto=100):
        emoji_map = {
            "cuaderno": "📒",
            "lapiz": "✏️",
            "mochila": "🎒",
            "colores": "🖍️",
            "regla": "📏",
            "borrador": "🧼",
            "tijeras": "✂️",
            "pegamento": "🧴",
            "compas": "⚙️",
            "calculadora": "🧮",
            "diccionario": "📚",
            "transportador": "📐",
            "tajador": "✏️",
            "marcador": "🖊️",
            "crayones": "🖍️",
            "acuerdo": "📋",
            "folder": "📁",
            "papel": "📄",
            "escuadra": "📐",
            "cartulina": "📄",
            "plasticola": "🧴",
            "tempera": "🎨",
            "pincel": "🖌️",
            "block": "📒"
        }

        nombre_lower = nombre_imagen.lower()
        for key, emoji in emoji_map.items():
            if key in nombre_lower:
                return emoji

        return "📦"

    @staticmethod
    def obtener_color_categoria(categoria):
        colores = {
            "útiles escolares": "#FFE4E6",
            "escritura": "#F0FDF4",
            "papelería": "#EFF6FF",
            "mochilas": "#FEFCE8",
            "arte": "#FDF2F8",
            "geometría": "#F8FAFC",
            "tecnología": "#EFF6FF",
            "matemáticas": "#FEF7CD",
            "ciencias": "#E0F2FE",
            "literatura": "#FCE7F3"
        }
        return colores.get(categoria.lower() if categoria else "", "#F8FAFC")

    @staticmethod
    def obtener_icono_categoria(categoria):
        iconos = {
            "útiles escolares": "📚",
            "escritura": "✏️",
            "papelería": "📄",
            "mochilas": "🎒",
            "arte": "🎨",
            "geometría": "📐",
            "tecnología": "💻",
            "matemáticas": "🧮",
            "ciencias": "🔬",
            "literatura": "📖"
        }
        return iconos.get(categoria.lower() if categoria else "", "📦")

class VentanaInicio(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Librería Escolar ABC")
        self.resize(1200, 800)
        self.setStyleSheet("background-color: #F5F5F5;")
        self.bd = ConexionBD(DB_FILE)
        self._construir_ui()

    def _construir_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)


        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet("background-color: #1E40AF; color: white;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 0, 30, 0)


        logo_layout = QHBoxLayout()
        logo_label = QLabel("📚")
        logo_label.setStyleSheet("font-size: 32px;")
        titulo = QLabel("Librería Escolar ABC")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold; color: white; margin-left: 10px;")
        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(titulo)


        nav_layout = QHBoxLayout()
        nav_items = [
            ("Inicio", self._ir_a_inicio),
            ("Productos", self._ir_a_productos),
            ("Listas", self._ir_a_listas),
            ("Promociones", self._ir_a_promociones),
            ("Contacto", self._ir_a_contacto)
        ]

        for item_text, item_func in nav_items:
            btn = QPushButton(item_text)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: white;
                    border: none;
                    padding: 10px 15px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1E3A8A;
                    border-radius: 5px;
                }
            """)
            btn.clicked.connect(item_func)
            nav_layout.addWidget(btn)


        user_layout = QHBoxLayout()
        btn_login = QPushButton("Iniciar Sesión")
        btn_login.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-weight: bold;
                margin-left: 10px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)
        btn_login.clicked.connect(self._mostrar_login)

        header_layout.addLayout(logo_layout)
        header_layout.addStretch()
        header_layout.addLayout(nav_layout)
        header_layout.addStretch()
        header_layout.addWidget(btn_login)


        hero = QWidget()
        hero.setFixedHeight(400)
        hero.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1E40AF, stop:1 #3B82F6);
            border-bottom-left-radius: 20px;
            border-bottom-right-radius: 20px;
        """)
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(100, 60, 100, 60)

        hero_title = QLabel("Encuentra todo lo que\nnecesitas para el colegio")
        hero_title.setStyleSheet("font-size: 48px; font-weight: bold; color: white; line-height: 1.2;")
        hero_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        hero_subtitle = QLabel("Útiles escolares de calidad para todos los grados")
        hero_subtitle.setStyleSheet("font-size: 20px; color: #E0F2FE; margin-top: 20px;")
        hero_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        hero_btn = QPushButton("Ver Catálogo Completo →")
        hero_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #1E40AF;
                border: none;
                border-radius: 10px;
                padding: 15px 40px;
                font-size: 18px;
                font-weight: bold;
                margin-top: 30px;
            }
            QPushButton:hover {
                background-color: #E0F2FE;
            }
        """)
        hero_btn.setFixedSize(250, 50)
        hero_btn.clicked.connect(self._ir_a_catalogo)

        hero_layout.addWidget(hero_title)
        hero_layout.addWidget(hero_subtitle)
        hero_layout.addWidget(hero_btn, alignment=Qt.AlignmentFlag.AlignCenter)


        features = self._crear_seccion_caracteristicas()


        productos = self._crear_seccion_productos()


        listas_utiles = self._crear_seccion_listas()


        footer = self._crear_footer()


        main_layout.addWidget(header)
        main_layout.addWidget(hero)
        main_layout.addWidget(features)
        main_layout.addWidget(productos)
        main_layout.addWidget(listas_utiles)
        main_layout.addWidget(footer)

        self.setLayout(main_layout)

    def _crear_seccion_caracteristicas(self):
        features = QWidget()
        features_layout = QVBoxLayout(features)
        features_layout.setContentsMargins(50, 50, 50, 50)

        features_title = QLabel("¿Por qué elegirnos?")
        features_title.setStyleSheet("font-size: 36px; font-weight: bold; color: #1E293B; margin-bottom: 40px;")
        features_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        features_grid = QGridLayout()
        features_data = [
            ("🚚", "Entrega Rápida", "Recibe tus productos en 24-48 horas", self._ir_a_envios),
            ("💰", "Precios Bajos", "Los mejores precios del mercado", self._ir_a_ofertas),
            ("⭐", "Calidad Garantizada", "Productos de primera calidad", self._ir_a_calidad),
            ("📦", "Gran Inventario", "Todo lo que necesitas en un solo lugar", self._ir_a_inventario)
        ]

        for i, (icono, titulo, desc, funcion) in enumerate(features_data):
            card = QWidget()
            card.setFixedSize(250, 180)
            card.setStyleSheet("""
                QWidget {
                    background-color: white;
                    border-radius: 15px;
                    padding: 20px;
                    border: 2px solid #E2E8F0;
                }
                QWidget:hover {
                    border: 2px solid #3B82F6;
                    cursor: pointer;
                }
            """)
            card_layout = QVBoxLayout(card)

            icon = QLabel(icono)
            icon.setStyleSheet("font-size: 40px;")
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

            title = QLabel(titulo)
            title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1E293B; margin-top: 10px;")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)

            description = QLabel(desc)
            description.setStyleSheet("font-size: 14px; color: #64748B; margin-top: 10px; text-align: center;")
            description.setWordWrap(True)
            description.setAlignment(Qt.AlignmentFlag.AlignCenter)

            card_layout.addWidget(icon)
            card_layout.addWidget(title)
            card_layout.addWidget(description)


            card.mousePressEvent = lambda event, func=funcion: func()
            features_grid.addWidget(card, i // 2, i % 2)

        features_layout.addWidget(features_title)
        features_layout.addLayout(features_grid)
        features_layout.setAlignment(features_grid, Qt.AlignmentFlag.AlignCenter)

        return features

    def _crear_seccion_productos(self):
        productos = QWidget()
        productos_layout = QVBoxLayout(productos)
        productos_layout.setContentsMargins(50, 50, 50, 50)

        productos_title = QLabel("Productos Destacados")
        productos_title.setStyleSheet("font-size: 36px; font-weight: bold; color: #1E293B; margin-bottom: 30px;")
        productos_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        productos_grid = QHBoxLayout()


        productos_data = [
            ("Cuadernos", "útiles escolares", "Desde Q25.00", self._ir_a_cuadernos),
            ("Lápices", "escritura", "Desde Q15.00", self._ir_a_lapices),
            ("Mochilas", "mochilas", "Desde Q150.00", self._ir_a_mochilas),
            ("Colores", "arte", "Desde Q45.00", self._ir_a_colores)
        ]

        for titulo, categoria, precio, funcion in productos_data:
            card = QWidget()
            card.setFixedSize(200, 200)

            color_fondo = ManejadorRecursos.obtener_color_categoria(categoria)
            emoji = ManejadorRecursos.obtener_icono_categoria(categoria)

            card.setStyleSheet(f"""
                QWidget {{
                    background-color: {color_fondo};
                    border-radius: 15px;
                    padding: 20px;
                    border: 2px solid #E2E8F0;
                }}
                QWidget:hover {{
                    border: 2px solid #3B82F6;
                    cursor: pointer;
                }}
            """)

            card_layout = QVBoxLayout(card)

            icon = QLabel(emoji)  # Usar el emoji del manejador
            icon.setStyleSheet("font-size: 50px;")
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

            title = QLabel(titulo)
            title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1E293B; margin-top: 15px;")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)

            price = QLabel(precio)
            price.setStyleSheet("font-size: 16px; color: #64748B; margin-top: 10px;")
            price.setAlignment(Qt.AlignmentFlag.AlignCenter)

            card_layout.addWidget(icon)
            card_layout.addWidget(title)
            card_layout.addWidget(price)

            card.mousePressEvent = lambda event, func=funcion: func()
            productos_grid.addWidget(card)

        productos_layout.addWidget(productos_title)
        productos_layout.addLayout(productos_grid)
        productos_layout.setAlignment(productos_grid, Qt.AlignmentFlag.AlignCenter)

        return productos

    def _crear_seccion_listas(self):
        listas = QWidget()
        listas.setStyleSheet("background-color: #F8FAFC;")
        listas_layout = QVBoxLayout(listas)
        listas_layout.setContentsMargins(50, 50, 50, 50)

        listas_title = QLabel("Listas de Útiles por Grado")
        listas_title.setStyleSheet("font-size: 36px; font-weight: bold; color: #1E293B; margin-bottom: 30px;")
        listas_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        tabla = QTableWidget()
        tabla.setColumnCount(4)
        tabla.setRowCount(5)
        tabla.setHorizontalHeaderLabels(["Grado", "Productos Incluidos", "Precio Total", "Acción"])


        datos_listas = [
            ("1°-3° Primaria", "Cuaderno, Lápices, Borradores", "Q 185.00", "Ver Lista"),
            ("4°-6° Primaria", "Cuadernos, Regla, Colores", "Q 220.00", "Ver Lista"),
            ("1°-3° Secundaria", "Cuadernos, Calculadora, Compás", "Q 285.00", "Ver Lista"),
            ("4°-6° Secundaria", "Cuadernos, Diccionario, Geometría", "Q 320.00", "Ver Lista"),
            ("Bachillerato", "Material especializado", "Q 350.00", "Ver Lista")
        ]

        for fila, (grado, productos, precio, accion) in enumerate(datos_listas):
            tabla.setItem(fila, 0, QTableWidgetItem(grado))
            tabla.setItem(fila, 1, QTableWidgetItem(productos))
            tabla.setItem(fila, 2, QTableWidgetItem(precio))


            btn_ver = QPushButton(accion)
            btn_ver.setStyleSheet("""
                QPushButton {
                    background-color: #3B82F6;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 5px 10px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #2563EB;
                }
            """)
            btn_ver.clicked.connect(lambda checked, grad=grado: self._ver_lista_grado(grad))
            tabla.setCellWidget(fila, 3, btn_ver)


        tabla.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                gridline-color: #E2E8F0;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #E2E8F0;
            }
            QHeaderView::section {
                background-color: #1E40AF;
                color: white;
                font-weight: bold;
                padding: 12px;
                border: none;
            }
        """)
        tabla.horizontalHeader().setStretchLastSection(True)
        tabla.verticalHeader().setVisible(False)
        tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        listas_layout.addWidget(listas_title)
        listas_layout.addWidget(tabla)

        return listas

    def _crear_footer(self):
        footer = QWidget()
        footer.setFixedHeight(250)
        footer.setStyleSheet("background-color: #1E293B; color: white;")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(100, 40, 100, 40)


        info_col = QVBoxLayout()
        info_title = QLabel("Librería Escolar ABC")
        info_title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 20px;")

        info_text = QLabel("Tu tienda de confianza para\nútiles escolares de calidad")
        info_text.setStyleSheet("color: #94A3B8; line-height: 1.5;")

        info_col.addWidget(info_title)
        info_col.addWidget(info_text)


        links_col = QVBoxLayout()
        links_title = QLabel("Enlaces Rápidos")
        links_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 15px;")

        links_data = [
            ("Inicio", self._ir_a_inicio),
            ("Productos", self._ir_a_productos),
            ("Listas", self._ir_a_listas),
            ("Promociones", self._ir_a_promociones),
            ("Contacto", self._ir_a_contacto)
        ]

        links_col.addWidget(links_title)
        for link_text, link_func in links_data:
            lbl = QLabel(link_text)
            lbl.setStyleSheet("color: #94A3B8; margin: 5px 0;")
            lbl.setCursor(Qt.CursorShape.PointingHandCursor)
            lbl.mousePressEvent = lambda event, func=link_func: func()
            links_col.addWidget(lbl)


        contact_col = QVBoxLayout()
        contact_title = QLabel("Contacto")
        contact_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 15px;")

        contact_info = [
            "📞 (502) 1234-5678",
            "📧 info@libreriaabc.com",
            "📍 Ciudad de Guatemala"
        ]

        contact_col.addWidget(contact_title)
        for info in contact_info:
            lbl = QLabel(info)
            lbl.setStyleSheet("color: #94A3B8; margin: 5px 0;")
            contact_col.addWidget(lbl)

        footer_layout.addLayout(info_col)
        footer_layout.addStretch()
        footer_layout.addLayout(links_col)
        footer_layout.addStretch()
        footer_layout.addLayout(contact_col)

        return footer


    def _ir_a_inicio(self):

        QMessageBox.information(self, "Inicio", "Ya te encuentras en la página de inicio")

    def _ir_a_productos(self):
        self._mostrar_login()

    def _ir_a_listas(self):
        QMessageBox.information(self, "Listas de Útiles", "Aquí verías las listas completas por grado")

    def _ir_a_promociones(self):
        QMessageBox.information(self, "Promociones", "Promociones especiales y descuentos")

    def _ir_a_contacto(self):
        QMessageBox.information(self, "Contacto",
                                "Librería Escolar ABC\n"
                                "Tel: (502) 1234-5678\n"
                                "Email: info@libreriaabc.com\n"
                                "Ciudad de Guatemala")

    def _ir_a_catalogo(self):
        self._mostrar_login()

    def _ir_a_cuadernos(self):
        QMessageBox.information(self, "Cuadernos", "Catálogo de cuadernos")

    def _ir_a_lapices(self):
        QMessageBox.information(self, "Lápices", "Catálogo de lápices")

    def _ir_a_mochilas(self):
        QMessageBox.information(self, "Mochilas", "Catálogo de mochilas")

    def _ir_a_colores(self):
        QMessageBox.information(self, "Colores", "Catálogo de colores")

    def _ir_a_envios(self):
        QMessageBox.information(self, "Envíos", "Información sobre envíos y entregas")

    def _ir_a_ofertas(self):
        QMessageBox.information(self, "Ofertas", "Las mejores ofertas y precios")

    def _ir_a_calidad(self):
        QMessageBox.information(self, "Calidad", "Nuestros estándares de calidad")

    def _ir_a_inventario(self):
        QMessageBox.information(self, "Inventario", "Nuestro amplio inventario")

    def _ver_lista_grado(self, grado):
        QMessageBox.information(self, f"Lista {grado}", f"Lista completa de útiles para {grado}")

    def _mostrar_login(self):

        self.hide()
        self.login_window = VentanaTipoUsuario()
        self.login_window.show()
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
        self.detalles = []

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
        self.showMaximized()  # Pantalla completa
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
                border-radius: 15px;
                padding: 15px 25px;
                font-size: 18px;
                font-weight: bold;
                min-width: 250px;
                min-height: 60px;
                margin: 10px;
            }
            QPushButton:hover { 
                background-color: #0056b3; 
            }
            QLabel {
                color: #1E40AF;
            }
        """)

    def _construir_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        container = QWidget()
        container.setFixedSize(600, 500)
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.setSpacing(30)

        # Logo y título
        logo_layout = QHBoxLayout()
        logo_label = QLabel("📚")
        logo_label.setStyleSheet("font-size: 48px;")
        titulo_app = QLabel("Librería Escolar ABC")
        titulo_app.setStyleSheet("font-size: 28px; font-weight: bold; color: #1E40AF; margin-left: 15px;")

        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(titulo_app)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Título principal
        titulo = QLabel("Bienvenido a Librería ABC")
        titulo.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("color: #1E293B; margin-bottom: 20px;")

        # Subtítulo
        subtitulo = QLabel("Selecciona tu tipo de usuario para continuar")
        subtitulo.setFont(QFont("Segoe UI", 14))
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitulo.setStyleSheet("color: #64748B; margin-bottom: 40px;")

        # Botones de selección
        btn_padres = QPushButton("👨‍👩‍👧‍👦 Padres de Familia")
        btn_padres.clicked.connect(self._abrir_padres)

        btn_admin = QPushButton("👨‍💼 Administrador / Empleado")
        btn_admin.clicked.connect(self._abrir_admin)

        # Agregar elementos al contenedor
        container_layout.addLayout(logo_layout)
        container_layout.addWidget(titulo)
        container_layout.addWidget(subtitulo)
        container_layout.addWidget(btn_padres)
        container_layout.addWidget(btn_admin)

        # Agregar contenedor al layout principal
        main_layout.addWidget(container)
        self.setLayout(main_layout)

    def _abrir_padres(self):
        self.hide()
        self.padres = VentanaLoginPadres()
        self.padres.showMaximized()

    def _abrir_admin(self):
        self.hide()
        self.admin = VentanaLoginAdmin()
        self.admin.showMaximized()


class VentanaLoginAdmin(QWidget):
    def __init__(self):
        super().__init__()
        self.bd = ConexionBD(DB_FILE)
        self.setWindowTitle("Iniciar Sesión - Admin/Empleado")
        self.showMaximized()  # Pantalla completa
        self._aplicar_estilos_login()
        self._construir_ui_login()

    def _aplicar_estilos_login(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #F8FAFC;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLineEdit {
                background-color: white;
                border: 2px solid #E2E8F0;
                border-radius: 8px;
                padding: 12px 15px;
                font-size: 14px;
                margin: 8px 0px;
            }
            QLineEdit:focus {
                border-color: #3B82F6;
            }
            QPushButton {
                background-color: #1E40AF;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 25px;
                font-size: 16px;
                font-weight: bold;
                margin: 10px 0px;
            }
            QPushButton:hover {
                background-color: #1E3A8A;
            }
            QPushButton#secundario {
                background-color: transparent;
                color: #1E40AF;
                border: 2px solid #1E40AF;
            }
            QPushButton#secundario:hover {
                background-color: #1E40AF;
                color: white;
            }
            QLabel#titulo {
                font-size: 28px;
                font-weight: bold;
                color: #1E293B;
            }
            QLabel#subtitulo {
                font-size: 16px;
                color: #64748B;
            }
        """)

    def _construir_ui_login(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(0)


        header_layout = QHBoxLayout()
        logo = QLabel("📚")
        logo.setStyleSheet("font-size: 32px;")
        titulo_app = QLabel("Librería ABC")
        titulo_app.setStyleSheet("font-size: 20px; font-weight: bold; color: #1E40AF; margin-left: 10px;")

        header_layout.addWidget(logo)
        header_layout.addWidget(titulo_app)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        layout.addSpacing(30)


        titulo = QLabel("Iniciar Sesión")
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitulo = QLabel("Administradores y Empleados")
        subtitulo.setObjectName("subtitulo")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)
        layout.addSpacing(30)


        self.txt_usuario = QLineEdit()
        self.txt_usuario.setPlaceholderText("Usuario")

        self.txt_contra = QLineEdit()
        self.txt_contra.setPlaceholderText("Contraseña")
        self.txt_contra.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addWidget(self.txt_usuario)
        layout.addWidget(self.txt_contra)


        btn_ingresar = QPushButton("Ingresar")
        btn_ingresar.clicked.connect(self._login)
        layout.addWidget(btn_ingresar)

        layout.addSpacing(20)


        btn_registrar = QPushButton("Crear cuenta nueva")
        btn_registrar.setObjectName("secundario")
        btn_registrar.clicked.connect(self._abrir_registro_moderno)
        layout.addWidget(btn_registrar)

        layout.addSpacing(30)


        btn_volver = QPushButton("← Volver al Inicio")
        btn_volver.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #64748B;
                border: none;
                padding: 8px 15px;
            }
            QPushButton:hover {
                color: #374151;
                text-decoration: underline;
            }
        """)
        btn_volver.clicked.connect(self._volver)
        layout.addWidget(btn_volver)

        layout.addStretch()

        self.setLayout(layout)

    def _abrir_registro_moderno(self):

        self.hide()
        self.registro = VentanaRegistroModerno(tipo_usuario="admin", bd=self.bd)
        self.registro.show()

    def _login(self):
        usuario = self.txt_usuario.text().strip()
        contra = self.txt_contra.text().strip()
        filas = self.bd.consultar(
            "SELECT * FROM Usuario WHERE usuario=? AND contrasena=? AND tipo='admin'",
            (usuario, contra)
        )
        if filas:
            QMessageBox.information(self, "Bienvenido", f"¡Hola {filas[0][1]}!")
            self.hide()
            self.admin_principal = VentanaAdmin(self.bd)
            self.admin_principal.show()
        else:
            QMessageBox.critical(self, "Error", "Usuario o contraseña incorrectos.")

    def _volver(self):
        self.close()
        self.tipo_usuario = VentanaTipoUsuario()
        self.tipo_usuario.show()

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
        self.registro = VentanaRegistroModerno(tipo_usuario="padre", bd=self.bd)  # Usar el nuevo registro
        self.registro.show()

    def _volver(self):
        self.close()
        self.tipo_usuario = VentanaTipoUsuario()
        self.tipo_usuario.showMaximized()


class VentanaLoginPadres(QWidget):
    def __init__(self):
        super().__init__()
        self.bd = ConexionBD(DB_FILE)
        self.setWindowTitle("Iniciar Sesión - Padres")
        self.showMaximized()  # Pantalla completa
        self._aplicar_estilos_login()
        self._construir_ui_login()

    def _aplicar_estilos_login(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #F8FAFC;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLineEdit {
                background-color: white;
                border: 2px solid #E2E8F0;
                border-radius: 8px;
                padding: 12px 15px;
                font-size: 14px;
                margin: 8px 0px;
            }
            QLineEdit:focus {
                border-color: #3B82F6;
            }
            QPushButton {
                background-color: #1E40AF;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 25px;
                font-size: 16px;
                font-weight: bold;
                margin: 10px 0px;
            }
            QPushButton:hover {
                background-color: #1E3A8A;
            }
            QPushButton#secundario {
                background-color: transparent;
                color: #1E40AF;
                border: 2px solid #1E40AF;
            }
            QPushButton#secundario:hover {
                background-color: #1E40AF;
                color: white;
            }
            QLabel#titulo {
                font-size: 28px;
                font-weight: bold;
                color: #1E293B;
            }
            QLabel#subtitulo {
                font-size: 16px;
                color: #64748B;
            }
        """)

    def _construir_ui_login(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(0)

        # Header
        header_layout = QHBoxLayout()
        logo = QLabel("📚")
        logo.setStyleSheet("font-size: 32px;")
        titulo_app = QLabel("Librería ABC")
        titulo_app.setStyleSheet("font-size: 20px; font-weight: bold; color: #1E40AF; margin-left: 10px;")

        header_layout.addWidget(logo)
        header_layout.addWidget(titulo_app)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        layout.addSpacing(30)

        # Título
        titulo = QLabel("Iniciar Sesión")
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitulo = QLabel("Padres de Familia")
        subtitulo.setObjectName("subtitulo")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)
        layout.addSpacing(30)


        self.txt_usuario = QLineEdit()
        self.txt_usuario.setPlaceholderText("Usuario")

        self.txt_contra = QLineEdit()
        self.txt_contra.setPlaceholderText("Contraseña")
        self.txt_contra.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addWidget(self.txt_usuario)
        layout.addWidget(self.txt_contra)


        btn_ingresar = QPushButton("Ingresar")
        btn_ingresar.clicked.connect(self._login)
        layout.addWidget(btn_ingresar)

        layout.addSpacing(20)


        btn_registrar = QPushButton("Crear cuenta nueva")
        btn_registrar.setObjectName("secundario")
        btn_registrar.clicked.connect(self._abrir_registro_moderno)
        layout.addWidget(btn_registrar)

        layout.addSpacing(30)


        btn_volver = QPushButton("← Volver al Inicio")
        btn_volver.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #64748B;
                border: none;
                padding: 8px 15px;
            }
            QPushButton:hover {
                color: #374151;
                text-decoration: underline;
            }
        """)
        btn_volver.clicked.connect(self._volver)
        layout.addWidget(btn_volver)

        layout.addStretch()

        self.setLayout(layout)

    def _abrir_registro_moderno(self):
        self.hide()
        self.registro = VentanaRegistroModerno(tipo_usuario="padre", bd=self.bd)
        self.registro.show()

    def _login(self):
        usuario = self.txt_usuario.text().strip()
        contra = self.txt_contra.text().strip()
        filas = self.bd.consultar(
            "SELECT * FROM Usuario WHERE usuario=? AND contrasena=? AND tipo='padre'",
            (usuario, contra)
        )
        if filas:
            QMessageBox.information(self, "Bienvenido", f"¡Hola {filas[0][1]}!")
            self.hide()
            self.padres_principal = VentanaPadres(self.bd, filas[0][0])
            self.padres_principal.show()
        else:
            QMessageBox.critical(self, "Error", "Usuario o contraseña incorrectos.")

    def _volver(self):
        self.close()
        self.tipo_usuario = VentanaTipoUsuario()
        self.tipo_usuario.showMaximized()

class VentanaRegistroModerno(QWidget):
    class VentanaRegistroModerno(QWidget):
        def __init__(self, tipo_usuario="padre", bd=None):
            super().__init__()
            self.tipo_usuario = tipo_usuario
            self.bd = bd if bd else ConexionBD(DB_FILE)
            self.setWindowTitle(
                f"Registro - {'Padres de Familia' if tipo_usuario == 'padre' else 'Administrador/Empleado'}")
            self.showMaximized()
            self._aplicar_estilos()
            self._construir_ui()

    def _aplicar_estilos(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #F8FAFC;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLineEdit {
                background-color: white;
                border: 2px solid #E2E8F0;
                border-radius: 8px;
                padding: 12px 15px;
                font-size: 14px;
                margin: 5px 0px;
            }
            QLineEdit:focus {
                border-color: #3B82F6;
                background-color: #F0F9FF;
            }
            QLineEdit[error="true"] {
                border-color: #EF4444;
                background-color: #FEF2F2;
            }
            QPushButton {
                background-color: #1E40AF;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 25px;
                font-size: 16px;
                font-weight: bold;
                margin: 10px 0px;
            }
            QPushButton:hover {
                background-color: #1E3A8A;
            }
            QPushButton:disabled {
                background-color: #9CA3AF;
                color: #6B7280;
            }
            QLabel#titulo {
                font-size: 28px;
                font-weight: bold;
                color: #1E293B;
                margin-bottom: 10px;
            }
            QLabel#subtitulo {
                font-size: 16px;
                color: #64748B;
                margin-bottom: 30px;
            }
            QCheckBox {
                font-size: 14px;
                color: #374151;
                margin: 10px 0px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #D1D5DB;
            }
            QCheckBox::indicator:checked {
                background-color: #1E40AF;
                border-color: #1E40AF;
            }
        """)

    def _construir_ui(self):
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(40, 40, 40, 40)
        layout_principal.setSpacing(0)


        header_layout = QHBoxLayout()
        logo = QLabel("📚")
        logo.setStyleSheet("font-size: 40px;")
        titulo_app = QLabel("Librería ABC")
        titulo_app.setStyleSheet("font-size: 24px; font-weight: bold; color: #1E40AF; margin-left: 10px;")

        header_layout.addWidget(logo)
        header_layout.addWidget(titulo_app)
        header_layout.addStretch()
        layout_principal.addLayout(header_layout)


        titulo = QLabel("Crear Cuenta")
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitulo_text = "Para padres de familia" if self.tipo_usuario == "padre" else "Para administradores y empleados"
        subtitulo = QLabel(subtitulo_text)
        subtitulo.setObjectName("subtitulo")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout_principal.addWidget(titulo)
        layout_principal.addWidget(subtitulo)
        layout_principal.addSpacing(20)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        lbl_nombre = QLabel("Nombre completo:")
        lbl_nombre.setStyleSheet("font-weight: bold; color: #374151;")
        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Ingresa tu nombre completo")
        form_layout.addRow(lbl_nombre, self.txt_nombre)


        lbl_usuario = QLabel("Usuario:")
        lbl_usuario.setStyleSheet("font-weight: bold; color: #374151;")
        self.txt_usuario = QLineEdit()
        self.txt_usuario.setPlaceholderText("Elige un nombre de usuario")
        form_layout.addRow(lbl_usuario, self.txt_usuario)


        lbl_correo = QLabel("Correo electrónico:")
        lbl_correo.setStyleSheet("font-weight: bold; color: #374151;")
        self.txt_correo = QLineEdit()
        self.txt_correo.setPlaceholderText("tu@email.com")
        form_layout.addRow(lbl_correo, self.txt_correo)


        lbl_telefono = QLabel("Teléfono:")
        lbl_telefono.setStyleSheet("font-weight: bold; color: #374151;")
        self.txt_telefono = QLineEdit()
        self.txt_telefono.setPlaceholderText("+502 1234-5678")
        form_layout.addRow(lbl_telefono, self.txt_telefono)


        lbl_contrasena = QLabel("Contraseña:")
        lbl_contrasena.setStyleSheet("font-weight: bold; color: #374151;")
        self.txt_contrasena = QLineEdit()
        self.txt_contrasena.setPlaceholderText("Mínimo 8 caracteres")
        self.txt_contrasena.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow(lbl_contrasena, self.txt_contrasena)


        lbl_confirmar = QLabel("Confirmar contraseña:")
        lbl_confirmar.setStyleSheet("font-weight: bold; color: #374151;")
        self.txt_confirmar = QLineEdit()
        self.txt_confirmar.setPlaceholderText("Repite tu contraseña")
        self.txt_confirmar.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow(lbl_confirmar, self.txt_confirmar)

        layout_principal.addLayout(form_layout)
        layout_principal.addSpacing(20)


        self.check_terminos = QCheckBox("Acepto los términos y condiciones y la política de privacidad")
        layout_principal.addWidget(self.check_terminos)


        self.btn_registrar = QPushButton("Crear Cuenta")
        self.btn_registrar.clicked.connect(self._registrar_usuario)
        layout_principal.addWidget(self.btn_registrar)


        layout_login = QHBoxLayout()
        lbl_tiene_cuenta = QLabel("¿Ya tienes una cuenta?")
        lbl_tiene_cuenta.setStyleSheet("color: #64748B;")

        btn_login = QPushButton("Iniciar Sesión")
        btn_login.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #1E40AF;
                border: none;
                font-weight: bold;
                padding: 5px 10px;
            }
            QPushButton:hover {
                color: #1E3A8A;
                text-decoration: underline;
            }
        """)
        btn_login.clicked.connect(self._ir_a_login)

        layout_login.addStretch()
        layout_login.addWidget(lbl_tiene_cuenta)
        layout_login.addWidget(btn_login)
        layout_login.addStretch()

        layout_principal.addLayout(layout_login)
        layout_principal.addStretch()

        self.setLayout(layout_principal)


        self.txt_contrasena.textChanged.connect(self._validar_contraseña)
        self.txt_confirmar.textChanged.connect(self._validar_contraseña)
        self.txt_usuario.textChanged.connect(self._validar_usuario)

    def _validar_contraseña(self):

        contrasena = self.txt_contrasena.text()
        confirmar = self.txt_confirmar.text()

        if confirmar and contrasena != confirmar:
            self.txt_confirmar.setProperty("error", "true")
            self.txt_confirmar.setStyleSheet(self.txt_confirmar.styleSheet())
        else:
            self.txt_confirmar.setProperty("error", "false")
            self.txt_confirmar.setStyleSheet(self.txt_confirmar.styleSheet())

    def _validar_usuario(self):
        usuario = self.txt_usuario.text()
        if usuario and len(usuario) < 3:
            self.txt_usuario.setProperty("error", "true")
            self.txt_usuario.setStyleSheet(self.txt_usuario.styleSheet())
        else:
            self.txt_usuario.setProperty("error", "false")
            self.txt_usuario.setStyleSheet(self.txt_usuario.styleSheet())

    def _registrar_usuario(self):

        nombre = self.txt_nombre.text().strip()
        usuario = self.txt_usuario.text().strip()
        correo = self.txt_correo.text().strip()
        telefono = self.txt_telefono.text().strip()
        contrasena = self.txt_contrasena.text()
        confirmar = self.txt_confirmar.text()


        errores = []

        if not nombre:
            errores.append("El nombre completo es obligatorio")

        if not usuario or len(usuario) < 3:
            errores.append("El usuario debe tener al menos 3 caracteres")

        if not correo or "@" not in correo:
            errores.append("Ingresa un correo electrónico válido")

        if not contrasena or len(contrasena) < 8:
            errores.append("La contraseña debe tener al menos 8 caracteres")

        if contrasena != confirmar:
            errores.append("Las contraseñas no coinciden")

        if not self.check_terminos.isChecked():
            errores.append("Debes aceptar los términos y condiciones")

        if errores:
            QMessageBox.warning(self, "Error de validación", "\n".join(errores))
            return


        try:
            existente = self.bd.consultar("SELECT * FROM Usuario WHERE usuario=?", (usuario,))
            if existente:
                QMessageBox.warning(self, "Usuario existente",
                                    "El nombre de usuario ya está en uso. Por favor elige otro.")
                return


            self.bd.ejecutar(
                "INSERT INTO Usuario (nombre, usuario, contrasena, tipo) VALUES (?, ?, ?, ?)",
                (nombre, usuario, contrasena, self.tipo_usuario)
            )


            if self.tipo_usuario == "padre":
                self.bd.ejecutar(
                    "INSERT INTO Cliente (nombre, telefono, correo, total_compras, descuento) VALUES (?, ?, ?, ?, ?)",
                    (nombre, telefono, correo, 0, 0)
                )

            QMessageBox.information(
                self,
                "Registro exitoso",
                f"¡Cuenta creada exitosamente!\n\n"
                f"Bienvenido/a {nombre}\n"
                f"Usuario: {usuario}\n\n"
                f"Ya puedes iniciar sesión en el sistema."
            )

            self._ir_a_login()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo completar el registro:\n{str(e)}")

    def _ir_a_login(self):

        self.close()
        if self.tipo_usuario == "padre":
            self.ventana_login = VentanaLoginPadres()
        else:
            self.ventana_login = VentanaLoginAdmin()
        self.ventana_login.show()

class VentanaPadres(QWidget):
    def __init__(self, bd, id_usuario):
        super().__init__()
        self.bd = bd
        self.id_usuario = id_usuario
        self.setWindowTitle("Padres de Familia - Librería ABC")
        self.resize(1000, 700)
        self.lista_seleccionados = []
        self.carrito_compras = []
        self._construir_ui()

    def _construir_ui(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)


        panel_botones = QWidget()
        panel_botones.setFixedWidth(250)
        panel_botones.setStyleSheet("""
            QWidget {
                background-color: #1E40AF;
                border-radius: 10px;
                margin: 10px;
            }
        """)

        layout_botones = QVBoxLayout(panel_botones)
        layout_botones.setContentsMargins(10, 20, 10, 20)
        layout_botones.setSpacing(10)


        usuario_info = self.bd.consultar("SELECT nombre FROM Usuario WHERE id_usuario=?", (self.id_usuario,))
        nombre_usuario = usuario_info[0][0] if usuario_info else "Usuario"

        lbl_usuario = QLabel(f"👤 {nombre_usuario}")
        lbl_usuario.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                background-color: #1E3A8A;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        lbl_usuario.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_botones.addWidget(lbl_usuario)


        botones_menu = [
            ("📚 Ver Catálogo", self.mostrar_catalogo),
            ("📝 Mi Lista de Útiles", self.mostrar_listado),
            ("🛒 Carrito de Compras", self.mostrar_carrito),
            ("📋 Listas Predefinidas", self.mostrar_listas_predefinidas),
            ("❌ Cerrar Sesión", self.cerrar_sesion)
        ]

        for texto, funcion in botones_menu:
            btn = QPushButton(texto)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3B82F6;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 15px;
                    font-size: 14px;
                    font-weight: bold;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #2563EB;
                }
            """)
            btn.clicked.connect(funcion)
            layout_botones.addWidget(btn)

        layout_botones.addStretch()


        self.panel_contenido = QScrollArea()
        self.panel_contenido.setWidgetResizable(True)
        self.panel_contenido.setStyleSheet("QScrollArea { border: none; background-color: #F8FAFC; }")

        self.contenido_widget = QWidget()
        self.contenido_layout = QVBoxLayout(self.contenido_widget)
        self.panel_contenido.setWidget(self.contenido_widget)


        self.mostrar_bienvenida()

        main_layout.addWidget(panel_botones)
        main_layout.addWidget(self.panel_contenido)

    def mostrar_bienvenida(self):
        self._limpiar_panel()

        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icono = QLabel("📚")
        icono.setStyleSheet("font-size: 80px;")
        icono.setAlignment(Qt.AlignmentFlag.AlignCenter)

        titulo = QLabel("¡Bienvenido a Librería ABC!")
        titulo.setStyleSheet("font-size: 32px; font-weight: bold; color: #1E293B; margin: 20px;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitulo = QLabel("Selecciona una opción del menú lateral para comenzar")
        subtitulo.setStyleSheet("font-size: 18px; color: #64748B; margin: 10px;")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        welcome_layout.addWidget(icono)
        welcome_layout.addWidget(titulo)
        welcome_layout.addWidget(subtitulo)

        self.contenido_layout.addWidget(welcome_widget)

    def mostrar_catalogo(self):
        self._limpiar_panel()

        header = QWidget()
        header_layout = QHBoxLayout(header)

        titulo = QLabel("📚 Catálogo de Productos")
        titulo.setStyleSheet("font-size: 28px; font-weight: bold; color: #1E293B;")

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("🔍 Buscar productos...")
        self.txt_buscar.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #E2E8F0;
                border-radius: 8px;
                font-size: 14px;
                min-width: 300px;
            }
        """)
        self.txt_buscar.textChanged.connect(self.filtrar_catalogo)

        header_layout.addWidget(titulo)
        header_layout.addStretch()
        header_layout.addWidget(self.txt_buscar)

        self.contenido_layout.addWidget(header)

        self.scroll_productos = QScrollArea()
        self.scroll_productos.setWidgetResizable(True)
        self.scroll_productos.setStyleSheet("QScrollArea { border: none; }")

        self.widget_productos = QWidget()
        self.layout_productos = QVBoxLayout(self.widget_productos)
        self.scroll_productos.setWidget(self.widget_productos)

        self.contenido_layout.addWidget(self.scroll_productos)

        self.cargar_productos()

    def cargar_productos(self):
        try:
            productos = self.bd.consultar("""
                SELECT p.id_producto, p.nombre, c.nombre as categoria, 
                       p.precio, p.stock, p.imagen, p.tipo_imagen
                FROM Producto p 
                LEFT JOIN Categoria c ON p.id_categoria = c.id_categoria
                ORDER BY p.nombre
            """)

            self.productos_completos = productos
            self.actualizar_vista_productos(productos)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los productos: {str(e)}")

    def actualizar_vista_productos(self, productos):
        for i in reversed(range(self.layout_productos.count())):
            item = self.layout_productos.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

        if not productos:
            lbl_vacio = QLabel("No se encontraron productos")
            lbl_vacio.setStyleSheet("font-size: 16px; color: #64748B; text-align: center; margin: 50px;")
            self.layout_productos.addWidget(lbl_vacio)
            return

        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(15)

        for i, producto in enumerate(productos):
            card = self.crear_card_producto(producto)
            grid_layout.addWidget(card, i // 3, i % 3)

        self.layout_productos.addWidget(grid_widget)

    def crear_card_producto(self, producto):
        id_producto, nombre, categoria, precio, stock, imagen_blob, tipo_imagen = producto

        card = QWidget()
        card.setFixedSize(280, 320)
        card.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #E2E8F0;
                border-radius: 15px;
                padding: 15px;
            }
            QWidget:hover {
                border-color: #3B82F6;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(10)


        lbl_imagen = QLabel()
        lbl_imagen.setFixedSize(120, 120)
        lbl_imagen.setStyleSheet("""
            QLabel {
                background-color: #F8FAFC;
                border-radius: 10px;
                qproperty-alignment: 'AlignCenter';
                font-size: 40px;
            }
        """)

        if imagen_blob:
            pixmap = ManejadorImagenes.blob_a_imagen(imagen_blob, tipo_imagen)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
                lbl_imagen.setPixmap(pixmap)
            else:
                emoji = "📦"
                lbl_imagen.setText(emoji)
        else:
            emoji = "📦"
            lbl_imagen.setText(emoji)


        lbl_nombre = QLabel(nombre)
        lbl_nombre.setStyleSheet("font-size: 16px; font-weight: bold; color: #1E293B;")
        lbl_nombre.setWordWrap(True)

        lbl_categoria = QLabel(categoria or "Sin categoría")
        lbl_categoria.setStyleSheet("font-size: 12px; color: #64748B;")

        lbl_precio = QLabel(f"Q{precio:.2f}")
        lbl_precio.setStyleSheet("font-size: 18px; font-weight: bold; color: #059669;")

        lbl_stock = QLabel(f"Stock: {stock}")
        color_stock = "#EF4444" if stock == 0 else "#F59E0B" if stock < 5 else "#10B981"
        lbl_stock.setStyleSheet(f"font-size: 12px; color: {color_stock}; font-weight: bold;")


        btn_layout = QHBoxLayout()

        btn_ver = QPushButton("Ver")
        btn_ver.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 12px;
            }
        """)
        btn_ver.clicked.connect(lambda: self.ver_detalle_producto(producto))

        btn_agregar = QPushButton("🛒 Agregar")
        btn_agregar.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 12px;
            }
        """)
        btn_agregar.clicked.connect(lambda: self.agregar_al_carrito(producto))
        btn_agregar.setEnabled(stock > 0)

        btn_layout.addWidget(btn_ver)
        btn_layout.addWidget(btn_agregar)

        layout.addWidget(lbl_imagen, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_nombre)
        layout.addWidget(lbl_categoria)
        layout.addWidget(lbl_precio)
        layout.addWidget(lbl_stock)
        layout.addLayout(btn_layout)

        return card

    def mostrar_listado(self):
        self._limpiar_panel()

        titulo = QLabel("📝 Mi Lista de Útiles Personal")
        titulo.setStyleSheet("font-size: 28px; font-weight: bold; color: #1E293B; margin-bottom: 20px;")
        self.contenido_layout.addWidget(titulo)

        self.lista_mis_utiles = QListWidget()
        self.lista_mis_utiles.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 2px solid #E2E8F0;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
            }
        """)

        for item in self.lista_seleccionados:
            self.lista_mis_utiles.addItem(item)

        self.contenido_layout.addWidget(self.lista_mis_utiles)

        botones_layout = QHBoxLayout()

        btn_agregar = QPushButton("➕ Agregar Útil")
        btn_agregar.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
        """)
        btn_agregar.clicked.connect(self.agregar_util)

        btn_eliminar = QPushButton("🗑️ Eliminar Seleccionado")
        btn_eliminar.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
        """)
        btn_eliminar.clicked.connect(self.eliminar_util)

        btn_limpiar = QPushButton("🧹 Limpiar Lista")
        btn_limpiar.setStyleSheet("""
            QPushButton {
                background-color: #F59E0B;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
        """)
        btn_limpiar.clicked.connect(self.limpiar_lista)

        botones_layout.addWidget(btn_agregar)
        botones_layout.addWidget(btn_eliminar)
        botones_layout.addWidget(btn_limpiar)
        botones_layout.addStretch()

        self.contenido_layout.addLayout(botones_layout)

    def agregar_util(self):
        productos = ["Cuaderno", "Lápiz", "Borrador", "Colores", "Mochila", "Regla",
                     "Tijeras", "Pegamento", "Compás", "Transportador", "Calculadora"]

        item, ok = QInputDialog.getItem(
            self, "Agregar útil", "Selecciona un útil:", productos, 0, False
        )

        if ok and item:
            if item not in self.lista_seleccionados:
                self.lista_seleccionados.append(item)
                self.lista_mis_utiles.addItem(item)
                QMessageBox.information(self, "Éxito", f"Se agregó '{item}' a tu listado.")

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
                self, "Confirmar limpieza", "¿Estás seguro de que quieres limpiar toda tu lista de útiles?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if respuesta == QMessageBox.StandardButton.Yes:
                self.lista_seleccionados.clear()
                self.lista_mis_utiles.clear()
                QMessageBox.information(self, "Éxito", "Lista limpiada correctamente.")

    def agregar_al_carrito(self, producto):
        id_producto, nombre, categoria, precio, stock, imagen_blob, tipo_imagen = producto


        cantidad, ok = QInputDialog.getInt(
            self,
            "Agregar al carrito",
            f"¿Cuántas unidades de '{nombre}' deseas agregar?\nPrecio unitario: Q{precio:.2f}\nStock disponible: {stock}",
            1,
            1,
            stock,
            1
        )

        if ok and cantidad > 0:

            for i, (prod, cant) in enumerate(self.carrito_compras):
                if prod[0] == id_producto:
                    self.carrito_compras[i] = (prod, cant + cantidad)
                    break
            else:
                self.carrito_compras.append((producto, cantidad))

            QMessageBox.information(self, "Éxito", f"Se agregaron {cantidad} unidad(es) de '{nombre}' al carrito.")

    def mostrar_carrito(self):
        self._limpiar_panel()

        titulo = QLabel("🛒 Carrito de Compras")
        titulo.setStyleSheet("font-size: 28px; font-weight: bold; color: #1E293B; margin-bottom: 20px;")
        self.contenido_layout.addWidget(titulo)

        if not self.carrito_compras:
            lbl_vacio = QLabel("Tu carrito está vacío")
            lbl_vacio.setStyleSheet("font-size: 18px; color: #64748B; text-align: center; margin: 50px;")
            self.contenido_layout.addWidget(lbl_vacio)


            btn_catalogo = QPushButton("📚 Ir al Catálogo")
            btn_catalogo.setStyleSheet("""
                QPushButton {
                    background-color: #3B82F6;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 25px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2563EB;
                }
            """)
            btn_catalogo.clicked.connect(self.mostrar_catalogo)
            self.contenido_layout.addWidget(btn_catalogo, alignment=Qt.AlignmentFlag.AlignCenter)

            return


        tabla_carrito = QTableWidget()
        tabla_carrito.setColumnCount(5)
        tabla_carrito.setHorizontalHeaderLabels(["Producto", "Precio Unitario", "Cantidad", "Subtotal", "Acciones"])

        tabla_carrito.setRowCount(len(self.carrito_compras))

        total = 0
        for i, (producto, cantidad) in enumerate(self.carrito_compras):
            id_producto, nombre, categoria, precio, stock, imagen_blob, tipo_imagen = producto
            subtotal = precio * cantidad
            total += subtotal

            tabla_carrito.setItem(i, 0, QTableWidgetItem(nombre))
            tabla_carrito.setItem(i, 1, QTableWidgetItem(f"Q{precio:.2f}"))
            tabla_carrito.setItem(i, 2, QTableWidgetItem(str(cantidad)))
            tabla_carrito.setItem(i, 3, QTableWidgetItem(f"Q{subtotal:.2f}"))


            widget_acciones = QWidget()
            layout_acciones = QHBoxLayout(widget_acciones)
            layout_acciones.setContentsMargins(5, 2, 5, 2)

            btn_eliminar = QPushButton("🗑️")
            btn_eliminar.setToolTip("Eliminar del carrito")
            btn_eliminar.setFixedSize(30, 25)
            btn_eliminar.setStyleSheet("""
                QPushButton {
                    background-color: #EF4444;
                    color: white;
                    border: none;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #DC2626;
                }
            """)
            btn_eliminar.clicked.connect(lambda checked, idx=i: self.eliminar_del_carrito(idx))

            layout_acciones.addWidget(btn_eliminar)
            tabla_carrito.setCellWidget(i, 4, widget_acciones)


        tabla_carrito.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                gridline-color: #E2E8F0;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #E2E8F0;
            }
            QHeaderView::section {
                background-color: #1E40AF;
                color: white;
                font-weight: bold;
                padding: 12px;
                border: none;
            }
        """)
        tabla_carrito.horizontalHeader().setStretchLastSection(True)
        tabla_carrito.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.contenido_layout.addWidget(tabla_carrito)


        total_layout = QHBoxLayout()

        lbl_total = QLabel(f"Total: Q{total:.2f}")
        lbl_total.setStyleSheet("font-size: 20px; font-weight: bold; color: #059669;")

        btn_comprar = QPushButton("💰 Realizar Compra")
        btn_comprar.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 25px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        btn_comprar.clicked.connect(self.realizar_compra)

        btn_limpiar = QPushButton("🧹 Limpiar Carrito")
        btn_limpiar.setStyleSheet("""
            QPushButton {
                background-color: #F59E0B;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 25px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D97706;
            }
        """)
        btn_limpiar.clicked.connect(self.limpiar_carrito)

        total_layout.addWidget(lbl_total)
        total_layout.addStretch()
        total_layout.addWidget(btn_limpiar)
        total_layout.addWidget(btn_comprar)

        self.contenido_layout.addLayout(total_layout)

    def eliminar_del_carrito(self, indice):
        if 0 <= indice < len(self.carrito_compras):
            producto, cantidad = self.carrito_compras[indice]
            nombre = producto[1]

            respuesta = QMessageBox.question(
                self,
                "Confirmar eliminación",
                f"¿Eliminar '{nombre}' del carrito?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if respuesta == QMessageBox.StandardButton.Yes:
                del self.carrito_compras[indice]
                self.mostrar_carrito()

    def limpiar_carrito(self):
        if self.carrito_compras:
            respuesta = QMessageBox.question(
                self,
                "Confirmar limpieza",
                "¿Estás seguro de que quieres limpiar todo el carrito?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if respuesta == QMessageBox.StandardButton.Yes:
                self.carrito_compras.clear()
                self.mostrar_carrito()
        else:
            QMessageBox.information(self, "Información", "El carrito ya está vacío.")

    def realizar_compra(self):

        if not self.carrito_compras:
            QMessageBox.warning(self, "Carrito vacío", "No hay productos en el carrito.")
            return


        total = sum(producto[3] * cantidad for producto, cantidad in self.carrito_compras)

        respuesta = QMessageBox.question(
            self,
            "Confirmar compra",
            f"¿Confirmar compra por un total de Q{total:.2f}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            try:

                fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                self.bd.ejecutar(
                    "INSERT INTO Venta (id_cliente, fecha, total, id_empleado) VALUES (?, ?, ?, ?)",
                    (self.id_usuario, fecha, total, 1)
                )
                id_venta = self.bd.cursor.lastrowid


                for producto, cantidad in self.carrito_compras:
                    id_producto, nombre, categoria, precio, stock, imagen_blob, tipo_imagen = producto


                    self.bd.ejecutar(
                        "INSERT INTO DetalleVenta (id_venta, id_producto, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?)",
                        (id_venta, id_producto, cantidad, precio, precio * cantidad)
                    )


                    self.bd.ejecutar(
                        "UPDATE Producto SET stock = stock - ? WHERE id_producto = ?",
                        (cantidad, id_producto)
                    )

                QMessageBox.information(
                    self,
                    "Compra exitosa",
                    f"¡Tu compra se ha realizado con éxito!\n"
                    f"Total: Q{total:.2f}\n"
                    f"Número de venta: {id_venta}"
                )

                self.carrito_compras.clear()
                self.mostrar_carrito()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo completar la compra: {str(e)}")

    def mostrar_listas_predefinidas(self):

        self._limpiar_panel()

        titulo = QLabel("📋 Listas de Útiles Predefinidas")
        titulo.setStyleSheet("font-size: 28px; font-weight: bold; color: #1E293B; margin-bottom: 20px;")
        self.contenido_layout.addWidget(titulo)


        listas_data = [
            ("1°-3° Primaria", 185.00,
             ["Cuaderno cuadriculado", "Lápices HB x6", "Borradores x2", "Caja de colores x12", "Tijeras punta roma",
              "Pegamento en barra"]),
            ("4°-6° Primaria", 220.00,
             ["Cuadernos profesionales x3", "Lápices HB x12", "Regla 30cm", "Transportador", "Compás",
              "Calculadora básica"]),
            ("1°-3° Secundaria", 285.00,
             ["Cuadernos universitarios x4", "Lápices de grafito", "Calculadora científica", "Juego de geometría",
              "Diccionario español"]),
            ("4°-6° Secundaria", 320.00,
             ["Cuadernos especializados", "Material de dibujo técnico", "Calculadora avanzada",
              "Diccionario inglés-español", "Block de hojas"]),
        ]

        for grado, precio, utiles in listas_data:
            grupo = QGroupBox(f"{grado} - Q{precio:.2f}")
            grupo.setStyleSheet("""
                QGroupBox {
                    font-size: 18px;
                    font-weight: bold;
                    color: #1E40AF;
                    border: 2px solid #E2E8F0;
                    border-radius: 10px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
            """)

            layout_grupo = QVBoxLayout()

            for util in utiles:
                lbl_util = QLabel(f"• {util}")
                lbl_util.setStyleSheet("font-size: 14px; color: #374151; margin: 2px;")
                layout_grupo.addWidget(lbl_util)

            btn_agregar_lista = QPushButton("➕ Agregar esta lista a mis útiles")
            btn_agregar_lista.setStyleSheet("""
                QPushButton {
                    background-color: #3B82F6;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 15px;
                    font-size: 12px;
                    margin-top: 10px;
                }
                QPushButton:hover {
                    background-color: #2563EB;
                }
            """)
            btn_agregar_lista.clicked.connect(lambda checked, u=utiles: self.agregar_lista_predefinida(u))

            layout_grupo.addWidget(btn_agregar_lista)
            grupo.setLayout(layout_grupo)
            self.contenido_layout.addWidget(grupo)

    def agregar_lista_predefinida(self, utiles):
        nuevos_utiles = 0
        for util in utiles:
            if util not in self.lista_seleccionados:
                self.lista_seleccionados.append(util)
                nuevos_utiles += 1

        if nuevos_utiles > 0:
            QMessageBox.information(self, "Lista agregada", f"Se agregaron {nuevos_utiles} nuevos útiles a tu lista.")
        else:
            QMessageBox.information(self, "Información", "Todos los útiles de esta lista ya están en tu listado.")

        self.mostrar_listado()

    def ver_detalle_producto(self, producto):
        id_producto, nombre, categoria, precio, stock, imagen_blob, tipo_imagen = producto

        mensaje = f"""
        📦 {nombre}

        📊 Información:
        • Categoría: {categoria or 'No especificada'}
        • Precio: Q{precio:.2f}
        • Stock: {stock}
        """

        QMessageBox.information(self, "Detalles del Producto", mensaje)

    def filtrar_catalogo(self):
        texto = self.txt_buscar.text().lower()
        if hasattr(self, 'productos_completos'):
            productos_filtrados = [
                p for p in self.productos_completos
                if texto in p[1].lower()
            ]
            self.actualizar_vista_productos(productos_filtrados)

    def cerrar_sesion(self):
        respuesta = QMessageBox.question(
            self, "Cerrar sesión", "¿Estás seguro de que quieres cerrar sesión?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            self.close()

    def _limpiar_panel(self):
        for i in reversed(range(self.contenido_layout.count())):
            item = self.contenido_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

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
            ("Agregar productos ejemplo", self._agregar_productos_ejemplo),
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
        """Limpia todos los campos del formulario"""
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
                    (self.id_usuario, fecha, total, 1)
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


        self.lbl_productos = QLabel("Productos agregados:\n")
        layout.addWidget(self.lbl_productos)


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


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyleSheet("""
        QMessageBox {
            background-color: white;
        }
        QMessageBox QPushButton {
            background-color: #3B82F6;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 8px 15px;
            min-width: 80px;
        }
        QMessageBox QPushButton:hover {
            background-color: #2563EB;
        }
    """)


    ventana_inicio = VentanaInicio()
    ventana_inicio.show()

    sys.exit(app.exec())
