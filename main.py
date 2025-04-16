import tkinter as tk
from controlador import GestorInventario
from vista import InventarioVista


def main():
    root = tk.Tk()

    # Crear instancia del controlador
    controlador = GestorInventario()

    # Crear instancia de la vista y pasarle el controlador
    vista = InventarioVista(root, controlador)

    # Iniciar la aplicación
    root.mainloop()


if __name__ == "__main__":
    main()