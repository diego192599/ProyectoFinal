
import os
import sys
import sqlite3
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit,
    QVBoxLayout, QMessageBox, QInputDialog, QHBoxLayout,
    QStackedLayout, QListWidget, QListWidgetItem, QFileDialog,
    QSpinBox, QScrollArea, QTableWidget, QTableWidgetItem, QComboBox,
    QFrame, QGridLayout, QGroupBox, QFormLayout, QCheckBox, QHeaderView, QTabWidget
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
        self.setStyleSheet("background-color: #F5F5F5;")
        self.bd = ConexionBD(DB_FILE)

        self.usuario_actual = None
        self.id_usuario_actual = None
        self.tipo_usuario = None

        self._construir_ui()
        self.showMaximized()

        self.ventana_login = None
        self.ventana_padres = None
        self.ventana_admin = None
        self.ventana_promociones = None
        self.ventana_contacto = None

    def _construir_ui(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("border: none; background: transparent;")

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header = self._crear_header()
        hero = self._crear_hero_section()
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

        scroll_area.setWidget(main_widget)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll_area)

    def _crear_header(self):
        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet("background-color: #1E40AF; color: white;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 0, 30, 0)

        logo_layout = QHBoxLayout()
        logo_label = QLabel("📚")
        logo_label.setStyleSheet("font-size: 32px; background: transparent;")
        titulo = QLabel("Librería Escolar ABC")
        titulo.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: white; margin-left: 10px; background: transparent;")
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

        self.user_container = QWidget()
        self.user_container.setStyleSheet("background: transparent;")
        self.user_layout = QHBoxLayout(self.user_container)
        self.user_layout.setContentsMargins(0, 0, 0, 0)
        self.user_layout.setSpacing(10)

        self.btn_login = QPushButton("Iniciar Sesión")
        self.btn_login.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)
        self.btn_login.clicked.connect(self._mostrar_login)

        self.user_widget = QWidget()
        self.user_widget.setStyleSheet("background: transparent;")
        user_widget_layout = QHBoxLayout(self.user_widget)
        user_widget_layout.setContentsMargins(0, 0, 0, 0)
        user_widget_layout.setSpacing(10)

        self.lbl_usuario = QLabel()
        self.lbl_usuario.setStyleSheet("""
            QLabel {
                color: white;
                font-weight: bold;
                background: transparent;
                padding: 5px 10px;
                border-radius: 5px;
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)

        self.btn_perfil = QPushButton("👤 Mi Perfil")
        self.btn_perfil.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.btn_perfil.clicked.connect(self._ir_a_perfil)

        self.btn_cerrar_sesion = QPushButton("🚪 Cerrar Sesión")
        self.btn_cerrar_sesion.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """)
        self.btn_cerrar_sesion.clicked.connect(self._cerrar_sesion)

        user_widget_layout.addWidget(self.lbl_usuario)
        user_widget_layout.addWidget(self.btn_perfil)
        user_widget_layout.addWidget(self.btn_cerrar_sesion)

        self.user_layout.addWidget(self.btn_login)
        self.user_layout.addWidget(self.user_widget)

        header_layout.addLayout(logo_layout)
        header_layout.addStretch()
        header_layout.addLayout(nav_layout)
        header_layout.addStretch()
        header_layout.addWidget(self.user_container)

        self._actualizar_ui_sesion()

        return header

    def _crear_hero_section(self):
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
        hero_title.setStyleSheet("""
            font-size: 48px; 
            font-weight: bold; 
            color: white; 
            line-height: 1.2;
            background: transparent;
        """)
        hero_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        hero_subtitle = QLabel("Útiles escolares de calidad para todos los grados")
        hero_subtitle.setStyleSheet("""
            font-size: 20px; 
            color: #E0F2FE; 
            margin-top: 20px;
            background: transparent;
        """)
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

        return hero

    def _crear_seccion_caracteristicas(self):
        features = QWidget()
        features_layout = QVBoxLayout(features)
        features_layout.setContentsMargins(50, 50, 50, 50)

        features_title = QLabel("¿Por qué elegirnos?")
        features_title.setStyleSheet("""
            font-size: 36px; 
            font-weight: bold; 
            color: #1E293B; 
            margin-bottom: 40px;
            background: transparent;
        """)
        features_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        features_grid = QHBoxLayout()
        features_grid.setSpacing(20)
        features_grid.setAlignment(Qt.AlignmentFlag.AlignCenter)

        features_data = [
            ("🚚", "Entrega Rápida", "Recibe tus productos en 24-48 horas", self._ir_a_envios),
            ("💰", "Precios Bajos", "Los mejores precios del mercado", self._ir_a_ofertas),
            ("⭐", "Calidad Garantizada", "Productos de primera calidad", self._ir_a_calidad),
            ("📦", "Gran Inventario", "Todo lo que necesitas en un solo lugar", self._ir_a_inventario)
        ]

        for icono, titulo, desc, funcion in features_data:
            card = QWidget()
            card.setMinimumWidth(250)
            card.setMinimumHeight(180)
            card.setMaximumWidth(300)
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
            card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            icon = QLabel(icono)
            icon.setStyleSheet("""
                font-size: 50px; 
                background: transparent;
                min-height: 60px;
            """)
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

            title = QLabel(titulo)
            title.setStyleSheet("""
                font-size: 20px; 
                font-weight: bold; 
                color: #1E293B; 
                margin-top: 10px;
                background: transparent;
            """)
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)

            description = QLabel(desc)
            description.setStyleSheet("""
                font-size: 14px; 
                color: #64748B; 
                margin-top: 10px; 
                text-align: center;
                background: transparent;
            """)
            description.setWordWrap(True)
            description.setAlignment(Qt.AlignmentFlag.AlignCenter)

            card_layout.addWidget(icon)
            card_layout.addWidget(title)
            card_layout.addWidget(description)

            card.mousePressEvent = lambda event, func=funcion: func()
            features_grid.addWidget(card)

        features_layout.addWidget(features_title)
        features_layout.addLayout(features_grid)

        return features

    def _crear_seccion_productos(self):
        productos = QWidget()
        productos_layout = QVBoxLayout(productos)
        productos_layout.setContentsMargins(50, 50, 50, 50)

        productos_title = QLabel("Productos Destacados")
        productos_title.setStyleSheet("""
            font-size: 36px; 
            font-weight: bold; 
            color: #1E293B; 
            margin-bottom: 30px;
            background: transparent;
        """)
        productos_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        productos_grid = QHBoxLayout()
        productos_grid.setSpacing(20)
        productos_grid.setAlignment(Qt.AlignmentFlag.AlignCenter)

        productos_data = [
            ("Cuadernos", "útiles escolares", "Desde Q25.00", self._ir_a_cuadernos),
            ("Lápices", "escritura", "Desde Q15.00", self._ir_a_lapices),
            ("Mochilas", "mochilas", "Desde Q150.00", self._ir_a_mochilas),
            ("Colores", "arte", "Desde Q45.00", self._ir_a_colores)
        ]

        for titulo, categoria, precio, funcion in productos_data:
            card = QWidget()
            card.setMinimumWidth(180)
            card.setMinimumHeight(200)
            card.setMaximumWidth(220)

            colores_categorias = {
                "útiles escolares": "#FFE4E6",
                "escritura": "#E0F2FE",
                "mochilas": "#F0FDF4",
                "arte": "#FEF7CD"
            }

            emojis_categorias = {
                "útiles escolares": "📓",
                "escritura": "✏️",
                "mochilas": "🎒",
                "arte": "🎨"
            }

            color_fondo = colores_categorias.get(categoria, "#F5F5F5")
            emoji = emojis_categorias.get(categoria, "📦")

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
            card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            icon = QLabel(emoji)
            icon.setStyleSheet("""
                font-size: 60px; 
                background: transparent;
                min-height: 70px;
            """)
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

            title = QLabel(titulo)
            title.setStyleSheet("""
                font-size: 18px; 
                font-weight: bold; 
                color: #1E293B; 
                margin-top: 15px;
                background: transparent;
            """)
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)

            price = QLabel(precio)
            price.setStyleSheet("""
                font-size: 16px; 
                color: #64748B; 
                margin-top: 10px;
                background: transparent;
            """)
            price.setAlignment(Qt.AlignmentFlag.AlignCenter)

            card_layout.addWidget(icon)
            card_layout.addWidget(title)
            card_layout.addWidget(price)

            card.mousePressEvent = lambda event, func=funcion: func()
            productos_grid.addWidget(card)

        productos_layout.addWidget(productos_title)
        productos_layout.addLayout(productos_grid)

        return productos

    def _crear_seccion_listas(self):
        listas = QWidget()
        listas.setStyleSheet("background-color: #F8FAFC;")
        listas_layout = QVBoxLayout(listas)
        listas_layout.setContentsMargins(50, 50, 50, 50)

        listas_title = QLabel("Listas de Útiles por Grado")
        listas_title.setStyleSheet("""
            font-size: 36px; 
            font-weight: bold; 
            color: #1E293B; 
            margin-bottom: 30px;
            background: transparent;
        """)
        listas_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        tabla = QTableWidget()
        tabla.setColumnCount(4)
        tabla.setRowCount(5)
        tabla.setHorizontalHeaderLabels(["Grado", "Productos Incluidos", "Precio Total", "Acción"])

        header = tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

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
                background: transparent;
            }
            QHeaderView::section {
                background-color: #1E40AF;
                color: white;
                font-weight: bold;
                padding: 12px;
                border: none;
            }
        """)
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
        info_title.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold; 
            margin-bottom: 20px;
            background: transparent;
        """)

        info_text = QLabel("Tu tienda de confianza para\nútiles escolares de calidad")
        info_text.setStyleSheet("""
            color: #94A3B8; 
            line-height: 1.5;
            background: transparent;
        """)

        info_col.addWidget(info_title)
        info_col.addWidget(info_text)

        links_col = QVBoxLayout()
        links_title = QLabel("Enlaces Rápidos")
        links_title.setStyleSheet("""
            font-size: 16px; 
            font-weight: bold; 
            margin-bottom: 15px;
            background: transparent;
        """)

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
            lbl.setStyleSheet("""
                color: #94A3B8; 
                margin: 5px 0;
                background: transparent;
            """)
            lbl.setCursor(Qt.CursorShape.PointingHandCursor)
            lbl.mousePressEvent = lambda event, func=link_func: func()
            links_col.addWidget(lbl)

        contact_col = QVBoxLayout()
        contact_title = QLabel("Contacto")
        contact_title.setStyleSheet("""
            font-size: 16px; 
            font-weight: bold; 
            margin-bottom: 15px;
            background: transparent;
        """)

        contact_info = [
            "📞 (502) 1234-5678",
            "📧 info@libreriaabc.com",
            "📍 Ciudad de Guatemala"
        ]

        contact_col.addWidget(contact_title)
        for info in contact_info:
            lbl = QLabel(info)
            lbl.setStyleSheet("""
                color: #94A3B8; 
                margin: 5px 0;
                background: transparent;
            """)
            contact_col.addWidget(lbl)

        footer_layout.addLayout(info_col)
        footer_layout.addStretch()
        footer_layout.addLayout(links_col)
        footer_layout.addStretch()
        footer_layout.addLayout(contact_col)

        return footer

    def _ir_a_inicio(self):
        self.showMaximized()

    def _ir_a_productos(self):
        if self.usuario_actual:
            if self.tipo_usuario == 'admin':
                self.abrir_ventana_admin(self.bd)
            else:
                self.abrir_ventana_padres(self.bd, self.id_usuario_actual)
        else:
            self._mostrar_login()

    def _ir_a_listas(self):
        if self.usuario_actual:
            if self.tipo_usuario == 'admin':
                self.abrir_ventana_admin(self.bd)
            else:
                self.abrir_ventana_padres(self.bd, self.id_usuario_actual)
        else:
            self._mostrar_login()

    def _ir_a_promociones(self):
        self.hide()
        self.ventana_promociones = VentanaPromociones(ventana_principal=self)
        self.ventana_promociones.showMaximized()

    def _ir_a_contacto(self):
        self.hide()
        self.ventana_contacto = VentanaContacto(ventana_principal=self)
        self.ventana_contacto.showMaximized()

    def _ir_a_catalogo(self):
        if self.usuario_actual:
            if self.tipo_usuario == 'admin':
                self.abrir_ventana_admin(self.bd)
            else:
                self.abrir_ventana_padres(self.bd, self.id_usuario_actual)
        else:
            self._mostrar_login()

    def _ir_a_cuadernos(self):
        if self.usuario_actual:
            if self.tipo_usuario == 'admin':
                self.abrir_ventana_admin(self.bd)
            else:
                self.abrir_ventana_padres(self.bd, self.id_usuario_actual)
        else:
            self._mostrar_login()

    def _ir_a_lapices(self):
        if self.usuario_actual:
            if self.tipo_usuario == 'admin':
                self.abrir_ventana_admin(self.bd)
            else:
                self.abrir_ventana_padres(self.bd, self.id_usuario_actual)
        else:
            self._mostrar_login()

    def _ir_a_mochilas(self):
        if self.usuario_actual:
            if self.tipo_usuario == 'admin':
                self.abrir_ventana_admin(self.bd)
            else:
                self.abrir_ventana_padres(self.bd, self.id_usuario_actual)
        else:
            self._mostrar_login()

    def _ir_a_colores(self):
        if self.usuario_actual:
            if self.tipo_usuario == 'admin':
                self.abrir_ventana_admin(self.bd)
            else:
                self.abrir_ventana_padres(self.bd, self.id_usuario_actual)
        else:
            self._mostrar_login()

    def _ir_a_envios(self):
        QMessageBox.information(self, "Envíos y Entregas",
                                "🚚 **Información de Envíos**\n\n"
                                "• **Entrega estándar:** 24-48 horas\n"
                                "• **Envío express:** Mismo día (pedidos antes de las 12pm)\n"
                                "• **Costo de envío:** Q25.00 en ciudad\n"
                                "• **Envío gratis:** En compras mayores a Q200\n"
                                "• **Área de cobertura:** Toda el área metropolitana")

    def _ir_a_ofertas(self):
        QMessageBox.information(self, "Ofertas Especiales",
                                "💰 **Las Mejores Ofertas**\n\n"
                                "🔥 **Ofertas de la Semana:**\n"
                                "• Pack de regreso a clases: Q199.00 (valor Q250)\n"
                                "• Mochila + Estuche: Q280.00\n"
                                "• Cuadernos x5: Q99.00\n\n"
                                "🎁 **Promociones permanentes:**\n"
                                "• 10% descuento pagando con tarjeta\n"
                                "• Puntos acumulables por cada compra")

    def _ir_a_calidad(self):
        QMessageBox.information(self, "Nuestra Calidad",
                                "⭐ **Estándares de Calidad**\n\n"
                                "• Productos 100% originales y certificados\n"
                                "• Materiales de primera calidad\n"
                                "• Garantía en todos nuestros productos\n"
                                "• Proveedores confiables y verificados\n"
                                "• Control de calidad riguroso")

    def _ir_a_inventario(self):
        QMessageBox.information(self, "Nuestro Inventario",
                                "📦 **Amplio Inventario**\n\n"
                                "Contamos con más de 500 productos diferentes:\n"
                                "• Útiles escolares para todos los grados\n"
                                "• Material de oficina y papelería\n"
                                "• Mochilas y loncheras\n"
                                "• Material artístico y creativo\n"
                                "• Tecnología educativa\n\n"
                                "¡Todo en un solo lugar!")

    def _ver_lista_grado(self, grado):
        if self.usuario_actual:
            if self.tipo_usuario == 'admin':
                self.abrir_ventana_admin(self.bd)
            else:
                self.abrir_ventana_padres(self.bd, self.id_usuario_actual)
        else:
            self._mostrar_login()

    def _cerrar_sesion(self):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Cerrar sesión")
        msg_box.setText("¿Estás seguro de que quieres cerrar sesión?")
        msg_box.setIcon(QMessageBox.Icon.Question)

        btn_si = msg_box.addButton("Sí", QMessageBox.ButtonRole.YesRole)
        btn_no = msg_box.addButton("No", QMessageBox.ButtonRole.NoRole)

        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
                color: black;
            }
            QMessageBox QLabel {
                color: #1E293B;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background-color: #3B82F6;
                color: white;
                border: 2px solid #1E40AF;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
                min-width: 80px;
                min-height: 35px;
                margin: 5px;
            }
            QMessageBox QPushButton:hover {
                background-color: #2563EB;
                border-color: #1E3A8A;
            }
            QMessageBox QPushButton:pressed {
                background-color: #1E40AF;
            }
        """)

        btn_si.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                border: 2px solid #DC2626;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
                min-width: 80px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #DC2626;
                border-color: #B91C1C;
            }
            QPushButton:pressed {
                background-color: #B91C1C;
            }
        """)

        msg_box.exec()

        if msg_box.clickedButton() == btn_si:
            self.usuario_actual = None
            self.id_usuario_actual = None
            self.tipo_usuario = None

            self._actualizar_ui_sesion()

            if hasattr(self, 'ventana_padres') and self.ventana_padres:
                self.ventana_padres.close()
                self.ventana_padres = None
            if hasattr(self, 'ventana_admin') and self.ventana_admin:
                self.ventana_admin.close()
                self.ventana_admin = None

            QMessageBox.information(self, "Sesión cerrada",
                                    "Has cerrado sesión correctamente.")

    def _actualizar_ui_sesion(self):
        if self.usuario_actual:
            self.btn_login.setVisible(False)
            self.user_widget.setVisible(True)
            self.lbl_usuario.setText(f"👤 {self.usuario_actual}")


            if self.tipo_usuario == 'admin':
                self.btn_perfil.setText("👑 Panel Admin")
            else:
                self.btn_perfil.setText("👤 Mi Perfil")

        else:
            self.btn_login.setVisible(True)
            self.user_widget.setVisible(False)


        self.user_container.update()
        self.user_container.repaint()

    def iniciar_sesion(self, id_usuario, nombre_usuario, tipo_usuario):
        self.id_usuario_actual = id_usuario
        self.usuario_actual = nombre_usuario
        self.tipo_usuario = tipo_usuario
        self._actualizar_ui_sesion()

        QMessageBox.information(self, "Bienvenido",
                                f"¡Hola {nombre_usuario}!\nHas iniciado sesión correctamente.")

    def _ir_a_perfil(self):
        if not self.usuario_actual:
            self._mostrar_login()
            return

        if self.tipo_usuario == 'admin':
            self.abrir_ventana_admin(self.bd)
        else:
            self.abrir_ventana_padres(self.bd, self.id_usuario_actual)

    def _mostrar_login(self):
        self.hide()
        self.ventana_login = VentanaTipoUsuario(ventana_principal=self)
        self.ventana_login.showMaximized()

    def _cerrar_sesion_silenciosa(self):
        self.usuario_actual = None
        self.id_usuario_actual = None
        self.tipo_usuario = None

        self._actualizar_ui_sesion()

        if hasattr(self, 'ventana_padres') and self.ventana_padres:
            self.ventana_padres.close()
            self.ventana_padres = None
        if hasattr(self, 'ventana_admin') and self.ventana_admin:
            self.ventana_admin.close()
            self.ventana_admin = None

    def mostrar_ventana_principal(self):
        if self.ventana_login:
            self.ventana_login.close()
            self.ventana_login = None
        if self.ventana_padres:
            self.ventana_padres.close()
            self.ventana_padres = None
        if self.ventana_admin:
            self.ventana_admin.close()
            self.ventana_admin = None
        if self.ventana_promociones:
            self.ventana_promociones.close()
            self.ventana_promociones = None
        if self.ventana_contacto:
            self.ventana_contacto.close()
            self.ventana_contacto = None

        self.showMaximized()
        self._actualizar_ui_sesion()

    def abrir_ventana_padres(self, bd, id_usuario):
        self.hide()
        self.ventana_padres = VentanaPadres(bd, id_usuario, ventana_principal=self)
        self.ventana_padres.showMaximized()

    def abrir_ventana_admin(self, bd):
        self.hide()
        self.ventana_admin = VentanaAdmin(bd, ventana_principal=self)
        self.ventana_admin.showMaximized()

    def closeEvent(self, event):
        if self.ventana_login:
            self.ventana_login.close()
        if self.ventana_padres:
            self.ventana_padres.close()
        if self.ventana_admin:
            self.ventana_admin.close()
        if self.ventana_promociones:
            self.ventana_promociones.close()
        if self.ventana_contacto:
            self.ventana_contacto.close()

        if self.bd:
            self.bd.cerrar()

        event.accept()

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
    def __init__(self, ventana_principal=None):
        super().__init__()
        self.padres = None
        self.admin = None
        self.ventana_principal = ventana_principal
        self.setWindowTitle("Selecciona tipo de usuario")
        self.showMaximized()
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
        main_layout.setContentsMargins(0, 20, 0, 0)

        header_layout = QHBoxLayout()
        btn_volver = QPushButton("← Volver al Inicio")
        btn_volver.setObjectName("volver")
        btn_volver.clicked.connect(self._volver_al_inicio)
        header_layout.addWidget(btn_volver)
        header_layout.addStretch()

        main_layout.addLayout(header_layout)
        main_layout.addSpacing(20)

        container = QWidget()
        container.setFixedSize(600, 500)
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.setSpacing(25)

        logo_layout = QHBoxLayout()
        logo_label = QLabel("📚")
        logo_label.setStyleSheet("font-size: 48px;")
        titulo_app = QLabel("Librería Escolar ABC")
        titulo_app.setStyleSheet("font-size: 28px; font-weight: bold; color: #1E40AF; margin-left: 15px;")

        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(titulo_app)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        titulo = QLabel("Bienvenido a Librería ABC")
        titulo.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("color: #1E293B; margin-bottom: 15px;")

        subtitulo = QLabel("Selecciona tu tipo de usuario para continuar")
        subtitulo.setFont(QFont("Segoe UI", 14))
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitulo.setStyleSheet("color: #64748B; margin-bottom: 30px;")

        btn_padres = QPushButton("👨‍👩‍👧‍👦 Padres de Familia")
        btn_padres.clicked.connect(self._abrir_padres)

        btn_admin = QPushButton("👨‍💼 Administrador / Empleado")
        btn_admin.clicked.connect(self._abrir_admin)

        container_layout.addLayout(logo_layout)
        container_layout.addSpacing(15)
        container_layout.addWidget(titulo)
        container_layout.addWidget(subtitulo)
        container_layout.addSpacing(10)
        container_layout.addWidget(btn_padres)
        container_layout.addWidget(btn_admin)

        centrado_layout = QHBoxLayout()
        centrado_layout.addStretch()
        centrado_layout.addWidget(container)
        centrado_layout.addStretch()

        main_layout.addLayout(centrado_layout)
        main_layout.addStretch()

        self.setLayout(main_layout)


    def _abrir_padres(self):
        self.hide()
        if self.padres is None:
            self.padres = VentanaLoginPadres(ventana_principal=self.ventana_principal)
        self.padres.showMaximized()

    def _abrir_admin(self):
        self.hide()
        if self.admin is None:
            self.admin = VentanaLoginAdmin(ventana_principal=self.ventana_principal)
        self.admin.showMaximized()

    def _volver_al_inicio(self):
        self.close()
        if self.ventana_principal:
            self.ventana_principal.mostrar_ventana_principal()

    def closeEvent(self, event):
        if self.ventana_principal:
            self.ventana_principal.mostrar_ventana_principal()
        if self.padres:
            self.padres.close()
        if self.admin:
            self.admin.close()
        event.accept()


