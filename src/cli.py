# ─────────────────────────────────────────────────────────────
#  cli.py – Interfaz de línea de comandos (consola)
#  Muestra el menú interactivo con las opciones clásicas
#  y delega la lógica en services.py.
# ─────────────────────────────────────────────────────────────

from . import data_store
from .services import configuracion, registro, emision


# Bucle principal del menú por consola
def menu(contador):
    while True:
        print(f"\n--- {data_store.nombre_torneo if data_store.nombre_torneo else 'SISTEMA MUNDIAL'} ---")
        print("1. Configuraci\u00f3n del torneo")
        print("2. Registro de resultados")
        print("3. Emisi\u00f3n de informes")
        print("4. Salir")
        print("5. Simulador")

        n = input("Opci\u00f3n: ")
        opciones = {"1": configuracion, "2": registro, "3": emision, "4": "salir", "5": "sim"}

        # Bloquea la opción 1 después de ejecutarla una vez
        if contador == 1 and "1" in opciones:
            del opciones["1"]

        if n == "4":
            break

        if n in opciones:
            if n == "1":
                contador = opciones[n]()
            else:
                if n == "2":
                    registro()
                elif n == "3":
                    emision()
        else:
            print("Opci\u00f3n inv\u00e1lida.")


# Punto de entrada: al ejecutar python src/cli.py directamente
if __name__ == "__main__":
    menu(0)
