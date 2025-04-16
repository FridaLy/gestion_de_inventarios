from datetime import datetime
from abc import ABC, abstractmethod


class Serializable:
    def to_dict(self):
        return self.__dict__


class Responsable(Serializable):
    def __init__(self, id_: str, nombre: str, rol: str):
        self.id = id_
        self.nombre = nombre
        self.rol = rol


class Categoria(Serializable):
    def __init__(self, id_: str, nombre: str):
        self.id = id_
        self.nombre = nombre


class Proveedor(Serializable):
    def __init__(self, id_: str, nombre: str, contacto: str):
        self.id = id_
        self.nombre = nombre
        self.contacto = contacto


class Producto(Serializable):
    def __init__(self, id_: str, nombre: str, categoria: Categoria,
                 proveedor: Proveedor, stock_minimo: int, stock_actual: int = 0):
        self.id = id_
        self.nombre = nombre
        self.categoria = categoria
        self.proveedor = proveedor
        self.stock_minimo = stock_minimo
        self.stock_actual = stock_actual

    def actualizar_stock(self, cantidad: int):
        self.stock_actual += cantidad
        return self.stock_actual


class Movimiento(ABC, Serializable):
    def __init__(self, id_: str, producto: Producto, cantidad: int,
                 responsable: Responsable, almacen: str):
        self.id = id_
        self.fecha = datetime.now()
        self.producto = producto
        self.cantidad = cantidad
        self.responsable = responsable
        self.almacen = almacen

    @abstractmethod
    def ejecutar(self):
        pass


class Entrada(Movimiento):
    def __init__(self, id_: str, producto: Producto, cantidad: int,
                 responsable: Responsable, almacen: str):
        super().__init__(id_, producto, cantidad, responsable, almacen)
        self.tipo = "Entrada"

    def ejecutar(self):
        self.producto.actualizar_stock(self.cantidad)
        return f"Entrada de {self.cantidad} unidades de {self.producto.nombre}"


class Salida(Movimiento):
    def __init__(self, id_: str, producto: Producto, cantidad: int,
                 responsable: Responsable, almacen: str):
        super().__init__(id_, producto, cantidad, responsable, almacen)
        self.tipo = "Salida"

    def ejecutar(self):
        if self.producto.stock_actual >= self.cantidad:
            self.producto.actualizar_stock(-self.cantidad)
            return f"Salida de {self.cantidad} unidades de {self.producto.nombre}"
        else:
            raise ValueError("Stock insuficiente")


class Devolucion(Movimiento):
    def __init__(self, id_: str, producto: Producto, cantidad: int,
                 responsable: Responsable, almacen: str, motivo: str):
        super().__init__(id_, producto, cantidad, responsable, almacen)
        self.tipo = "Devolución"
        self.motivo = motivo

    def ejecutar(self):
        self.producto.actualizar_stock(self.cantidad)
        return f"Devolución de {self.cantidad} unidades de {self.producto.nombre}. Motivo: {self.motivo}"