class VentanaLoginAdmin(QWidget):
    def __init__(self, ventana_principal=None):
        super().__init__()
        self.bd = ConexionBD(DB_FILE)
        self.ventana_principal = ventana_principal
        self.registro = None
        self.admin_principal = None
        self.tipo_usuario = None
        self.setWindowTitle("Iniciar Sesión - Admin/Empleado")
        self.showMaximized()
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
        if not self.bd or not hasattr(self.bd, 'conexion') or not self.bd.conexion:
            QMessageBox.critical(self, "Error", "Error de conexión a la base de datos")
            return

        usuario = self.txt_usuario.text().strip()
        contra = self.txt_contra.text().strip()

        if not usuario or not contra:
            QMessageBox.warning(self, "Error", "Por favor ingresa usuario y contraseña")
            return

        try:
            filas = self.bd.consultar(
                "SELECT id_usuario, nombre, tipo FROM Usuario WHERE usuario=? AND contrasena=? AND tipo='admin'",
                (usuario, contra)
            )
            if filas:
                id_usuario, nombre_usuario, tipo = filas[0]

                if self.ventana_principal:
                    self.ventana_principal.iniciar_sesion(id_usuario, nombre_usuario, tipo)
                    self.ventana_principal.abrir_ventana_admin(self.bd)
                    self.close()
                else:
                    QMessageBox.information(self, "Bienvenido", f"¡Hola {nombre_usuario}!")
                    self.hide()
                    self.admin_principal = VentanaAdmin(self.bd)
                    self.admin_principal.show()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al consultar la base de datos: {str(e)}")

    def _volver(self):
        self.close()
        if self.ventana_principal:
            self.ventana_principal.mostrar_ventana_principal()

    def closeEvent(self, event):
        if self.bd:
            self.bd.cerrar()
        event.accept()


