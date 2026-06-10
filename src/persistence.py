import os
import json
from datetime import datetime
from . import data_store
from .models import Equipo

RUTA = None

def _ruta_archivo():
    global RUTA
    if RUTA is None:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        RUTA = os.path.join(base, "mundial_data.json")
    return RUTA


def _equipo_a_dict(eq):
    return {
        "nombre": eq.nombre,
        "abreviatura": eq.abreviatura,
        "prefijo": eq.prefijo,
        "grupo": eq.grupo,
        "id": eq.id,
        "confederacion": eq.confederacion,
        "puntos": eq.puntos,
        "pj": eq.pj,
        "gf": eq.gf,
        "gc": eq.gc,
        "am": eq.am,
        "rj": eq.rj,
        "partidos": eq.partidos,
        "plantel": eq.plantel
    }


def _dict_a_equipo(d):
    eq = Equipo(
        nombre=d["nombre"],
        abreviatura=d["abreviatura"],
        prefijo=d["prefijo"],
        grupo=d["grupo"],
        id_identificador=d["id"],
        confederacion=d.get("confederacion", "")
    )
    eq.puntos = d.get("puntos", 0)
    eq.pj = d.get("pj", 0)
    eq.gf = d.get("gf", 0)
    eq.gc = d.get("gc", 0)
    eq.am = d.get("am", 0)
    eq.rj = d.get("rj", 0)
    eq.partidos = d.get("partidos", [])
    eq.plantel = d.get("plantel", {})
    return eq


def guardar_datos():
    datos = {
        "nombre_torneo": data_store.nombre_torneo,
        "fecha_inicio": data_store.fecha_inicio_obj.isoformat() if data_store.fecha_inicio_obj else None,
        "fecha_fin": data_store.fecha_fin_obj.isoformat() if data_store.fecha_fin_obj else None,
        "config_guardada": data_store.config_guardada,
        "ronda_actual": data_store.ronda_actual,
        "partidos_ronda": data_store.partidos_ronda,
        "avances_equipos": data_store.avances_equipos,
        "tablagral": {nom: _equipo_a_dict(eq) for nom, eq in data_store.tablagral.items()}
    }
    try:
        with open(_ruta_archivo(), "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def cargar_datos():
    try:
        with open(_ruta_archivo(), "r", encoding="utf-8") as f:
            datos = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return

    data_store.nombre_torneo = datos.get("nombre_torneo", "")

    fi = datos.get("fecha_inicio")
    data_store.fecha_inicio_obj = datetime.fromisoformat(fi) if fi else None

    ff = datos.get("fecha_fin")
    data_store.fecha_fin_obj = datetime.fromisoformat(ff) if ff else None

    data_store.config_guardada = datos.get("config_guardada", False)
    data_store.ronda_actual = datos.get("ronda_actual")
    data_store.partidos_ronda = datos.get("partidos_ronda", [])
    data_store.avances_equipos = datos.get("avances_equipos", {})

    tablagral_datos = datos.get("tablagral", {})
    data_store.tablagral.clear()
    for nom, d in tablagral_datos.items():
        data_store.tablagral[nom] = _dict_a_equipo(d)
