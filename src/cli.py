# ─────────────────────────────────────────────────────────────
#  cli.py – Interfaz de línea de comandos (consola)
#  Muestra un menú interactivo con las opciones del sistema
#  y delega la lógica de negocio en services.py.
#  Responsabilidad: proporcionar una alternativa a la GUI
#  usando únicamente la terminal para interactuar con el usuario.
# ─────────────────────────────────────────────────────────────

from . import data_store
from .services import configuracion, registro, emision


def menu(contador):
    """
    Bucle principal del menú por consola.
    Muestra las opciones disponibles y ejecuta la acción
    seleccionada por el usuario.

    La opción 1 (Configuración) se oculta automáticamente
    una vez que se ha guardado la configuración del torneo
    (data_store.config_guardada = True).

    Parámetros:
        contador (int): valor legacy para control de flujo
                        (iniciar con 0).
    """
    while True:
        print(f"\n--- {data_store.nombre_torneo if data_store.nombre_torneo else 'SISTEMA MUNDIAL'} ---")
        print("1. Configuraci\u00f3n del torneo")
        print("2. Registro de resultados")
        print("3. Emisi\u00f3n de informes")
        print("4. Salir")
        print("5. Simulador")

        n = input("Opci\u00f3n: ")
        opciones = {"2": registro, "3": emision, "4": "salir", "5": "sim"}

        # Si la configuración aún no fue guardada, se habilita la opción 1
        if not data_store.config_guardada:
            opciones["1"] = configuracion

        if n == "4":
            break

        if n in opciones:
            if n == "1":
                contador = opciones[n]()
                if contador not in (None, False):
                    data_store.config_guardada = True
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
