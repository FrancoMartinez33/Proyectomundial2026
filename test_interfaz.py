#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────
# test_interfaz.py – Script para probar la nueva interfaz
# ─────────────────────────────────────────────────────────────

import tkinter as tk
from src.gui import InterfazMundial

if __name__ == "__main__":
    print("Iniciando FIFA World Cup 2026 - Sistema de Control")
    print("=" * 50)
    print("Nueva interfaz visual aplicada:")
    print("✓ Menú en Canvas con imágenes")
    print("✓ Reloj dinámico")
    print("✓ Colores neón (Cian y Verde)")
    print("✓ Resolución: 1280x720")
    print("=" * 50)
    
    root = tk.Tk()
    app = InterfazMundial(root)
    root.mainloop()