class VentanaLoginPadres(QWidget):
    def __init__(self, ventana_principal=None):
        super().__init__()
        self.bd = ConexionBD(DB_FILE)
        self.ventana_principal = ventana_principal
        self.registro = None
        self.padres_principal = None
        self.tipo_usuario = None
        self.setWindowTitle("Iniciar Sesión - Padres")
        self.showMaximized()
        self._aplicar_estilos_login()
        self._construir_ui_login()

    def _aplicar_estilos_message_box(self, msg_box, *botones):
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #F8FAFC;
                border: 2px solid #E2E8F0;
                border-radius: 10px;
            }
            QMessageBox QLabel {
                color: #1E293B;
                font-size: 14px;
                font-weight: normal;
            }
        """)

        for boton in botones:
            texto = boton.text()
            if texto == "Sí":
                boton.setStyleSheet("""
                    QPushButton {
                        background-color: #EF4444;
                        color: white;
                        border: 2px solid #DC2626;
                        border-radius: 6px;
                        padding: 8px 20px;
                        font-weight: bold;
                        min-width: 80px;
                    }
                    QPushButton:hover { background-color: #DC2626; }
                """)
            elif texto == "No":
                boton.setStyleSheet("""
                    QPushButton {
                        background-color: #6B7280;
                        color: white;
                        border: 2px solid #4B5563;
                        border-radius: 6px;
                        padding: 8px 20px;
                        font-weight: bold;
                        min-width: 80px;
                    }
                    QPushButton:hover { background-color: #4B5563; }
                """)
            elif texto == "OK":
                boton.setStyleSheet("""
                    QPushButton {
                        background-color: #10B981;
                        color: white;
                        border: 2px solid #059669;
                        border-radius: 6px;
                        padding: 8px 20px;
                        font-weight: bold;
                        min-width: 80px;
                    }
                    QPushButton:hover { background-color: #059669; }
                """)

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
        if not self.bd or not hasattr(self.bd, 'conexion') or not self.bd.conexion:
            try:
                self.bd = ConexionBD(DB_FILE)
            except:
                msg_box = QMessageBox()
                msg_box.setWindowTitle("Error")
                msg_box.setText("Error de conexión a la base de datos")
                msg_box.setIcon(QMessageBox.Icon.Critical)
                btn_ok = msg_box.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
                self._aplicar_estilos_message_box(msg_box, btn_ok)
                msg_box.exec()
                return

        usuario = self.txt_usuario.text().strip()
        contra = self.txt_contra.text().strip()

        if not usuario or not contra:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Error")
            msg_box.setText("Por favor ingresa usuario y contraseña")
            msg_box.setIcon(QMessageBox.Icon.Warning)
            btn_ok = msg_box.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
            self._aplicar_estilos_message_box(msg_box, btn_ok)
            msg_box.exec()
            return

        try:
            filas = self.bd.consultar(
                "SELECT id_usuario, nombre, tipo FROM Usuario WHERE usuario=? AND contrasena=? AND tipo='padre'",
                (usuario, contra)
            )
            if filas:
                id_usuario, nombre_usuario, tipo = filas[0]

                if self.ventana_principal:
                    self.ventana_principal.iniciar_sesion(id_usuario, nombre_usuario, tipo)
                    self.ventana_principal.abrir_ventana_padres(self.bd, id_usuario)
                    self.close()
                else:
                    msg_box = QMessageBox()
                    msg_box.setWindowTitle("Bienvenido")
                    msg_box.setText(f"¡Hola {nombre_usuario}!")
                    msg_box.setIcon(QMessageBox.Icon.Information)
                    btn_ok = msg_box.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
                    self._aplicar_estilos_message_box(msg_box, btn_ok)
                    msg_box.exec()

                    self.hide()
                    self.padres_principal = VentanaPadres(self.bd, id_usuario)
                    self.padres_principal.show()

        except Exception as e:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Error")
            msg_box.setText(f"Error al consultar la base de datos: {str(e)}")
            msg_box.setIcon(QMessageBox.Icon.Critical)
            btn_ok = msg_box.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
            self._aplicar_estilos_message_box(msg_box, btn_ok)
            msg_box.exec()

    def _volver(self):
        self.close()
        if self.ventana_principal:
            self.ventana_principal.mostrar_ventana_principal()

    def closeEvent(self, event):
        event.accept()


class VentanaRegistroModerno(QWidget):
    def __init__(self, tipo_usuario="padre", bd=None, ventana_principal=None):
        super().__init__()
        self.tipo_usuario = tipo_usuario
        self.bd = bd if bd else ConexionBD(DB_FILE)
        self.ventana_principal = ventana_principal
        self.ventana_login = None
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
        if not self.bd or not hasattr(self.bd, 'conexion') or not self.bd.conexion:
            QMessageBox.critical(self, "Error", "Error de conexión a la base de datos")
            return

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

    def closeEvent(self, event):
        if self.bd:
            self.bd.cerrar()
        event.accept()


class VentanaPadres(QWidget):
    def __init__(self, bd, id_usuario, ventana_principal=None):
        super().__init__()
        self.bd = bd
        self.id_usuario = id_usuario
        self.ventana_principal = ventana_principal
        self.setWindowTitle("Padres de Familia - Librería ABC")
        self.showMaximized()
        self.lista_seleccionados = []
        self.carrito_compras = []
        self.lista_mis_utiles = None
        self._construir_ui()

    def _construir_ui(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        scroll_panel = QScrollArea()
        scroll_panel.setFixedWidth(300)
        scroll_panel.setWidgetResizable(True)
        scroll_panel.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_panel.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_panel.setStyleSheet("""
            QScrollArea {
                background-color: #1E40AF;
                border: none;
                border-radius: 10px;
                margin: 10px;
            }
            QScrollBar:vertical {
                background-color: #1E3A8A;
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #3B82F6;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #2563EB;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)

        panel_botones = QWidget()
        panel_botones.setStyleSheet("""
            QWidget {
                background-color: #1E40AF;
                border-radius: 10px;
            }
        """)

        layout_botones = QVBoxLayout(panel_botones)
        layout_botones.setContentsMargins(15, 20, 15, 20)
        layout_botones.setSpacing(15)

        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setSpacing(10)

        btn_volver = QPushButton("🏠 Volver al Inicio")
        btn_volver.setStyleSheet("""
            QPushButton {
                background-color: #6B7280;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 15px;
                font-size: 14px;
                font-weight: bold;
                min-height: 45px;
            }
            QPushButton:hover {
                background-color: #4B5563;
            }
        """)
        btn_volver.clicked.connect(self.volver_al_inicio)
        header_layout.addWidget(btn_volver)

        usuario_info = self.bd.consultar("SELECT nombre FROM Usuario WHERE id_usuario=?", (self.id_usuario,))
        nombre_usuario = usuario_info[0][0] if usuario_info else "Usuario"

        lbl_usuario = QLabel(f"👤 {nombre_usuario}")
        lbl_usuario.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                background-color: #1E3A8A;
                border-radius: 8px;
                text-align: center;
            }
        """)
        lbl_usuario.setWordWrap(True)
        header_layout.addWidget(lbl_usuario)

        layout_botones.addWidget(header_widget)

        botones_menu = [
            ("📚 Ver Catálogo", self.mostrar_catalogo),
            ("📝 Mi Lista de Útiles", self.mostrar_listado),
            ("🛒 Carrito de Compras", self.mostrar_carrito),
            ("📋 Listas Predefinidas", self.mostrar_listas_predefinidas),
            ("⚙️ Configuración", self.mostrar_configuracion),
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
                    padding: 15px;
                    font-size: 14px;
                    font-weight: bold;
                    text-align: left;
                    min-height: 50px;
                }
                QPushButton:hover {
                    background-color: #2563EB;
                }
            """)
            btn.clicked.connect(funcion)
            layout_botones.addWidget(btn)

        layout_botones.addStretch()

        scroll_panel.setWidget(panel_botones)
        main_layout.addWidget(scroll_panel)

        self.panel_contenido = QScrollArea()
        self.panel_contenido.setWidgetResizable(True)
        self.panel_contenido.setStyleSheet("""
            QScrollArea { 
                border: none; 
                background-color: #F8FAFC; 
            }
        """)

        self.contenido_widget = QWidget()
        self.contenido_layout = QVBoxLayout(self.contenido_widget)
        self.contenido_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.contenido_layout.setContentsMargins(20, 20, 20, 20)
        self.contenido_layout.setSpacing(15)
        self.panel_contenido.setWidget(self.contenido_widget)

        self.mostrar_bienvenida()

        main_layout.addWidget(self.panel_contenido)

    def _limpiar_panel(self):
        self.lista_mis_utiles = None

        while self.contenido_layout.count():
            item = self.contenido_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def mostrar_bienvenida(self):
        self._limpiar_panel()

        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.setSpacing(20)

        icono = QLabel("📚")
        icono.setStyleSheet("font-size: 100px;")
        icono.setAlignment(Qt.AlignmentFlag.AlignCenter)

        titulo = QLabel("¡Bienvenido a Librería ABC!")
        titulo.setStyleSheet("""
            font-size: 36px; 
            font-weight: bold; 
            color: #1E293B; 
            margin: 20px;
            text-align: center;
        """)
        titulo.setWordWrap(True)

        subtitulo = QLabel("Selecciona una opción del menú lateral para comenzar")
        subtitulo.setStyleSheet("""
            font-size: 18px; 
            color: #64748B; 
            margin: 10px;
            text-align: center;
        """)
        subtitulo.setWordWrap(True)

        welcome_layout.addStretch()
        welcome_layout.addWidget(icono)
        welcome_layout.addWidget(titulo)
        welcome_layout.addWidget(subtitulo)
        welcome_layout.addStretch()

        self.contenido_layout.addWidget(welcome_widget)

    def mostrar_catalogo(self):
        self._limpiar_panel()

        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)

        titulo = QLabel("📚 Catálogo de Productos")
        titulo.setStyleSheet("""
            font-size: 28px; 
            font-weight: bold; 
            color: #1E293B;
        """)

        buscador_widget = QWidget()
        buscador_layout = QHBoxLayout(buscador_widget)
        buscador_layout.setContentsMargins(0, 0, 0, 0)

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("🔍 Buscar productos...")
        self.txt_buscar.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #E2E8F0;
                border-radius: 8px;
                font-size: 14px;
                min-width: 300px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3B82F6;
            }
        """)
        self.txt_buscar.textChanged.connect(self.filtrar_catalogo)

        btn_limpiar_busqueda = QPushButton("Limpiar")
        btn_limpiar_busqueda.setStyleSheet("""
            QPushButton {
                background-color: #6B7280;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 15px;
                font-size: 14px;
                margin-left: 5px;
            }
            QPushButton:hover {
                background-color: #4B5563;
            }
        """)
        btn_limpiar_busqueda.clicked.connect(self.limpiar_busqueda)

        buscador_layout.addWidget(self.txt_buscar)
        buscador_layout.addWidget(btn_limpiar_busqueda)

        header_layout.addWidget(titulo)
        header_layout.addStretch()
        header_layout.addWidget(buscador_widget)

        self.contenido_layout.addWidget(header_widget)

        self.scroll_productos = QScrollArea()
        self.scroll_productos.setWidgetResizable(True)
        self.scroll_productos.setStyleSheet("""
            QScrollArea { 
                border: none; 
                background: transparent;
            }
        """)

        self.widget_productos = QWidget()
        self.layout_productos = QVBoxLayout(self.widget_productos)
        self.layout_productos.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout_productos.setSpacing(20)
        self.layout_productos.setContentsMargins(10, 10, 10, 10)
        self.scroll_productos.setWidget(self.widget_productos)

        self.contenido_layout.addWidget(self.scroll_productos)

        self.cargar_productos()

    def limpiar_busqueda(self):
        self.txt_buscar.clear()
        if hasattr(self, 'productos_completos'):
            self.actualizar_vista_productos(self.productos_completos)

    def cargar_productos(self):
        try:
            if not self.bd or not hasattr(self.bd, 'conexion'):
                raise Exception("No hay conexión a la base de datos")

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
            try:
                msg_box = QMessageBox()
                msg_box.setWindowTitle("Error")
                msg_box.setText(f"No se pudieron cargar los productos:\n\n{str(e)}")
                msg_box.setIcon(QMessageBox.Icon.Critical)
                btn_ok = msg_box.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
                self._aplicar_estilos_message_box(msg_box, btn_ok)
                msg_box.exec()
            except:
                QMessageBox.critical(self, "Error", f"No se pudieron cargar los productos:\n\n{str(e)}")

    def actualizar_vista_productos(self, productos):
        while self.layout_productos.count():
            item = self.layout_productos.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not productos:
            lbl_vacio = QLabel("No se encontraron productos que coincidan con la búsqueda")
            lbl_vacio.setStyleSheet("""
                font-size: 16px; 
                color: #64748B; 
                text-align: center; 
                margin: 50px;
                padding: 20px;
            """)
            lbl_vacio.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout_productos.addWidget(lbl_vacio)
            return

        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(20)
        grid_layout.setContentsMargins(10, 10, 10, 10)

        for i, producto in enumerate(productos):
            card = self.crear_card_producto(producto)
            grid_layout.addWidget(card, i // 3, i % 3)

        self.layout_productos.addWidget(grid_widget)

    def crear_card_producto(self, producto):
        id_producto, nombre, categoria, precio, stock, imagen_blob, tipo_imagen = producto

        card = QWidget()
        card.setFixedSize(280, 350)
        card.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #E2E8F0;
                border-radius: 15px;
                padding: 20px;
            }
            QWidget:hover {
                border-color: #3B82F6;
                background-color: #F8FAFF;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        lbl_imagen = QLabel()
        lbl_imagen.setFixedSize(120, 120)
        lbl_imagen.setStyleSheet("""
            QLabel {
                background-color: #F8FAFC;
                border-radius: 10px;
                qproperty-alignment: 'AlignCenter';
                font-size: 40px;
                border: 1px solid #E2E8F0;
            }
        """)

        try:
            if imagen_blob:
                pixmap = QPixmap()
                if pixmap.loadFromData(imagen_blob):
                    pixmap = pixmap.scaled(110, 110, Qt.AspectRatioMode.KeepAspectRatio,
                                           Qt.TransformationMode.SmoothTransformation)
                    lbl_imagen.setPixmap(pixmap)
                else:
                    lbl_imagen.setText("📦")
            else:
                lbl_imagen.setText("📦")
        except Exception as e:
            print(f"DEBUG: Error cargando imagen: {e}")
            lbl_imagen.setText("📦")

        lbl_nombre = QLabel(nombre)
        lbl_nombre.setStyleSheet("""
            font-size: 16px; 
            font-weight: bold; 
            color: #1E293B;
            margin-top: 5px;
        """)
        lbl_nombre.setWordWrap(True)
        lbl_nombre.setMaximumHeight(40)

        lbl_categoria = QLabel(categoria or "Sin categoría")
        lbl_categoria.setStyleSheet("font-size: 12px; color: #64748B;")

        lbl_precio = QLabel(f"Q{precio:.2f}")
        lbl_precio.setStyleSheet("font-size: 20px; font-weight: bold; color: #059669;")

        lbl_stock = QLabel(f"Stock: {stock}")
        color_stock = "#EF4444" if stock == 0 else "#F59E0B" if stock < 5 else "#10B981"
        lbl_stock.setStyleSheet(f"font-size: 12px; color: {color_stock}; font-weight: bold;")

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        btn_ver = QPushButton("👀 Ver")
        btn_ver.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)
        btn_ver.clicked.connect(lambda: self.ver_detalle_producto(producto))

        btn_agregar = QPushButton("🛒 Agregar")
        btn_agregar.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        btn_agregar.clicked.connect(lambda: self.agregar_al_carrito(producto))
        btn_agregar.setEnabled(stock > 0)

        if stock == 0:
            btn_agregar.setToolTip("Producto sin stock")
            btn_agregar.setStyleSheet("""
                QPushButton {
                    background-color: #9CA3AF;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 12px;
                    font-weight: bold;
                }
            """)

        btn_layout.addWidget(btn_ver)
        btn_layout.addWidget(btn_agregar)

        layout.addWidget(lbl_imagen, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_nombre)
        layout.addWidget(lbl_categoria)
        layout.addWidget(lbl_precio)
        layout.addWidget(lbl_stock)
        layout.addLayout(btn_layout)

        return card

    def filtrar_catalogo(self):
        texto = self.txt_buscar.text().lower().strip()

        if not hasattr(self, 'productos_completos'):
            return

        if not texto:
            self.actualizar_vista_productos(self.productos_completos)
            return

        productos_filtrados = [
            p for p in self.productos_completos
            if texto in p[1].lower() or (p[2] and texto in p[2].lower())
        ]

        self.actualizar_vista_productos(productos_filtrados)

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

    def mostrar_listado(self):
        self._limpiar_panel()

        contenedor_principal = QWidget()
        layout_principal = QVBoxLayout(contenedor_principal)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(20)

        titulo = QLabel("📝 Mi Lista de Útiles Personal")
        titulo.setStyleSheet("font-size: 28px; font-weight: bold; color: #1E293B; margin-bottom: 20px;")
        layout_principal.addWidget(titulo)

        self.lista_mis_utiles = QListWidget()
        self.lista_mis_utiles.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 2px solid #E2E8F0;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                min-height: 300px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #E2E8F0;
            }
            QListWidget::item:selected {
                background-color: #3B82F6;
                color: white;
            }
        """)
        layout_principal.addWidget(self.lista_mis_utiles)

        self.actualizar_lista_utiles()

        contenedor_botones = QWidget()
        contenedor_botones.setMaximumHeight(80)
        layout_botones = QHBoxLayout(contenedor_botones)
        layout_botones.setContentsMargins(0, 10, 0, 10)
        layout_botones.setSpacing(10)

        btn_agregar = QPushButton("➕ Agregar Útil")
        btn_agregar.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 15px;
                font-weight: bold;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        btn_agregar.clicked.connect(self.agregar_util)

        btn_eliminar = QPushButton("🗑️ Eliminar")
        btn_eliminar.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 15px;
                font-weight: bold;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """)
        btn_eliminar.clicked.connect(self.eliminar_util)

        btn_limpiar = QPushButton("🧹 Limpiar")
        btn_limpiar.setStyleSheet("""
            QPushButton {
                background-color: #F59E0B;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 15px;
                font-weight: bold;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #D97706;
            }
        """)
        btn_limpiar.clicked.connect(self.limpiar_lista)

        btn_agregar_carrito = QPushButton("🛒 Agregar al Carrito")
        btn_agregar_carrito.setStyleSheet("""
            QPushButton {
                background-color: #8B5CF6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 15px;
                font-weight: bold;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #7C3AED;
            }
        """)
        btn_agregar_carrito.clicked.connect(self.agregar_lista_al_carrito)

        layout_botones.addWidget(btn_agregar)
        layout_botones.addWidget(btn_eliminar)
        layout_botones.addWidget(btn_limpiar)
        layout_botones.addWidget(btn_agregar_carrito)
        layout_botones.addStretch()

        layout_principal.addWidget(contenedor_botones)

        self.contenido_layout.addWidget(contenedor_principal)

    def agregar_lista_al_carrito(self):
        if not self.lista_seleccionados:
            QMessageBox.warning(self, "Lista vacía", "Tu lista de útiles está vacía.")
            return

        productos_encontrados = []
        productos_no_encontrados = []

        for util in self.lista_seleccionados:
            productos = self.bd.consultar("""
                SELECT p.id_producto, p.nombre, c.nombre as categoria, 
                       p.precio, p.stock, p.imagen, p.tipo_imagen
                FROM Producto p 
                LEFT JOIN Categoria c ON p.id_categoria = c.id_categoria
                WHERE p.nombre LIKE ? AND p.stock > 0
                LIMIT 1
            """, (f"%{util}%",))

            if productos:
                productos_encontrados.append((productos[0], 1))
            else:
                productos_no_encontrados.append(util)

        if not productos_encontrados:
            QMessageBox.warning(self, "No se encontraron productos",
                                "No se encontraron productos en el catálogo que coincidan con tu lista.")
            return

        for producto, cantidad in productos_encontrados:
            encontrado = False
            for i, (prod, cant) in enumerate(self.carrito_compras):
                if prod[0] == producto[0]:
                    self.carrito_compras[i] = (prod, cant + cantidad)
                    encontrado = True
                    break

            if not encontrado:
                self.carrito_compras.append((producto, cantidad))

        mensaje = f"Se agregaron {len(productos_encontrados)} productos al carrito."
        if productos_no_encontrados:
            mensaje += f"\n\nNo se encontraron: {', '.join(productos_no_encontrados)}"

        QMessageBox.information(self, "Lista agregada al carrito", mensaje)

        respuesta = QMessageBox.question(
            self, "Ir al carrito",
            "¿Deseas ver tu carrito de compras?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            self.mostrar_carrito()

    def mostrar_listas_predefinidas(self):
        self._limpiar_panel()

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        titulo = QLabel("📋 Listas de Útiles Predefinidas")
        titulo.setStyleSheet("font-size: 28px; font-weight: bold; color: #1E293B; margin-bottom: 20px;")
        scroll_layout.addWidget(titulo)

        descripcion = QLabel("Selecciona una lista predefinida según el grado escolar:")
        descripcion.setStyleSheet("font-size: 16px; color: #64748B; margin-bottom: 30px;")
        scroll_layout.addWidget(descripcion)

        listas_data = [
            ("1°-3° Primaria", 185.00, [
                "Cuaderno cuadriculado grande",
                "Lápices HB x6",
                "Borradores x2",
                "Caja de colores x12",
                "Tijeras punta roma",
                "Pegamento en barra",
                "Sacapuntas",
                "Block de hojas de dibujo"
            ]),
            ("4°-6° Primaria", 220.00, [
                "Cuadernos profesionales x3",
                "Lápices HB x12",
                "Regla 30cm",
                "Transportador",
                "Compás",
                "Calculadora básica",
                "Diccionario español",
                "Block de hojas milimetradas"
            ]),
            ("1°-3° Secundaria", 285.00, [
                "Cuadernos universitarios x4",
                "Lápices de grafito x8",
                "Calculadora científica",
                "Juego de geometría completo",
                "Diccionario español avanzado",
                "Marcadores fluorescentes x4",
                "Carpeta de argollas",
                "Separadores de cartón"
            ]),
            ("4°-6° Secundaria", 320.00, [
                "Cuadernos especializados x5",
                "Material de dibujo técnico",
                "Calculadora avanzada",
                "Diccionario inglés-español",
                "Block de hojas especiales",
                "Portaminas y minas",
                "Correctores líquidos",
                "Organizador semanal"
            ]),
        ]

        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(20)
        grid_layout.setContentsMargins(10, 10, 10, 10)

        for idx, (grado, precio, utiles) in enumerate(listas_data):
            grupo = self.crear_grupo_lista(grado, precio, utiles)
            grid_layout.addWidget(grupo, idx // 2, idx % 2)

        scroll_layout.addWidget(grid_widget)
        scroll_layout.addStretch()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        self.contenido_layout.addWidget(scroll_area)

    def crear_grupo_lista(self, grado, precio, utiles):
        grupo = QGroupBox(f"🎒 {grado} - Q{precio:.2f}")
        grupo.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                color: #1E40AF;
                border: 2px solid #E2E8F0;
                border-radius: 15px;
                margin: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 5px 10px 5px 10px;
                background-color: #1E40AF;
                color: white;
                border-radius: 8px;
            }
        """)

        layout_grupo = QVBoxLayout()
        layout_grupo.setSpacing(10)
        layout_grupo.setContentsMargins(15, 25, 15, 15)

        for util in utiles:
            lbl_util = QLabel(f"• {util}")
            lbl_util.setStyleSheet("""
                QLabel {
                    font-size: 14px; 
                    color: #374151; 
                    margin: 2px;
                    padding: 2px;
                }
            """)
            lbl_util.setWordWrap(True)
            layout_grupo.addWidget(lbl_util)

        botones_layout = QHBoxLayout()

        btn_agregar_lista = QPushButton("➕ Agregar a Mis Útiles")
        btn_agregar_lista.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)
        btn_agregar_lista.clicked.connect(
            lambda checked, u=utiles: self.agregar_lista_predefinida(u, actualizar_vista=False))

        btn_comprar_lista = QPushButton("🛒 Comprar Lista")
        btn_comprar_lista.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        btn_comprar_lista.clicked.connect(
            lambda checked, u=utiles, p=precio: self.comprar_lista_predefinida(u, p, grado))

        botones_layout.addWidget(btn_agregar_lista)
        botones_layout.addWidget(btn_comprar_lista)
        botones_layout.addStretch()

        layout_grupo.addLayout(botones_layout)
        grupo.setLayout(layout_grupo)

        return grupo

    def comprar_lista_predefinida(self, utiles, precio_total, grado):
        productos_encontrados = []
        productos_no_encontrados = []

        for util in utiles:
            productos = self.bd.consultar("""
                SELECT p.id_producto, p.nombre, c.nombre as categoria, 
                       p.precio, p.stock, p.imagen, p.tipo_imagen
                FROM Producto p 
                LEFT JOIN Categoria c ON p.id_categoria = c.id_categoria
                WHERE p.nombre LIKE ? AND p.stock > 0
                LIMIT 1
            """, (f"%{util}%",))

            if productos:
                productos_encontrados.append((productos[0], 1))
            else:
                productos_no_encontrados.append(util)

        if not productos_encontrados:
            QMessageBox.warning(self, "No se encontraron productos",
                                "No se encontraron productos para esta lista.")
            return

        for producto, cantidad in productos_encontrados:
            encontrado = False
            for i, (prod, cant) in enumerate(self.carrito_compras):
                if prod[0] == producto[0]:
                    self.carrito_compras[i] = (prod, cant + cantidad)
                    encontrado = True
                    break

            if not encontrado:
                self.carrito_compras.append((producto, cantidad))

        mensaje = f"Lista '{grado}' agregada al carrito.\n"
        mensaje += f"Productos agregados: {len(productos_encontrados)}\n"
        mensaje += f"Precio estimado: Q{precio_total:.2f}"

        if productos_no_encontrados:
            mensaje += f"\n\nNo se encontraron: {', '.join(productos_no_encontrados)}"

        QMessageBox.information(self, "Lista agregada al carrito", mensaje)

    def agregar_lista_predefinida(self, utiles, actualizar_vista=True):
        nuevos_utiles = 0
        for util in utiles:
            if util not in self.lista_seleccionados:
                self.lista_seleccionados.append(util)
                nuevos_utiles += 1

        if nuevos_utiles > 0:
            mensaje = f"Se agregaron {nuevos_utiles} nuevos útiles a tu lista."
            if actualizar_vista and self.lista_mis_utiles is not None:
                self.actualizar_lista_utiles()
                QMessageBox.information(self, "Lista agregada", mensaje)
            else:
                QMessageBox.information(self, "Lista agregada",
                                        f"{mensaje}\n\nPuedes ver tu lista actualizada en 'Mi Lista de Útiles'.")
        else:
            QMessageBox.information(self, "Información", "Todos los útiles de esta lista ya están en tu listado.")

    def actualizar_lista_utiles(self):
        if self.lista_mis_utiles is not None:
            try:
                self.lista_mis_utiles.clear()
                for item in self.lista_seleccionados:
                    self.lista_mis_utiles.addItem(item)
            except RuntimeError:
                self.lista_mis_utiles = None

    def agregar_util(self):
        productos = ["Cuaderno", "Lápiz", "Borrador", "Colores", "Mochila", "Regla",
                     "Tijeras", "Pegamento", "Compás", "Transportador", "Calculadora",
                     "Cuaderno cuadriculado", "Lápices HB", "Caja de colores",
                     "Block de hojas", "Diccionario", "Calculadora científica"]

        item, ok = QInputDialog.getItem(
            self, "Agregar útil", "Selecciona un útil:", productos, 0, False
        )

        if ok and item:
            if item not in self.lista_seleccionados:
                self.lista_seleccionados.append(item)
                self.actualizar_lista_utiles()
                QMessageBox.information(self, "Éxito", f"Se agregó '{item}' a tu listado.")

    def eliminar_util(self):
        if self.lista_mis_utiles is None:
            QMessageBox.warning(self, "Error", "La lista no está disponible. Por favor, ve a 'Mi Lista de Útiles'.")
            return

        current_item = self.lista_mis_utiles.currentItem()
        if current_item:
            item_text = current_item.text()
            if item_text in self.lista_seleccionados:
                self.lista_seleccionados.remove(item_text)
                self.actualizar_lista_utiles()
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
                self.actualizar_lista_utiles()
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

        self.tabla_carrito = QTableWidget()
        self.tabla_carrito.setColumnCount(5)
        self.tabla_carrito.setHorizontalHeaderLabels(
            ["Producto", "Precio Unitario", "Cantidad", "Subtotal", "Acciones"])
        self.tabla_carrito.setRowCount(len(self.carrito_compras))

        total = 0
        for i, (producto, cantidad) in enumerate(self.carrito_compras):
            id_producto, nombre, categoria, precio, stock, imagen_blob, tipo_imagen = producto
            subtotal = precio * cantidad
            total += subtotal

            self.tabla_carrito.setItem(i, 0, QTableWidgetItem(nombre))
            self.tabla_carrito.setItem(i, 1, QTableWidgetItem(f"Q{precio:.2f}"))
            self.tabla_carrito.setItem(i, 2, QTableWidgetItem(str(cantidad)))
            self.tabla_carrito.setItem(i, 3, QTableWidgetItem(f"Q{subtotal:.2f}"))

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

            self.tabla_carrito.setCellWidget(i, 4, btn_eliminar)

        self.tabla_carrito.setStyleSheet("""
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
        self.tabla_carrito.horizontalHeader().setStretchLastSection(True)
        self.tabla_carrito.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.contenido_layout.addWidget(self.tabla_carrito)

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

    def mostrar_configuracion(self):
        self._limpiar_panel()

        titulo = QLabel("⚙️ Configuración")
        titulo.setStyleSheet("font-size: 28px; font-weight: bold; color: #1E293B; margin-bottom: 20px;")
        self.contenido_layout.addWidget(titulo)

        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)

        lbl_info = QLabel("Opciones de configuración del usuario")
        lbl_info.setStyleSheet("font-size: 16px; color: #64748B;")
        info_layout.addWidget(lbl_info)

        self.contenido_layout.addWidget(info_widget)

    def volver_al_inicio(self):
        if self.ventana_principal:
            self.ventana_principal.show()
            self.ventana_principal.raise_()
            self.ventana_principal.activateWindow()

        self.hide()

    def _aplicar_estilos_message_box(self, msg_box, *botones):
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #F8FAFC;
                border: 2px solid #E2E8F0;
                border-radius: 10px;
            }
            QMessageBox QLabel {
                color: #1E293B;
                font-size: 14px;
                font-weight: normal;
            }
        """)

        for boton in botones:
            texto = boton.text()
            if texto == "Sí":
                boton.setStyleSheet("""
                    QPushButton {
                        background-color: #EF4444;
                        color: white;
                        border: 2px solid #DC2626;
                        border-radius: 6px;
                        padding: 8px 20px;
                        font-weight: bold;
                        min-width: 80px;
                    }
                    QPushButton:hover { background-color: #DC2626; }
                """)
            elif texto == "No":
                boton.setStyleSheet("""
                    QPushButton {
                        background-color: #6B7280;
                        color: white;
                        border: 2px solid #4B5563;
                        border-radius: 6px;
                        padding: 8px 20px;
                        font-weight: bold;
                        min-width: 80px;
                    }
                    QPushButton:hover { background-color: #4B5563; }
                """)
            elif texto == "OK":
                boton.setStyleSheet("""
                    QPushButton {
                        background-color: #10B981;
                        color: white;
                        border: 2px solid #059669;
                        border-radius: 6px;
                        padding: 8px 20px;
                        font-weight: bold;
                        min-width: 80px;
                    }
                    QPushButton:hover { background-color: #059669; }
                """)

    def cerrar_sesion(self):
        msg_box_pregunta = QMessageBox()
        msg_box_pregunta.setWindowTitle("Cerrar sesión")
        msg_box_pregunta.setText("¿Estás seguro de que quieres cerrar sesión?")
        msg_box_pregunta.setIcon(QMessageBox.Icon.Question)
        btn_si = msg_box_pregunta.addButton("Sí", QMessageBox.ButtonRole.YesRole)
        btn_no = msg_box_pregunta.addButton("No", QMessageBox.ButtonRole.NoRole)
        self._aplicar_estilos_message_box(msg_box_pregunta, btn_si, btn_no)
        msg_box_pregunta.exec()

        if msg_box_pregunta.clickedButton() == btn_si:
            self.carrito_compras.clear()
            self.lista_seleccionados.clear()

            if self.ventana_principal:
                self.ventana_principal._cerrar_sesion_silenciosa()

            self.close()

    def closeEvent(self, event):
        if self.ventana_principal and not self.ventana_principal.isVisible():
            self.ventana_principal.show()
        event.accept()


