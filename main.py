class Categoria:
    def __init__(self,id_categoria,nombre):
        self.id_categoria=id_categoria
        self.nombre=nombre


class Producto:

    def __init__(self, codigo_producto, id_categoria, nombre, precio, total_compras, total_ventas, stock, limite_stock):
        self.codigo_producto = codigo_producto
        self.id_categoria = id_categoria
        self.nombre = nombre
        self.precio = precio
        self.total_compras = total_compras
        self.total_ventas = total_ventas
        self.stock = stock
        self.limite_stock = limite_stock

    def actualizar_stock(self, cantidad, tipo):

        if tipo == 'compra':
            if self.limite_stock is not None and self.stock + cantidad > self.limite_stock:
                print(f"No se puede agregar la compra. Excede el límite de stock ({self.limite_stock}).")
                return False
            self.stock += cantidad
            self.total_compras += cantidad
            return True
        elif tipo == 'venta':
            if self.stock >= cantidad:
                self.stock -= cantidad
                self.total_ventas += cantidad
                return True
            else:
                print("Error: No hay suficiente stock para la venta.")
                return False
        return False

    def mostrar_info(self):
        return f"[{self.codigo_producto}] {self.nombre} | Precio: {self.precio:.2f} | Stock: {self.stock}"
