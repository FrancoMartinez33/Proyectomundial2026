# ─────────────────────────────────────────────────────────────
#  data_store.py – Almacén de datos global del torneo
#  Todas las variables compartidas entre módulos (CLI y GUI).
#  Funciona como una base de datos en memoria.
#  Responsabilidad: mantener el estado global del torneo
#  para que services.py, cli.py y gui.py compartan la misma info.
# ─────────────────────────────────────────────────────────────

import os

from src.models import Equipo

# ── CARGA DE JUGADORES DESDE ARCHIVO TXT ──────
# El archivo jugadores.txt debe contener: NombrePaís, NombreJugador
# Ejemplo: "México, Luis Malagón"
# Se carga al importar el módulo.

jugadores_por_equipo = {}   # { nombre_pais: [lista_de_jugadores] }

try:
    _base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _ruta = os.path.join(_base, "jugadores.txt")
    with open(_ruta, encoding="utf-8") as _f:
        for _linea in _f:
            _linea = _linea.strip()
            if not _linea:
                continue
            _partes = _linea.split(",", 1)
            if len(_partes) == 2:
                _equipo = _partes[0].strip()
                _jugador = _partes[1].strip()
                if _equipo not in jugadores_por_equipo:
                    jugadores_por_equipo[_equipo] = []
                jugadores_por_equipo[_equipo].append(_jugador)
except Exception:
    pass

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

# ── CARGA DE PAÍSES DESDE ARCHIVO TXT ────────────
# El archivo paises.txt debe contener: nombre;confederación;prefijo
# Ejemplo: "Argentina;CONMEBOL;+54"
# Se usa importlib.resources para acceder al archivo empaquetado.

import importlib.resources as _resources

paises_mundial = []            # Lista con nombres de los países
prefijos_telefonicos = {}      # { nombre_pais: prefijo }
confederaciones = {}           # { nombre_pais: confederación }

try:
    _texto = _resources.read_text("src", "paises.txt", encoding="utf-8")
    for _linea in _texto.strip().split("\n"):
        _linea = _linea.strip()
        if not _linea:
            continue
        _partes = _linea.split(";")
        if len(_partes) >= 3:
            nombre = _partes[0].strip()
            confed = _partes[1].strip()
            prefijo = _partes[2].strip()
            paises_mundial.append(nombre)
            prefijos_telefonicos[nombre] = prefijo
            confederaciones[nombre] = confed
except Exception:
    pass
