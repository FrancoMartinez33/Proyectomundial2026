# ─────────────────────────────────────────────────────────────
#  data_store.py – Almacén de datos global del torneo
#  Todas las variables compartidas entre módulos (CLI y GUI).
#  Funciona como una base de datos en memoria.
# ─────────────────────────────────────────────────────────────

from src.models import Equipo

# tablagral: diccionario { nombre_del_pais: objeto Equipo }
# Es la estructura principal que contiene toda la información del torneo
tablagral = {}

nombre_torneo = ""
fecha_inicio_obj = None  # datetime de inicio del torneo
fecha_fin_obj = None     # datetime de fin del torneo

# Lista fija con los 48 países participantes del Mundial 2026
paises_mundial = [
    "Argentina", "Bolivia", "Brasil", "Chile", "Colombia", "Ecuador", "Paraguay", "Perú", "Uruguay", "Venezuela",
    "México", "Estados Unidos", "Canadá", "Costa Rica", "Panamá", "Jamaica", "Honduras", "El Salvador",
    "España", "Francia", "Inglaterra", "Alemania", "Italia", "Portugal", "Holanda", "Bélgica", "Croacia", "Suiza",
    "Japón", "Corea del Sur", "Australia", "Arabia Saudita", "Irán", "Catar",
    "Egipto", "Marruecos", "Senegal", "Túnez", "Argelia", "Nigeria", "Camerún", "Ghana", "Sudáfrica", "Costa de Marfil",
    "Nueva Zelanda", "Polonia", "Dinamarca", "Serbia"
]
