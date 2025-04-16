import tkinter as tk
from tkinter import ttk, messagebox
# Eliminado: 'from controlador import GestorInventario' (no se usa directamente en la vista)

class InventarioVista:
    def __init__(self, root, controlador):
        self.root = root
        self.controlador = controlador
        self.frame_reporte = None  # Inicializado en __init__
        self.widgets = {}  # Inicializado en __init__
        self.labels = {}  # Inicializado en __init__
        self.configurar_interfaz()

    def configurar_interfaz(self):
        self.root.title("Sistema de Gestión de Inventario")
        self.root.geometry("800x600")
        self.crear_menu_principal()

    def crear_menu_principal(self):
        self.limpiar_pantalla()

        tk.Label(self.root, text="Sistema de Gestión de Inventario",
                font=("Arial", 16)).pack(pady=20)

        frame_botones = tk.Frame(self.root)
        frame_botones.pack(pady=20)

        opciones = [
            ("Gestión de Productos", self.mostrar_formulario_producto),
            ("Registrar Movimiento", self.mostrar_formulario_movimiento),
            ("Generar Reportes", self.mostrar_reportes),
            ("Salir", self.root.quit)
        ]

        for texto, comando in opciones:
            tk.Button(frame_botones, text=texto, width=25,
                     command=comando).pack(pady=5)

    def mostrar_formulario_producto(self):
        self.limpiar_pantalla()
        self.crear_formulario(
            "Registrar Nuevo Producto",
            [
                ("ID Producto:", "entry", "entry_id"),
                ("Nombre:", "entry", "entry_nombre"),
                ("Categoría:", "combo", "combo_categoria",
                 [f"{c.id} - {c.nombre}" for c in self.controlador.categorias]),
                ("Proveedor:", "combo", "combo_proveedor",
                 [f"{p.id} - {p.nombre}" for p in self.controlador.proveedores]),
                ("Stock Mínimo:", "entry", "entry_stock_min")
            ],
            self.guardar_producto
        )

    def guardar_producto(self):
        try:
            datos = {
                'id': self.widgets["entry_id"].get(),
                'nombre': self.widgets["entry_nombre"].get(),
                'categoria_id': self.widgets["combo_categoria"].get().split(" - ")[0],
                'proveedor_id': self.widgets["combo_proveedor"].get().split(" - ")[0],
                'stock_minimo': int(self.widgets["entry_stock_min"].get())
            }

            self.controlador.registrar_producto(**datos)
            messagebox.showinfo("Éxito", "Producto registrado correctamente")
            self.crear_menu_principal()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def mostrar_formulario_movimiento(self):
        self.limpiar_pantalla()
        self.crear_formulario(
            "Registrar Movimiento de Inventario",
            [
                ("Tipo Movimiento:", "combo", "combo_tipo", ["Entrada", "Salida", "Devolución"]),
                ("Producto:", "combo", "combo_producto",
                 [f"{p.id} - {p.nombre}" for p in self.controlador.productos]),
                ("Cantidad:", "entry", "entry_cantidad"),
                ("Responsable:", "combo", "combo_responsable",
                 [f"{r.id} - {r.nombre}" for r in self.controlador.responsables]),
                ("Almacén:", "entry", "entry_almacen"),
                ("Motivo (solo devolución):", "entry", "entry_motivo")
            ],
            self.registrar_movimiento,
            config_extra=self.configurar_formulario_movimiento
        )

    def configurar_formulario_movimiento(self):
        # Ocultar motivo inicialmente
        self.widgets["entry_motivo"].grid_remove()
        self.labels["entry_motivo"].grid_remove()

        # Configurar evento para tipo de movimiento
        self.widgets["combo_tipo"].bind("<<ComboboxSelected>>", self.actualizar_formulario_movimiento)

    def actualizar_formulario_movimiento(self, event=None):  # Añadido event=None para evitar warning
        tipo = self.widgets["combo_tipo"].get()
        if tipo == "Devolución":
            self.widgets["entry_motivo"].grid()
            self.labels["entry_motivo"].grid()
        else:
            self.widgets["entry_motivo"].grid_remove()
            self.labels["entry_motivo"].grid_remove()

    def registrar_movimiento(self):
        try:
            datos = {
                'tipo': self.widgets["combo_tipo"].get(),
                'producto_id': self.widgets["combo_producto"].get().split(" - ")[0],
                'cantidad': int(self.widgets["entry_cantidad"].get()),
                'responsable_id': self.widgets["combo_responsable"].get().split(" - ")[0],
                'almacen': self.widgets["entry_almacen"].get()
            }

            if datos['tipo'] == "Devolución":
                datos['motivo'] = self.widgets["entry_motivo"].get()
                if not datos['motivo']:
                    raise ValueError("Debe especificar un motivo para la devolución")

            resultado = self.controlador.registrar_movimiento(**datos)
            messagebox.showinfo("Éxito", resultado)
            self.crear_menu_principal()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def mostrar_reportes(self):
        self.limpiar_pantalla()

        tk.Label(self.root, text="Generar Reportes",
                font=("Arial", 14)).pack(pady=10)

        frame_opciones = tk.Frame(self.root)
        frame_opciones.pack(pady=10)

        tk.Button(frame_opciones, text="Lista de Productos",
                 command=lambda: self.mostrar_reporte("productos")).pack(pady=5)
        tk.Button(frame_opciones, text="Historial de Movimientos",
                 command=lambda: self.mostrar_reporte("movimientos")).pack(pady=5)
        tk.Button(frame_opciones, text="Productos con Stock Bajo",
                 command=lambda: self.mostrar_reporte("stock_minimo")).pack(pady=5)

        tk.Button(self.root, text="Volver al Menú Principal",
                 command=self.crear_menu_principal).pack(pady=20)

        self.frame_reporte = tk.Frame(self.root)
        self.frame_reporte.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def mostrar_reporte(self, tipo: str):
        for widget in self.frame_reporte.winfo_children():
            widget.destroy()

        try:
            datos = self.controlador.generar_reporte(tipo)

            if not datos:
                tk.Label(self.frame_reporte, text="No hay datos para mostrar").pack()
                return

            tree = ttk.Treeview(self.frame_reporte)
            scrollbar = ttk.Scrollbar(self.frame_reporte, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscroll=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            tree.pack(fill=tk.BOTH, expand=True)

            if tipo == "productos":
                self._configurar_treeview_productos(tree, datos)
            elif tipo == "movimientos":
                self._configurar_treeview_movimientos(tree, datos)
            elif tipo == "stock_minimo":
                self._configurar_treeview_stock(tree, datos)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    @staticmethod
    def _configurar_columnas(tree, columnas):
        tree["columns"] = columnas
        tree.heading("#0", text="Ítem")
        tree.column("#0", width=50, stretch=tk.NO)

        for col in columnas:
            tree.heading(col, text=col.capitalize().replace("_", " "))
            tree.column(col, width=100, anchor=tk.W)

    def _configurar_treeview_productos(self, tree, datos):
        columnas = ("id", "nombre", "categoria", "proveedor", "stock_actual", "stock_minimo")
        self._configurar_columnas(tree, columnas)

        for i, item in enumerate(datos, 1):
            tree.insert("", tk.END, text=str(i), values=(
                item["id"],
                item["nombre"],
                item["categoria"]["nombre"],
                item["proveedor"]["nombre"],
                item["stock_actual"],
                item["stock_minimo"]
            ))

    def _configurar_treeview_movimientos(self, tree, datos):
        columnas = ("id", "fecha", "tipo", "producto", "cantidad", "responsable", "almacen")
        self._configurar_columnas(tree, columnas)

        for i, item in enumerate(datos, 1):
            tree.insert("", tk.END, text=str(i), values=(
                item["id"],
                item["fecha"],
                item.get("tipo", ""),
                item["producto"]["nombre"],
                item["cantidad"],
                item["responsable"]["nombre"],
                item["almacen"]
            ))

    def _configurar_treeview_stock(self, tree, datos):
        columnas = ("id", "nombre", "stock_actual", "stock_minimo", "diferencia")
        self._configurar_columnas(tree, columnas)

        for i, item in enumerate(datos, 1):
            diferencia = item["stock_actual"] - item["stock_minimo"]
            tree.insert("", tk.END, text=str(i), values=(
                item["id"],
                item["nombre"],
                item["stock_actual"],
                item["stock_minimo"],
                diferencia
            ))

    def crear_formulario(self, titulo, campos, comando_guardar, config_extra=None):
        tk.Label(self.root, text=titulo, font=("Arial", 14)).pack(pady=10)

        frame_form = tk.Frame(self.root)
        frame_form.pack(pady=10)

        self.widgets = {}
        self.labels = {}

        for i, (texto, tipo, clave, *opciones) in enumerate(campos):
            label = tk.Label(frame_form, text=texto)
            label.grid(row=i, column=0, padx=5, pady=5, sticky="e")
            self.labels[clave] = label

            if tipo == "combo":
                widget = ttk.Combobox(frame_form, values=opciones[0])
            else:
                widget = tk.Entry(frame_form)

            widget.grid(row=i, column=1, padx=5, pady=5, sticky="we")
            self.widgets[clave] = widget

        frame_botones = tk.Frame(self.root)
        frame_botones.pack(pady=10)

        tk.Button(frame_botones, text="Guardar", command=comando_guardar).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_botones, text="Cancelar", command=self.crear_menu_principal).pack(side=tk.LEFT, padx=5)

        if config_extra:
            config_extra()

    def limpiar_pantalla(self):
        for widget in self.root.winfo_children():
            widget.destroy()