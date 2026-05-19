# ─────────────────────────────────────────────────────────────
#  data_store.py – Almacén de datos global del torneo
#  Todas las variables compartidas entre módulos (CLI y GUI).
#  Funciona como una base de datos en memoria.
#  Responsabilidad: mantener el estado global del torneo
#  para que services.py, cli.py y gui.py compartan la misma info.
# ─────────────────────────────────────────────────────────────

from src.models import Equipo

# ── ESTRUCTURA PRINCIPAL ─────────────────────────
# tablagral: diccionario { nombre_del_pais: objeto Equipo }
# Es la estructura principal que contiene toda la información del torneo.
# Se popula cuando se finaliza la configuración (asignación de grupos).
tablagral = {}

# ── CONFIGURACIÓN DEL TORNEO ─────────────────────
nombre_torneo = ""             # Nombre del torneo ingresado por el usuario
fecha_inicio_obj = None        # datetime de inicio del torneo (objeto datetime o None)
fecha_fin_obj = None           # datetime de fin del torneo (objeto datetime o None)
config_guardada = False        # True después de finalizar la configuración del torneo.
                               # Impide volver a acceder a la pantalla de configuración.

# ── FASE ELIMINATORIA ────────────────────────────
# Datos de la fase eliminatoria (R32, R16, QF, SF, F).
ronda_actual = None            # "R32", "R16", "QF", "SF", "F" o None si no iniciada
partidos_ronda = []            # lista de dicts con info de cada partido eliminatorio.
                               # Cada dict: {"local", "visitante", "fase", "goles", "ganador"}
avances_equipos = {}           # { nombre_equipo: ronda_maxima_alcanzada }
                               # Se actualiza cada vez que un equipo gana un partido eliminatorio.

# ── PREFIJOS TELEFÓNICOS ─────────────────────────
# Diccionario que asigna a cada país su prefijo telefónico internacional.
# Se usa como último criterio de desempate en la clasificación de terceros
# (según la consigna: Puntos → DG → GF → Prefijo telefónico).
prefijos_telefonicos = {
    "Argentina": "+54", "Bolivia": "+591", "Brasil": "+55", "Chile": "+56",
    "Colombia": "+57", "Ecuador": "+593", "Paraguay": "+595", "Perú": "+51",
    "Uruguay": "+598", "Venezuela": "+58", "México": "+52", "Estados Unidos": "+1",
    "Canadá": "+1", "Costa Rica": "+506", "Panamá": "+507", "Jamaica": "+1876",
    "Honduras": "+504", "El Salvador": "+503", "España": "+34", "Francia": "+33",
    "Inglaterra": "+44", "Alemania": "+49", "Italia": "+39", "Portugal": "+351",
    "Holanda": "+31", "Bélgica": "+32", "Croacia": "+385", "Suiza": "+41",
    "Japón": "+81", "Corea del Sur": "+82", "Australia": "+61", "Arabia Saudita": "+966",
    "Irán": "+98", "Catar": "+974", "Egipto": "+20", "Marruecos": "+212",
    "Senegal": "+221", "Túnez": "+216", "Argelia": "+213", "Nigeria": "+234",
    "Camerún": "+237", "Ghana": "+233", "Sudáfrica": "+27", "Costa de Marfil": "+225",
    "Nueva Zelanda": "+64", "Polonia": "+48", "Dinamarca": "+45", "Serbia": "+381"
}

# ── PAÍSES PARTICIPANTES ─────────────────────────
# Lista fija con los 48 países participantes del Mundial 2026.
# Se usa como pool para que el usuario asigne equipos a los 12 grupos (A-L).
paises_mundial = [
    "Argentina", "Bolivia", "Brasil", "Chile", "Colombia", "Ecuador", "Paraguay", "Perú", "Uruguay", "Venezuela",
    "México", "Estados Unidos", "Canadá", "Costa Rica", "Panamá", "Jamaica", "Honduras", "El Salvador",
    "España", "Francia", "Inglaterra", "Alemania", "Italia", "Portugal", "Holanda", "Bélgica", "Croacia", "Suiza",
    "Japón", "Corea del Sur", "Australia", "Arabia Saudita", "Irán", "Catar",
    "Egipto", "Marruecos", "Senegal", "Túnez", "Argelia", "Nigeria", "Camerún", "Ghana", "Sudáfrica", "Costa de Marfil",
    "Nueva Zelanda", "Polonia", "Dinamarca", "Serbia"
]
