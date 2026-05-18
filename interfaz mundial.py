# ─────────────────────────────────────────────────────────────
#  interfaz mundial.py – Punto de entrada para la GUI
#  Crea la ventana raíz de tkinter e inicia la aplicación
#  gráfica del sistema de control del torneo.
# ─────────────────────────────────────────────────────────────

from src.gui import InterfazMundial
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazMundial(root)
    root.mainloop()