class VentanaAdmin(QWidget):
    def __init__(self, bd, ventana_principal=None):
        super().__init__()
        self.bd = bd
        self.ventana_principal = ventana_principal
        self.mostrar_login = None
        self.setWindowTitle("Administrador - Librería ABC")
        self.showMaximized()
        self._aplicar_estilos()
        self._construir_ui()

    def _aplicar_estilos(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #F8FAFC;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: #1E40AF;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 14px;
                font-weight: bold;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #1E3A8A;
            }
            QPushButton:disabled {
                background-color: #9CA3AF;
                color: #6B7280;
            }
            QPushButton#peligro {
                background-color: #DC2626;
            }
            QPushButton#peligro:hover {
                background-color: #B91C1C;
            }
            QPushButton#secundario {
                background-color: #6B7280;
            }
            QPushButton#secundario:hover {
                background-color: #4B5563;
            }
            QPushButton#success {
                background-color: #059669;
            }
            QPushButton#success:hover {
                background-color: #047857;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: white;
                border: 2px solid #E2E8F0;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                margin: 2px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border-color: #3B82F6;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                gridline-color: #E2E8F0;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F1F5F9;
            }
            QTableWidget::item:selected {
                background-color: #DBEAFE;
                color: #1E40AF;
            }
            QHeaderView::section {
                background-color: #1E40AF;
                color: white;
                font-weight: bold;
                padding: 12px 8px;
                border: none;
                font-size: 13px;
            }
            QTabWidget::pane {
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #F1F5F9;
                color: #64748B;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #1E40AF;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #E2E8F0;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                color: #1E293B;
                border: 2px solid #E2E8F0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 5px 10px;
                background-color: #1E40AF;
                color: white;
                border-radius: 4px;
            }
            QLabel#titulo {
                font-size: 28px;
                font-weight: bold;
                color: #1E293B;
                padding: 10px;
            }
            QLabel#subtitulo {
                font-size: 16px;
                color: #64748B;
                padding: 5px;
            }
        """)

    def _construir_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        header_layout = QHBoxLayout()

        logo_layout = QHBoxLayout()
        logo_label = QLabel("📊")
        logo_label.setStyleSheet("font-size: 24px;")
        titulo = QLabel("Panel de Administración")
        titulo.setObjectName("titulo")

        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(titulo)

        header_layout.addLayout(logo_layout)
        header_layout.addStretch()

        btn_volver = QPushButton("🏠 Volver al Inicio")
        btn_volver.setObjectName("secundario")
        btn_volver.clicked.connect(self.volver_al_inicio)

        btn_cerrar_sesion = QPushButton("🚪 Cerrar Sesión")
        btn_cerrar_sesion.setObjectName("peligro")
        btn_cerrar_sesion.clicked.connect(self._abrir_login)

        header_layout.addWidget(btn_volver)
        header_layout.addWidget(btn_cerrar_sesion)

        main_layout.addLayout(header_layout)

        h_layout = QHBoxLayout()
        main_layout.addLayout(h_layout)

        nav_widget = QWidget()
        nav_widget.setFixedWidth(280)
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(10, 10, 10, 10)

        lbl_gestion = QLabel("Gestión del Sistema")
        lbl_gestion.setStyleSheet("font-size: 16px; font-weight: bold; color: #1E40AF; margin: 10px 0px;")
        nav_layout.addWidget(lbl_gestion)

        botones_gestion = [
            ("📦 Gestión de Inventario", self._mostrar_gestion_inventario),
            ("📊 Dashboard", self._mostrar_dashboard),
            ("👥 Gestión de Usuarios", self._mostrar_gestion_usuarios),
            ("💰 Ventas y Compras", self._mostrar_ventas_compras),
        ]

        for texto, funcion in botones_gestion:
            btn = QPushButton(texto)
            btn.setFixedHeight(45)
            btn.clicked.connect(funcion)
            nav_layout.addWidget(btn)

        nav_layout.addSpacing(20)

        lbl_acciones = QLabel("Acciones Rápidas")
        lbl_acciones.setStyleSheet("font-size: 16px; font-weight: bold; color: #1E40AF; margin: 10px 0px;")
        nav_layout.addWidget(lbl_acciones)

        botones_rapidos = [
            ("➕ Agregar Producto", lambda: self._cambiar_pantalla("producto")),
            ("🆕 Agregar Productos Ejemplo", self._agregar_productos_ejemplo),
            ("📋 Reporte de Stock", self._generar_reporte_stock),
        ]

        for texto, funcion in botones_rapidos:
            btn = QPushButton(texto)
            btn.setFixedHeight(40)
            btn.clicked.connect(funcion)
            nav_layout.addWidget(btn)

        nav_layout.addStretch()
        h_layout.addWidget(nav_widget)

        self.stacked_layout = QStackedLayout()
        h_layout.addLayout(self.stacked_layout)

        self._inicializar_pantallas()

        self._mostrar_dashboard()

    def _inicializar_pantallas(self):
        self.pantallas = {
            "categoria": PantallaAgregarCategoria(self.bd),
            "producto": PantallaAgregarProducto(self.bd),
            "cliente": PantallaAgregarCliente(self.bd),
            "empleado": PantallaAgregarEmpleado(self.bd),
            "proveedor": PantallaAgregarProveedor(self.bd),
            "ventas": PantallaNuevaVenta(self.bd),
            "compra": PantallaNuevaCompra(self.bd),
            "listas": PantallaCrearLista(self.bd),
            "inventario": self._crear_pantalla_inventario(),
            "dashboard": self._crear_pantalla_dashboard(),
            "usuarios": self._crear_pantalla_usuarios(),
            "ventas_compras": self._crear_pantalla_ventas_compras(),
        }

        for widget in self.pantallas.values():
            self.stacked_layout.addWidget(widget)

    def _crear_pantalla_inventario(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)

        header_layout = QHBoxLayout()
        titulo = QLabel("📦 Gestión de Inventario")
        titulo.setObjectName("titulo")
        header_layout.addWidget(titulo)
        header_layout.addStretch()

        btn_actualizar = QPushButton("🔄 Actualizar")
        btn_actualizar.clicked.connect(self._actualizar_tabla_inventario)
        header_layout.addWidget(btn_actualizar)

        layout.addLayout(header_layout)

        controles_layout = QHBoxLayout()

        self.buscar_inventario = QLineEdit()
        self.buscar_inventario.setPlaceholderText("🔍 Buscar productos...")
        self.buscar_inventario.textChanged.connect(self._filtrar_inventario)

        self.combo_categoria = QComboBox()
        self.combo_categoria.addItem("Todas las categorías")
        self._cargar_categorias_combo()
        self.combo_categoria.currentTextChanged.connect(self._filtrar_inventario)

        controles_layout.addWidget(QLabel("Buscar:"))
        controles_layout.addWidget(self.buscar_inventario)
        controles_layout.addWidget(QLabel("Categoría:"))
        controles_layout.addWidget(self.combo_categoria)
        controles_layout.addStretch()

        layout.addLayout(controles_layout)

        self.tabla_inventario = QTableWidget()
        self.tabla_inventario.setColumnCount(7)
        self.tabla_inventario.setHorizontalHeaderLabels([
            "ID", "Nombre", "Categoría", "Precio", "Stock", "Stock Mínimo", "Acciones"
        ])

        self.tabla_inventario.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_inventario.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_inventario.verticalHeader().setVisible(False)

        header = self.tabla_inventario.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.tabla_inventario)

        botones_layout = QHBoxLayout()

        btn_agregar = QPushButton("➕ Agregar Producto")
        btn_agregar.clicked.connect(lambda: self._cambiar_pantalla("producto"))

        btn_editar = QPushButton("✏️ Editar Seleccionado")
        btn_editar.clicked.connect(self._editar_producto)

        btn_eliminar = QPushButton("🗑️ Eliminar Seleccionado")
        btn_eliminar.setObjectName("peligro")
        btn_eliminar.clicked.connect(self._eliminar_producto)

        btn_exportar = QPushButton("📊 Exportar Reporte")
        btn_exportar.setObjectName("success")
        btn_exportar.clicked.connect(self._exportar_inventario)

        botones_layout.addWidget(btn_agregar)
        botones_layout.addWidget(btn_editar)
        botones_layout.addWidget(btn_eliminar)
        botones_layout.addStretch()
        botones_layout.addWidget(btn_exportar)

        layout.addLayout(botones_layout)

        self._actualizar_tabla_inventario()

        return widget

    def _crear_pantalla_dashboard(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)

        titulo = QLabel("📊 Dashboard - Resumen del Sistema")
        titulo.setObjectName("titulo")
        layout.addWidget(titulo)

        resumen_layout = QHBoxLayout()

        metricas = [
            ("📦 Total Productos", "0", "#3B82F6"),
            ("💰 Ventas Hoy", "Q 0.00", "#10B981"),
            ("👥 Clientes Registrados", "0", "#8B5CF6"),
            ("⚠️ Stock Bajo", "0", "#F59E0B")
        ]

        for texto, valor, color in metricas:
            card = self._crear_tarjeta_metrica(texto, valor, color)
            resumen_layout.addWidget(card)

        layout.addLayout(resumen_layout)

        tab_widget = QTabWidget()

        widget_stock = QWidget()
        layout_stock = QVBoxLayout(widget_stock)

        self.tabla_stock_bajo = QTableWidget()
        self.tabla_stock_bajo.setColumnCount(4)
        self.tabla_stock_bajo.setHorizontalHeaderLabels(["Producto", "Stock Actual", "Stock Mínimo", "Diferencia"])
        layout_stock.addWidget(self.tabla_stock_bajo)

        tab_widget.addTab(widget_stock, "📉 Stock Bajo")

        widget_ventas = QWidget()
        layout_ventas = QVBoxLayout(widget_ventas)

        self.tabla_ventas_recientes = QTableWidget()
        self.tabla_ventas_recientes.setColumnCount(4)
        self.tabla_ventas_recientes.setHorizontalHeaderLabels(["Fecha", "Cliente", "Productos", "Total"])
        layout_ventas.addWidget(self.tabla_ventas_recientes)

        tab_widget.addTab(widget_ventas, "💰 Ventas Recientes")

        layout.addWidget(tab_widget)

        self._actualizar_dashboard()

        return widget

    def _crear_tarjeta_metrica(self, titulo, valor, color):
        card = QWidget()
        card.setFixedSize(200, 100)
        card.setStyleSheet(f"""
            QWidget {{
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 15px;
            }}
        """)

        layout = QVBoxLayout(card)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("font-size: 14px; color: #64748B;")

        lbl_valor = QLabel(valor)
        lbl_valor.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color};")

        layout.addWidget(lbl_titulo)
        layout.addWidget(lbl_valor)
        layout.addStretch()

        return card

    def _crear_pantalla_usuarios(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        titulo = QLabel("👥 Gestión de Usuarios")
        titulo.setObjectName("titulo")
        layout.addWidget(titulo)

        label_info = QLabel("Funcionalidad en desarrollo...")
        label_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label_info)

        return widget

    def _crear_pantalla_ventas_compras(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        titulo = QLabel("💰 Ventas y Compras")
        titulo.setObjectName("titulo")
        layout.addWidget(titulo)

        tab_widget = QTabWidget()

        widget_ventas = QWidget()
        layout_ventas = QVBoxLayout(widget_ventas)
        btn_ventas = QPushButton("Nueva Venta")
        btn_ventas.clicked.connect(lambda: self._cambiar_pantalla("ventas"))
        layout_ventas.addWidget(btn_ventas)
        tab_widget.addTab(widget_ventas, "🛒 Ventas")

        widget_compras = QWidget()
        layout_compras = QVBoxLayout(widget_compras)
        btn_compras = QPushButton("Nueva Compra")
        btn_compras.clicked.connect(lambda: self._cambiar_pantalla("compra"))
        layout_compras.addWidget(btn_compras)
        tab_widget.addTab(widget_compras, "📥 Compras")

        layout.addWidget(tab_widget)

        return widget

    def _actualizar_tabla_inventario(self):
        try:
            query = """
                SELECT p.id_producto, p.nombre, c.nombre as categoria, 
                       p.precio, p.stock, p.limite_stock 
                FROM Producto p 
                LEFT JOIN Categoria c ON p.id_categoria = c.id_categoria
                ORDER BY p.nombre
            """
            productos = self.bd.consultar(query)

            self.tabla_inventario.setRowCount(len(productos))

            for fila, producto in enumerate(productos):
                id_producto, nombre, categoria, precio, stock, limite_stock = producto

                self.tabla_inventario.setItem(fila, 0, QTableWidgetItem(str(id_producto)))
                self.tabla_inventario.setItem(fila, 1, QTableWidgetItem(nombre))
                self.tabla_inventario.setItem(fila, 2, QTableWidgetItem(categoria or "Sin categoría"))
                self.tabla_inventario.setItem(fila, 3, QTableWidgetItem(f"Q{precio:.2f}"))
                self.tabla_inventario.setItem(fila, 4, QTableWidgetItem(str(stock)))
                self.tabla_inventario.setItem(fila, 5, QTableWidgetItem(str(limite_stock or "-")))

                widget_acciones = QWidget()
                layout_acciones = QHBoxLayout(widget_acciones)
                layout_acciones.setContentsMargins(2, 2, 2, 2)

                btn_editar = QPushButton("✏️")
                btn_editar.setFixedSize(30, 25)
                btn_editar.setToolTip("Editar producto")
                btn_editar.clicked.connect(lambda checked, id=id_producto: self._editar_producto_id(id))

                btn_eliminar = QPushButton("🗑️")
                btn_eliminar.setFixedSize(30, 25)
                btn_eliminar.setObjectName("peligro")
                btn_eliminar.setToolTip("Eliminar producto")
                btn_eliminar.clicked.connect(
                    lambda checked, id=id_producto, nom=nombre: self._eliminar_producto_id(id, nom))

                layout_acciones.addWidget(btn_editar)
                layout_acciones.addWidget(btn_eliminar)
                layout_acciones.addStretch()

                self.tabla_inventario.setCellWidget(fila, 6, widget_acciones)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el inventario: {str(e)}")
    def _filtrar_inventario(self):
        texto_busqueda = self.buscar_inventario.text().lower()
        categoria_seleccionada = self.combo_categoria.currentText()

        for fila in range(self.tabla_inventario.rowCount()):
            mostrar_fila = True

            if texto_busqueda:
                nombre = self.tabla_inventario.item(fila, 1).text().lower()
                categoria = self.tabla_inventario.item(fila, 2).text().lower()
                if texto_busqueda not in nombre and texto_busqueda not in categoria:
                    mostrar_fila = False

            if categoria_seleccionada != "Todas las categorías":
                categoria = self.tabla_inventario.item(fila, 2).text()
                if categoria != categoria_seleccionada:
                    mostrar_fila = False

            self.tabla_inventario.setRowHidden(fila, not mostrar_fila)

    def _cargar_categorias_combo(self):
        try:
            categorias = self.bd.consultar("SELECT nombre FROM Categoria ORDER BY nombre")
            for categoria in categorias:
                self.combo_categoria.addItem(categoria[0])
        except Exception as e:
            print(f"Error al cargar categorías: {e}")

    def _editar_producto(self):
        fila_seleccionada = self.tabla_inventario.currentRow()
        if fila_seleccionada >= 0:
            id_producto = int(self.tabla_inventario.item(fila_seleccionada, 0).text())
            self._editar_producto_id(id_producto)
        else:
            QMessageBox.warning(self, "Selección requerida", "Por favor selecciona un producto para editar.")

    def _editar_producto_id(self, id_producto):

        QMessageBox.information(self, "Editar Producto",
                                f"Funcionalidad de edición para el producto ID: {id_producto}\n\n"
                                "Esta característica estará disponible en la próxima actualización.")

    def _eliminar_producto(self):
        fila_seleccionada = self.tabla_inventario.currentRow()
        if fila_seleccionada >= 0:
            id_producto = int(self.tabla_inventario.item(fila_seleccionada, 0).text())
            nombre_producto = self.tabla_inventario.item(fila_seleccionada, 1).text()
            self._eliminar_producto_id(id_producto, nombre_producto)
        else:
            QMessageBox.warning(self, "Selección requerida", "Por favor selecciona un producto para eliminar.")
    def _eliminar_producto_id(self, id_producto, nombre_producto):
        respuesta = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Estás seguro de que quieres eliminar el producto:\n\n\"{nombre_producto}\"?\n\nEsta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            try:
                self.bd.ejecutar("DELETE FROM Producto WHERE id_producto = ?", (id_producto,))
                QMessageBox.information(self, "Éxito", "Producto eliminado correctamente.")
                self._actualizar_tabla_inventario()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar el producto: {str(e)}")

    def _exportar_inventario(self):
        QMessageBox.information(self, "Exportar", "Funcionalidad de exportación en desarrollo.")

    def _actualizar_dashboard(self):
        try:
            total_productos = self.bd.consultar("SELECT COUNT(*) FROM Producto")[0][0]
            total_clientes = self.bd.consultar("SELECT COUNT(*) FROM Cliente")[0][0]
            pass

        except Exception as e:
            print(f"Error al actualizar dashboard: {e}")

    def _mostrar_gestion_inventario(self):
        self._cambiar_pantalla("inventario")

    def _mostrar_dashboard(self):
        self._cambiar_pantalla("dashboard")

    def _mostrar_gestion_usuarios(self):
        self._cambiar_pantalla("usuarios")

    def _mostrar_ventas_compras(self):
        self._cambiar_pantalla("ventas_compras")

    def _cambiar_pantalla(self, key):
        widget = self.pantallas.get(key)
        if widget:
            self.stacked_layout.setCurrentWidget(widget)

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

    def _generar_reporte_stock(self):
        QMessageBox.information(self, "Reporte de Stock", "Generando reporte de stock...")

    def volver_al_inicio(self):
        self.close()
        if self.ventana_principal:
            self.ventana_principal.mostrar_ventana_principal()

    def _abrir_login(self):
        self.volver_al_inicio()

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


class VentanaPromociones(QWidget):
    def __init__(self, ventana_principal=None):
        super().__init__()
        self.ventana_principal = ventana_principal
        self.setWindowTitle("Promociones Especiales - Librería ABC")
        self._aplicar_estilos()
        self._construir_ui()
        self.showMaximized()

    def _aplicar_estilos(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #F8FAFC;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: #1E40AF;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
                margin: 5px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #1E3A8A;
            }
            QPushButton#secundario {
                background-color: #6B7280;
            }
            QPushButton#secundario:hover {
                background-color: #4B5563;
            }
            QPushButton#oferta {
                background-color: #DC2626;
                font-size: 16px;
                padding: 15px 25px;
                min-height: 50px;
            }
            QPushButton#oferta:hover {
                background-color: #B91C1C;
            }
            QPushButton#copiar {
                min-height: 40px;
                font-size: 14px;
            }
            QLabel#titulo {
                font-size: 32px;
                font-weight: bold;
                color: #1E293B;
            }
            QLabel#subtitulo {
                font-size: 18px;
                color: #64748B;
            }
            QGroupBox {
                background-color: white;
                border: 2px solid #E2E8F0;
                border-radius: 12px;
                margin: 15px;
                padding: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 8px 15px;
                background-color: #1E40AF;
                color: white;
                border-radius: 6px;
                font-weight: bold;
                font-size: 16px;
            }
        """)

    def _construir_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        header_layout = QHBoxLayout()

        btn_volver = QPushButton("← Volver al Inicio")
        btn_volver.setObjectName("secundario")
        btn_volver.clicked.connect(self._volver_al_inicio)
        btn_volver.setFixedHeight(45)
        btn_volver.setMinimumWidth(180)

        titulo = QLabel("🎉 Promociones Especiales")
        titulo.setObjectName("titulo")

        header_layout.addWidget(btn_volver)
        header_layout.addStretch()
        header_layout.addWidget(titulo)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        subtitulo = QLabel("Descubre nuestras increíbles ofertas y descuentos exclusivos")
        subtitulo.setObjectName("subtitulo")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitulo.setWordWrap(True)
        layout.addWidget(subtitulo)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #F1F5F9;
                width: 15px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #CBD5E1;
                border-radius: 7px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94A3B8;
            }
        """)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(20)
        scroll_layout.setContentsMargins(10, 10, 10, 10)

        promociones = [
            {
                "titulo": "🔥 OFERTA RELÁMPAGO",
                "descripcion": "20% DE DESCUENTO EN MOCHILAS",
                "detalles": "Válido solo hoy en toda nuestra línea de mochilas escolares y deportivas. Perfecta para el regreso a clases.",
                "codigo": "MOCHILA20",
                "color": "#DC2626",
                "icono": "🎒",
                "validez": "Válido hasta: Hoy"
            },
            {
                "titulo": "📚 PACK ESCOLAR COMPLETO",
                "descripcion": "15% OFF EN PACKS COMPLETOS",
                "detalles": "Incluye cuadernos, lápices, colores, regla, tijeras, pegamento y más. Todo lo necesario para el colegio en un solo pack.",
                "codigo": "PACK15",
                "color": "#059669",
                "icono": "📦",
                "validez": "Válido hasta: 30 días"
            },
            {
                "titulo": "🎁 2x1 EN CUADERNOS",
                "descripcion": "LLEVATE 2 PAGANDO 1",
                "detalles": "Válido en cuadernos cuadriculados y rayados de 100 hojas. No acumulable con otras promociones.",
                "codigo": "2X1CUAD",
                "color": "#7C3AED",
                "icono": "📓",
                "validez": "Válido hasta: Fin de mes"
            },
            {
                "titulo": "💳 10% DESCUENTO ADICIONAL",
                "descripcion": "PAGANDO CON TARJETA",
                "detalles": "Acumulable con otras promociones. Válido en todas las compras con tarjeta de crédito o débito.",
                "codigo": "TARJETA10",
                "color": "#0EA5E9",
                "icono": "💳",
                "validez": "Permanente"
            },
            {
                "titulo": "🚚 ENVÍO GRATIS",
                "descripcion": "EN COMPRAS MAYORES A Q200",
                "detalles": "Recibe tu pedido sin costo adicional en toda el área metropolitana. Entrega en 24-48 horas.",
                "codigo": "ENVIOGRATIS",
                "color": "#F59E0B",
                "icono": "🚚",
                "validez": "Permanente"
            },
            {
                "titulo": "⭐ CLIENTE FRECUENTE",
                "descripcion": "ACUMULA PUNTOS POR COMPRA",
                "detalles": "Por cada Q100 gastados, acumulas 10 puntos. Canjea por descuentos exclusivos y productos gratis.",
                "codigo": "PUNTOSABC",
                "color": "#8B5CF6",
                "icono": "⭐",
                "validez": "Permanente"
            }
        ]

        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)
        grid_layout.setContentsMargins(10, 10, 10, 10)

        for i, promo in enumerate(promociones):
            card = self._crear_tarjeta_promocion(promo)
            row = i // 2
            col = i % 2
            grid_layout.addWidget(card, row, col)

        scroll_layout.addLayout(grid_layout)
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        btn_layout = QHBoxLayout()
        btn_contacto = QPushButton("📞 Contactar para Más Información")
        btn_contacto.setObjectName("oferta")
        btn_contacto.setFixedHeight(55)
        btn_contacto.setMinimumWidth(300)
        btn_contacto.clicked.connect(self._abrir_contacto)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_contacto)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def _crear_tarjeta_promocion(self, promocion):
        card = QGroupBox(f"{promocion['icono']} {promocion['titulo']}")
        card.setMinimumHeight(300)
        card.setStyleSheet(f"""
            QGroupBox {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 {promocion['color']}15, stop:1 white);
                border: 2px solid {promocion['color']}40;
            }}
            QGroupBox::title {{
                background-color: {promocion['color']};
                color: white;
                font-size: 14px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(12)

        lbl_descripcion = QLabel(promocion['descripcion'])
        lbl_descripcion.setStyleSheet(f"""
            font-size: 20px; 
            font-weight: bold; 
            color: {promocion['color']};
            margin: 10px 0px;
            line-height: 1.3;
        """)
        lbl_descripcion.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_descripcion.setWordWrap(True)
        lbl_descripcion.setMinimumHeight(50)
        layout.addWidget(lbl_descripcion)

        lbl_detalles = QLabel(promocion['detalles'])
        lbl_detalles.setStyleSheet("""
            font-size: 14px; 
            color: #64748B; 
            margin: 8px 0px; 
            line-height: 1.4;
        """)
        lbl_detalles.setWordWrap(True)
        lbl_detalles.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_detalles.setMinimumHeight(60)
        layout.addWidget(lbl_detalles)

        lbl_validez = QLabel(promocion['validez'])
        lbl_validez.setStyleSheet("""
            font-size: 12px; 
            font-weight: bold; 
            color: #6B7280; 
            margin: 5px 0px;
        """)
        lbl_validez.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_validez.setWordWrap(True)
        layout.addWidget(lbl_validez)

        layout_codigo = QHBoxLayout()

        lbl_codigo = QLabel(promocion['codigo'])
        lbl_codigo.setStyleSheet(f"""
            font-size: 18px; 
            font-weight: bold; 
            color: {promocion['color']};
            background-color: {promocion['color']}15;
            padding: 10px 20px;
            border-radius: 6px;
            border: 2px dashed {promocion['color']};
            min-width: 120px;
        """)
        lbl_codigo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_codigo.setMinimumWidth(120)

        layout_codigo.addStretch()
        layout_codigo.addWidget(lbl_codigo)
        layout_codigo.addStretch()

        layout.addLayout(layout_codigo)

        btn_copiar_layout = QHBoxLayout()
        btn_copiar = QPushButton("📋 Copiar Código")
        btn_copiar.setObjectName("copiar")
        btn_copiar.setFixedHeight(40)
        btn_copiar.setMinimumWidth(150)
        btn_copiar.setStyleSheet(f"""
            QPushButton {{
                background-color: {promocion['color']};
                color: white;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self._oscurecer_color(promocion['color'])};
            }}
        """)
        btn_copiar.clicked.connect(lambda: self._copiar_codigo(promocion['codigo']))

        btn_copiar_layout.addStretch()
        btn_copiar_layout.addWidget(btn_copiar)
        btn_copiar_layout.addStretch()

        layout.addLayout(btn_copiar_layout)

        return card

    def _oscurecer_color(self, color_hex):
        import re
        match = re.search(r'^#([A-Fa-f0-9]{6})$', color_hex)
        if match:
            hex_color = match.group(1)
            r = max(0, int(hex_color[0:2], 16) - 51)
            g = max(0, int(hex_color[2:4], 16) - 51)
            b = max(0, int(hex_color[4:6], 16) - 51)
            return f"#{r:02x}{g:02x}{b:02x}"
        return color_hex

    def _copiar_codigo(self, codigo):
        QApplication.clipboard().setText(codigo)
        QMessageBox.information(self, "Código Copiado",
                                f"El código '{codigo}' ha sido copiado al portapapeles.\n\n¡Úsalo al realizar tu compra!")

    def _abrir_contacto(self):
        self.ventana_contacto = VentanaContacto(self.ventana_principal)
        self.ventana_contacto.showMaximized()

    def _volver_al_inicio(self):
        self.close()
        if self.ventana_principal:
            self.ventana_principal.showMaximized()


class VentanaContacto(QWidget):
    def __init__(self, ventana_principal=None):
        super().__init__()
        self.ventana_principal = ventana_principal
        self.setWindowTitle("Contacto - Librería ABC")
        self._aplicar_estilos()
        self._construir_ui()
        self.showMaximized()

    def _aplicar_estilos(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #F8FAFC;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: #1E40AF;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
                margin: 5px;
                min-height: 45px;
            }
            QPushButton:hover {
                background-color: #1E3A8A;
            }
            QPushButton#secundario {
                background-color: #6B7280;
                min-width: 120px;
            }
            QPushButton#secundario:hover {
                background-color: #4B5563;
            }
            QPushButton#whatsapp {
                background-color: #25D366;
                font-size: 16px;
                padding: 15px 25px;
                min-height: 50px;
                min-width: 220px;
            }
            QPushButton#whatsapp:hover {
                background-color: #128C7E;
            }
            QPushButton#llamar {
                min-width: 150px;
                min-height: 50px;
            }
            QPushButton#email {
                min-width: 150px;
                min-height: 50px;
            }
            QLabel#titulo {
                font-size: 32px;
                font-weight: bold;
                color: #1E293B;
            }
            QLabel#subtitulo {
                font-size: 18px;
                color: #64748B;
            }
            QFrame#info_card {
                background-color: white;
                border: 2px solid #E2E8F0;
                border-radius: 12px;
                padding: 25px;
            }
        """)

    def _construir_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        header_layout = QHBoxLayout()

        btn_volver = QPushButton("← Volver")
        btn_volver.setObjectName("secundario")
        btn_volver.setFixedHeight(45)
        btn_volver.setMinimumWidth(120)
        btn_volver.clicked.connect(self._volver_al_inicio)

        titulo = QLabel("📞 Contacto - Librería ABC")
        titulo.setObjectName("titulo")

        header_layout.addWidget(btn_volver)
        header_layout.addStretch()
        header_layout.addWidget(titulo)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        subtitulo = QLabel("Estamos aquí para ayudarte. Contáctanos por cualquier consulta o solicitud")
        subtitulo.setObjectName("subtitulo")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitulo.setWordWrap(True)
        layout.addWidget(subtitulo)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #F1F5F9;
                width: 15px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #CBD5E1;
                border-radius: 7px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94A3B8;
            }
        """)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(20)
        scroll_layout.setContentsMargins(10, 10, 10, 10)

        info_frame = QFrame()
        info_frame.setObjectName("info_card")
        info_layout = QVBoxLayout(info_frame)

        info_items = [
            ("🏢", "Dirección",
             "7a Avenida 12-34, Zona 1\nCiudad de Guatemala, Guatemala\n\n📍 Fácil acceso con estacionamiento disponible"),
            ("📞", "Teléfonos",
             "Línea Principal: (502) 1234-5678\nLínea de Ventas: (502) 8765-4321\nLínea de Soporte: (502) 5555-9999"),
            ("📧", "Email",
             "Información General: info@libreriaabc.com\nVentas y Pedidos: ventas@libreriaabc.com\nSoporte Técnico: soporte@libreriaabc.com"),
            ("🕒", "Horario de Atención",
             "Lunes a Viernes: 8:00 AM - 6:00 PM\nSábados: 9:00 AM - 1:00 PM\nDomingos: Cerrado\n\n⏰ Horario extendido en temporada escolar"),
            ("🌐", "Sitio Web y Redes",
             "Sitio Oficial: www.libreriaabc.com\nFacebook: /LibreriaABC\nInstagram: @LibreriaABC\nWhatsApp Business: +502 1234-5678")
        ]

        for icono, titulo_texto, contenido in info_items:
            item_layout = QHBoxLayout()

            lbl_icono = QLabel(icono)
            lbl_icono.setStyleSheet("font-size: 28px; margin-right: 20px; min-width: 50px;")

            texto_layout = QVBoxLayout()
            lbl_titulo = QLabel(titulo_texto)
            lbl_titulo.setStyleSheet("""
                font-size: 18px; 
                font-weight: bold; 
                color: #1E40AF; 
                margin-bottom: 8px;
            """)
            lbl_titulo.setWordWrap(True)

            lbl_contenido = QLabel(contenido)
            lbl_contenido.setStyleSheet("""
                font-size: 15px; 
                color: #64748B; 
                line-height: 1.5;
            """)
            lbl_contenido.setWordWrap(True)

            texto_layout.addWidget(lbl_titulo)
            texto_layout.addWidget(lbl_contenido)

            item_layout.addWidget(lbl_icono)
            item_layout.addLayout(texto_layout)
            item_layout.addStretch()

            info_layout.addLayout(item_layout)

            if info_items.index((icono, titulo_texto, contenido)) < len(info_items) - 1:
                separador = QFrame()
                separador.setFrameShape(QFrame.Shape.HLine)
                separador.setFrameShadow(QFrame.Shadow.Sunken)
                separador.setStyleSheet("background-color: #E2E8F0; margin: 15px 0px;")
                info_layout.addWidget(separador)

        scroll_layout.addWidget(info_frame)

        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(15)

        btn_whatsapp = QPushButton("💬 Contactar por WhatsApp")
        btn_whatsapp.setObjectName("whatsapp")
        btn_whatsapp.setFixedHeight(55)
        btn_whatsapp.setMinimumWidth(250)

        btn_llamar = QPushButton("📞 Llamar Ahora")
        btn_llamar.setObjectName("llamar")
        btn_llamar.setFixedHeight(55)
        btn_llamar.setMinimumWidth(160)

        btn_email = QPushButton("📧 Enviar Email")
        btn_email.setObjectName("email")
        btn_email.setFixedHeight(55)
        btn_email.setMinimumWidth(160)

        btn_whatsapp.clicked.connect(self._abrir_whatsapp)
        btn_llamar.clicked.connect(self._realizar_llamada)
        btn_email.clicked.connect(self._enviar_email)

        botones_layout.addStretch()
        botones_layout.addWidget(btn_whatsapp)
        botones_layout.addWidget(btn_llamar)
        botones_layout.addWidget(btn_email)
        botones_layout.addStretch()

        scroll_layout.addLayout(botones_layout)

        ubicacion_frame = QFrame()
        ubicacion_frame.setObjectName("info_card")
        ubicacion_layout = QVBoxLayout(ubicacion_frame)

        lbl_mapa_titulo = QLabel("🗺️ Nuestra Ubicación")
        lbl_mapa_titulo.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold; 
            color: #1E40AF; 
            margin-bottom: 15px;
        """)
        lbl_mapa_titulo.setWordWrap(True)

        info_ubicacion = QLabel(
            "📍 <b>Centro Comercial Plaza Central</b><br><br>"
            "7a Avenida 12-34, Zona 1<br>"
            "Ciudad de Guatemala, Guatemala<br><br>"
            "🚗 <b>Cómo llegar:</b><br>"
            "• A 2 cuadras del Parque Central<br>"
            "• Estacionamiento gratuito por 2 horas<br>"
            "• Acceso para personas con discapacidad<br>"
            "• Servicio de valet parking disponible<br><br>"
            "🚌 <b>Rutas de transporte:</b><br>"
            "• Rutas 1, 5, 7, 12 y 15<br>"
            "• Transmetro a 1 cuadra<br>"
            "• Taxis disponibles 24/7"
        )
        info_ubicacion.setStyleSheet("""
            font-size: 14px; 
            color: #64748B; 
            line-height: 1.6;
        """)
        info_ubicacion.setWordWrap(True)

        mapa_simulado = QLabel(
            "🗺️ \n\n📍 Ubicación: Centro de la Ciudad\n🏢 Edificio: Plaza Central, Nivel 2\n🚪 Local: 205-207")
        mapa_simulado.setStyleSheet("""
            font-size: 16px; 
            color: #374151; 
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F1F5F9, stop:1 #E2E8F0);
            padding: 60px 30px;
            border-radius: 10px;
            border: 3px dashed #CBD5E1;
            text-align: center;
            font-weight: bold;
            min-height: 180px;
        """)
        mapa_simulado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mapa_simulado.setWordWrap(True)

        ubicacion_layout.addWidget(lbl_mapa_titulo)
        ubicacion_layout.addWidget(info_ubicacion)
        ubicacion_layout.addWidget(mapa_simulado)

        scroll_layout.addWidget(ubicacion_frame)
        scroll_layout.addStretch()

        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        self.setLayout(layout)

    def _volver_al_inicio(self):
        if self.ventana_principal:
            self.ventana_principal.mostrar_ventana_principal()
        self.close()

    def _abrir_whatsapp(self):
        QMessageBox.information(self, "Contactar por WhatsApp",
                                "📱 <b>Contacto por WhatsApp</b><br><br>"
                                "Puedes contactarnos a través de:<br><br>"
                                "• <b>WhatsApp Business:</b> +502 1234-5678<br>"
                                "• <b>Horario de atención:</b> 8:00 AM - 6:00 PM<br>"
                                "• <b>Tiempo de respuesta:</b> 15 minutos promedio<br><br>"
                                "¡Estamos para servirte! 🎒✏️")

    def _realizar_llamada(self):
        QMessageBox.information(self, "Llamar",
                                "📞 <b>Líneas Telefónicas</b><br><br>"
                                "Puedes llamarnos a cualquiera de nuestras líneas:<br><br>"
                                "• <b>Línea Principal:</b> (502) 1234-5678<br>"
                                "• <b>Ventas y Pedidos:</b> (502) 8765-4321<br>"
                                "• <b>Soporte Técnico:</b> (502) 5555-9999<br><br>"
                                "⏰ <b>Horario de atención telefónica:</b><br>"
                                "Lunes a Viernes: 8:00 AM - 6:00 PM<br>"
                                "Sábados: 9:00 AM - 1:00 PM")

    def _enviar_email(self):
        QMessageBox.information(self, "Enviar Email",
                                "📧 <b>Correos Electrónicos</b><br><br>"
                                "Puedes enviarnos un email a:<br><br>"
                                "• <b>Información General:</b> info@libreriaabc.com<br>"
                                "• <b>Ventas y Pedidos:</b> ventas@libreriaabc.com<br>"
                                "• <b>Soporte Técnico:</b> soporte@libreriaabc.com<br><br>"
                                "⏳ <b>Tiempo de respuesta:</b> 24 horas máximo<br>"
                                "📎 <b>Adjunta:</b> Comprobantes, imágenes, etc.")

    def closeEvent(self, event):
        if self.ventana_principal and not self.ventana_principal.isVisible():
            self.ventana_principal.mostrar_ventana_principal()
        event.accept()

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
