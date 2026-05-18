# ─────────────────────────────────────────────────────────────
#  proyectoanashei.py – Punto de entrada para la CLI (consola)
#  Versión original del programa. Ahora solo importa los
#  módulos refactorizados del paquete src/ y arranca el menú
#  interactivo por consola con menu(0).
# ─────────────────────────────────────────────────────────────

from src.models import Equipo
from src.data_store import tablagral, nombre_torneo, fecha_inicio_obj, fecha_fin_obj, paises_mundial
from src.validators import validar_fecha_manual
from src.services import configuracion, fechapartido, registro, emision, asignar_tarjetas
from src.cli import menu

if __name__ == "__main__":
    menu(0)
