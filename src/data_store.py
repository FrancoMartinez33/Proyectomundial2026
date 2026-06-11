import os

jugadores_por_equipo = {}

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

tablagral = {}

nombre_torneo = ""
fecha_inicio_obj = None
fecha_fin_obj = None
config_guardada = False

ronda_actual = None
partidos_ronda = []
avances_equipos = {}
historial_penales = []

paises_mundial = []
prefijos_telefonicos = {}
confederaciones = {}

try:
    _base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _ruta = os.path.join(_base, "paises.txt")
    with open(_ruta, encoding="utf-8") as _f:
        for _linea in _f:
            _linea = _linea.strip()
            if not _linea:
                continue
            _partes = _linea.split(",")
            if len(_partes) >= 4:
                nombre = _partes[0].strip()
                prefijo = _partes[2].strip()
                confed = _partes[3].strip()
                paises_mundial.append(nombre)
                prefijos_telefonicos[nombre] = prefijo
                confederaciones[nombre] = confed
except Exception as e:
    print(f"Advertencia: No se pudieron cargar los países: {e}")
