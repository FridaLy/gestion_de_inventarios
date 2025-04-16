import json
from modelo import *
from typing import List


class GestorInventario:
    def __init__(self):
        self.productos: List[Producto] = []
        self.movimientos: List[Movimiento] = []
        self.categorias: List[Categoria] = []
        self.proveedores: List[Proveedor] = []
        self.responsables: List[Responsable] = []
        self.cargar_datos_ejemplo()

    def cargar_datos_ejemplo(self):
        cat1 = Categoria("CAT001", "Electrónicos")
        cat2 = Categoria("CAT002", "Ropa")
        self.categorias.extend([cat1, cat2])

        prov1 = Proveedor("PROV001", "TecnoSum", "contacto@tecnosum.com")
        prov2 = Proveedor("PROV002", "Textiles S.A.", "ventas@textiles.com")
        self.proveedores.extend([prov1, prov2])

        resp1 = Responsable("RESP001", "Christofer Amador", "Administrador")
        resp2 = Responsable("RESP002", "David Lara", "Supervisor")
        self.responsables.extend([resp1, resp2])

        prod1 = Producto("PROD001", "Laptop", cat1, prov1, 5, 10)
        prod2 = Producto("PROD002", "Camiseta", cat2, prov2, 20, 50)
        self.productos.extend([prod1, prod2])

    def registrar_producto(self, _id: str, nombre: str, categoria_id: str,
                           proveedor_id: str, stock_minimo: int) -> Producto:
        categoria = next((c for c in self.categorias if c.id == categoria_id), None)
        proveedor = next((p for p in self.proveedores if p.id == proveedor_id), None)

        if not categoria or not proveedor:
            raise ValueError("Categoría o proveedor no encontrado")

        producto = Producto(_id, nombre, categoria, proveedor, stock_minimo)
        self.productos.append(producto)
        return producto

    def buscar_producto(self, _id: str) -> Producto:
        return next((p for p in self.productos if p.id == id), None)

    def registrar_movimiento(self, tipo: str, producto_id: str, cantidad: int,
                             responsable_id: str, almacen: str, motivo=None) -> str:
        producto = self.buscar_producto(producto_id)
        responsable = next((r for r in self.responsables if r.id == responsable_id), None)

        if not producto or not responsable:
            raise ValueError("Producto o responsable no encontrado")

        movimiento_id = f"MOV{len(self.movimientos) + 1:03d}"

        if tipo == "Entrada":
            movimiento = Entrada(movimiento_id, producto, cantidad, responsable, almacen)
        elif tipo == "Salida":
            movimiento = Salida(movimiento_id, producto, cantidad, responsable, almacen)
        elif tipo == "Devolución":
            if not motivo:
                raise ValueError("Motivo requerido para devolución")
            movimiento = Devolucion(movimiento_id, producto, cantidad, responsable, almacen, motivo)
        else:
            raise ValueError("Tipo de movimiento no válido")

        resultado = movimiento.ejecutar()
        self.movimientos.append(movimiento)
        return resultado

    def validar_stock(self, producto_id: str) -> bool:
        producto = self.buscar_producto(producto_id)
        if not producto:
            raise ValueError("Producto no encontrado")
        return producto.stock_actual >= producto.stock_minimo

    def generar_reporte(self, tipo: str) -> List[dict]:
        if tipo == "productos":
            return [p.to_dict() for p in self.productos]
        elif tipo == "movimientos":
            return [m.to_dict() for m in self.movimientos]
        elif tipo == "stock_minimo":
            return [p.to_dict() for p in self.productos if p.stock_actual < p.stock_minimo]
        else:
            raise ValueError("Tipo de reporte no válido")

    def guardar_datos(self, archivo: str):
        datos = {
            'productos': [p.to_dict() for p in self.productos],
            'movimientos': [m.to_dict() for m in self.movimientos],
            'categorias': [c.to_dict() for c in self.categorias],
            'proveedores': [p.to_dict() for p in self.proveedores],
            'responsables': [r.to_dict() for r in self.responsables]
        }
        with open(archivo, 'w') as f:
            json.dump(datos, f, indent=4, default=str)  # type: ignore[arg-type]

    def cargar_datos(self, archivo: str):
        try:
            with open(archivo, 'r') as f:
                datos = json.load(f)
                self._cargar_desde_dict(datos)
        except FileNotFoundError:
            print("Archivo no encontrado, comenzando con datos vacíos")
        except Exception as e:
            print(f"Error al cargar datos: {e}")

    def _cargar_desde_dict(self, datos: dict):
        self.productos.clear()
        self.movimientos.clear()
        self.categorias.clear()
        self.proveedores.clear()
        self.responsables.clear()

        # Cargar entidades básicas
        self.categorias = [Categoria(c['id'], c['nombre']) for c in datos['categorias']]
        self.proveedores = [Proveedor(p['id'], p['nombre'], p['contacto']) for p in datos['proveedores']]
        self.responsables = [Responsable(r['id'], r['nombre'], r['rol']) for r in datos['responsables']]

        # Cargar productos (requiere reconstruir relaciones)
        for p in datos['productos']:
            cat = next((c for c in self.categorias if c.id == p['categoria']['id']), None)
            prov = next((pr for pr in self.proveedores if pr.id == p['proveedor']['id']), None)
            if cat and prov:
                self.productos.append(Producto(
                    p['id'], p['nombre'], cat, prov,
                    p['stock_minimo'], p['stock_actual']
                ))