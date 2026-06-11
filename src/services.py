import os
import random
from datetime import datetime

from . import data_store
from .data_store import tablagral, paises_mundial, prefijos_telefonicos, confederaciones, jugadores_por_equipo


def generar_pares_grupo(lista_equipos):
    pares = []
    for i in range(len(lista_equipos)):
        for j in range(i + 1, len(lista_equipos)):
            pares.append((lista_equipos[i], lista_equipos[j]))
    return pares


def _prefijo_num(nombre_pais):
    p = prefijos_telefonicos.get(nombre_pais, "+0")
    return int(''.join(c for c in p if c.isdigit())) if any(c.isdigit() for c in p) else 0


def calcular_tabla_grupo(k):
    temp = []
    for nombre in tablagral:
        e = tablagral[nombre]
        if e.grupo == k:
            e.reset_stats()
            for p in e.partidos:
                if p.get("goles") is not None:
                    gf, gc = p["goles"][0], p["goles"][1]
                    e.pj += 1
                    e.gf += gf
                    e.gc += gc
                    if gf > gc:
                        e.puntos += 3
                    elif gf == gc:
                        e.puntos += 1
            temp.append(e)

    temp.sort(key=lambda e: (e.puntos, e.gf - e.gc, e.gf, -_prefijo_num(e.nombre)), reverse=True)
    return temp


def configuracion(nombre, f_inicio, f_fin):
    data_store.nombre_torneo = nombre
    try:
        data_store.fecha_inicio_obj = datetime.strptime(f_inicio, "%d/%m/%Y")
        data_store.fecha_fin_obj = datetime.strptime(f_fin, "%d/%m/%Y")
    except (ValueError, TypeError):
        return "ERROR: fechas inv\u00e1lidas"

    if data_store.fecha_fin_obj <= data_store.fecha_inicio_obj:
        return "ERROR: rango de fechas incorrecto"

    return {
        "disponibles": list(paises_mundial),
        "grupos": ["A","B","C","D","E","F","G","H","I","J","K","L"]
    }


def _puede_agregar_a_grupo(pais, grupo_actual):
    conf_pais = confederaciones.get(pais)
    if not conf_pais:
        return True
    if conf_pais == "UEFA":
        uefa_count = sum(1 for eq in grupo_actual if confederaciones.get(eq) == "UEFA")
        return uefa_count < 2
    for eq in grupo_actual:
        if confederaciones.get(eq) == conf_pais:
            return False
    return True


def _distribuir_grupos(disponibles, asignaciones):
    temp_asig = {g: list(eqs) for g, eqs in asignaciones.items()}
    temp_disp = list(disponibles)

    for g in temp_asig:
        colocados = []
        restantes = []
        for pais in temp_disp:
            if len(temp_asig[g]) + len(colocados) >= 4:
                restantes.append(pais)
            elif _puede_agregar_a_grupo(pais, temp_asig[g] + colocados):
                colocados.append(pais)
            else:
                restantes.append(pais)
        temp_asig[g].extend(colocados)
        temp_disp = restantes

    return temp_asig, set(temp_disp)


def randomizar_grupos(disponibles, asignaciones):
    disponibles = list(disponibles)
    mejor_resultado = None
    mejor_restantes = None

    for _ in range(50):
        random.shuffle(disponibles)
        resultado, restantes = _distribuir_grupos(disponibles, asignaciones)
        if mejor_resultado is None or len(restantes) < len(mejor_restantes):
            mejor_resultado = resultado
            mejor_restantes = restantes
        if not restantes:
            return mejor_resultado, mejor_restantes

    return mejor_resultado, mejor_restantes


def partidos_en_fecha(fecha_str):
    equipos = list(tablagral.values())
    resultados = []
    for e in equipos:
        for p in e.partidos:
            if p.get("fecha") == fecha_str:
                goles = p.get("goles")
                if goles is not None:
                    resultado = f"{goles[0]} - {goles[1]}"
                else:
                    resultado = "Pendiente"
                resultados.append({
                    "local": e.nombre,
                    "visitante": p["rival"],
                    "grupo": e.grupo,
                    "hora": p.get("hora", ""),
                    "resultado": resultado,
                    "goles": goles
                })
    return resultados


def resultados_equipo(nombre):
    equipo = tablagral.get(nombre)
    if not equipo:
        return None
    dg = equipo.gf - equipo.gc
    partidos = []
    for p in equipo.partidos:
        goles = p.get("goles")
        if goles is not None:
            resultado = f"{goles[0]} - {goles[1]}"
        else:
            resultado = "Pendiente"
        partidos.append({
            "rival": p["rival"],
            "fecha": p.get("fecha", ""),
            "hora": p.get("hora", ""),
            "resultado": resultado,
            "goles": goles
        })

    plantel = []
    for jug, cards in sorted(equipo.plantel.items()):
        plantel.append({"nombre": jug, "am": cards["AM"], "rj": cards["RJ"]})

    return {
        "nombre": equipo.nombre,
        "abreviatura": equipo.abreviatura,
        "grupo": equipo.grupo,
        "id": equipo.id,
        "pj": equipo.pj,
        "puntos": equipo.puntos,
        "gf": equipo.gf,
        "gc": equipo.gc,
        "dg": dg,
        "am": equipo.am,
        "rj": equipo.rj,
        "partidos": partidos,
        "plantel": plantel
    }


def proximo_partido_equipo(nombre):
    equipo = tablagral.get(nombre)
    if not equipo:
        return None
    for p in equipo.partidos:
        if p.get("goles") is None:
            return {
                "local": nombre,
                "visitante": p["rival"],
                "grupo": equipo.grupo,
                "fecha": p.get("fecha", "Sin asignar"),
                "hora": p.get("hora", "Sin asignar"),
                "fase": "grupos"
            }
    for p in data_store.partidos_ronda:
        if p.get("goles") is not None:
            continue
        if p["local"] == nombre:
            return {
                "local": nombre,
                "visitante": p["visitante"],
                "fase": "R32",
                "fecha": "Sin asignar",
                "hora": "Sin asignar"
            }
        if p["visitante"] == nombre:
            return {
                "local": nombre,
                "visitante": p["local"],
                "fase": "R32",
                "fecha": "Sin asignar",
                "hora": "Sin asignar"
            }
    return None


def todas_tablas():
    grupos = "ABCDEFGHIJKL"
    resultado = {}
    for g in grupos:
        tabla = calcular_tabla_grupo(g)
        filas = []
        for e in tabla:
            filas.append({
                "id": e.id,
                "nombre": e.nombre,
                "pj": e.pj,
                "puntos": e.puntos,
                "gf": e.gf,
                "gc": e.gc,
                "dg": e.gf - e.gc,
                "am": e.am,
                "rj": e.rj
            })
        resultado[g] = filas
    return resultado


def generar_reporte_completo():
    lineas = []
    lineas.append("=" * 60)
    lineas.append(f"INFORME COMPLETO DEL TORNEO: {data_store.nombre_torneo}")
    lineas.append(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    lineas.append("=" * 60)

    lineas.append("\n\n" + "=" * 60)
    lineas.append("TABLAS DE POSICIONES - TODOS LOS GRUPOS")
    lineas.append("=" * 60)
    tabs = todas_tablas()
    for g in "ABCDEFGHIJKL":
        lineas.append(f"\n--- GRUPO {g} ---")
        lineas.append(f"{'ID':<4} {'EQUIPO':<18} {'PJ':<3} {'PTS':<4} {'DG':<4} {'GF':<3}")
        for e in tabs[g]:
            lineas.append(f"{e['id']:<4} {e['nombre']:<18} {e['pj']:<3} {e['puntos']:<4} {e['dg']:<4} {e['gf']:<3}")

    terceros = calcular_terceros()
    if terceros:
        lineas.append("\n\n" + "=" * 60)
        lineas.append("CLASIFICACIÓN DE TERCEROS (8 MEJORES)")
        lineas.append("=" * 60)
        lineas.append(f"{'#':<3} {'EQUIPO':<18} {'GRUPO':<6} {'PTS':<4} {'DG':<4} {'GF':<3}")
        for i, t in enumerate(terceros, 1):
            lineas.append(f"{i:<3} {t['nombre']:<18} {t['grupo']:<6} {t['puntos']:<4} {t['dg']:<4} {t['gf']:<3}")

    return "\n".join(lineas)


def generar_informe_equipo(nombre_equipo):
    equipo = tablagral.get(nombre_equipo)
    if not equipo:
        return "ERROR: equipo no encontrado"

    lineas = []
    lineas.append("=" * 50)
    lineas.append(f"INFORME DEL EQUIPO: {equipo.nombre}")
    lineas.append(f"Abreviatura: {equipo.abreviatura}")
    lineas.append(f"Grupo: {equipo.grupo}  |  ID: {equipo.id}")
    lineas.append(f"Torneo: {data_store.nombre_torneo}")
    lineas.append("=" * 50)

    lineas.append(f"\n--- ESTADÍSTICAS ---")
    lineas.append(f"  Partidos jugados:   {equipo.pj}")
    lineas.append(f"  Puntos:             {equipo.puntos}")
    lineas.append(f"  Goles a favor:      {equipo.gf}")
    lineas.append(f"  Goles en contra:    {equipo.gc}")
    lineas.append(f"  Diferencia de gol:  {equipo.gf - equipo.gc}")
    lineas.append(f"  Tarjetas amarillas: {equipo.am}")
    lineas.append(f"  Tarjetas rojas:     {equipo.rj}")

    lineas.append(f"\n--- PARTIDOS ---")
    if equipo.partidos:
        for i, p in enumerate(equipo.partidos, 1):
            goles = p.get("goles")
            if goles is not None:
                resultado = f"{goles[0]} - {goles[1]}"
            else:
                resultado = "Pendiente"
            fe = p.get("fecha", "")
            ho = p.get("hora", "")
            fyh = f"{fe} {ho}".strip()
            lineas.append(f"  {i}. vs {p['rival']:<18}  {resultado:>9}   {fyh}")
    else:
        lineas.append("  (No hay partidos registrados)")

    lineas.append(f"\n--- PLANTEL / TARJETAS ---")
    if equipo.plantel:
        for jug, cards in sorted(equipo.plantel.items()):
            lineas.append(f"  {jug:<20}  AM={cards['AM']}  RJ={cards['RJ']}")
    else:
        lineas.append("  (No hay jugadores registrados)")

    lineas.append("\n" + "=" * 50)
    return "\n".join(lineas)


def guardar_informe_txt(contenido, nombre_archivo=None):
    os.makedirs("informes", exist_ok=True)
    if nombre_archivo is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"informe_{timestamp}.txt"
    ruta = os.path.join("informes", nombre_archivo)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido)
    return ruta


def calcular_terceros():
    equipos = []
    for g in "ABCDEFGHIJKL":
        tabla = calcular_tabla_grupo(g)
        if len(tabla) >= 3:
            tercero = tabla[2]
            dg = tercero.gf - tercero.gc
            equipos.append({
                "nombre": tercero.nombre,
                "grupo": g,
                "puntos": tercero.puntos,
                "dg": dg,
                "gf": tercero.gf,
                "prefijo": _prefijo_num(tercero.nombre),
                "equipo": tercero
            })

    equipos.sort(key=lambda x: (-x["puntos"], -x["dg"], -x["gf"], x["prefijo"]))
    return equipos[:8]


def _ganadores_grupos():
    res = {}
    for g in "ABCDEFGHIJKL":
        tabla = calcular_tabla_grupo(g)
        if len(tabla) >= 1:
            res[g] = tabla[0].nombre
    return res


def _segundos_grupos():
    res = {}
    for g in "ABCDEFGHIJKL":
        tabla = calcular_tabla_grupo(g)
        if len(tabla) >= 2:
            res[g] = tabla[1].nombre
    return res


def _asignar_terceros(terceros, cruces_terceros):
    grupos_a_indices = {}
    for i, (_, grupos_permitidos) in enumerate(cruces_terceros):
        for g in grupos_permitidos:
            grupos_a_indices.setdefault(g, []).append(i)

    terceros_ordenados = sorted(terceros, key=lambda t: len(grupos_a_indices.get(t["grupo"], [])))

    asignados = {}
    indices_usados = set()
    for t in terceros_ordenados:
        opciones = [i for i in grupos_a_indices.get(t["grupo"], []) if i not in indices_usados]
        if not opciones:
            return None
        idx = opciones[0]
        asignados[idx] = t
        indices_usados.add(idx)

    return [asignados.get(i) for i in range(len(cruces_terceros))]


def generar_ronda32():
    ganadores = _ganadores_grupos()
    segundos = _segundos_grupos()
    terceros = calcular_terceros()

    if len(ganadores) < 12 or len(segundos) < 12 or len(terceros) < 8:
        return None

    cruces_terceros = [
        ("E", {"A","B","C","D","F"}),   # M74
        ("I", {"C","D","F","G","H"}),   # M77
        ("A", {"C","E","F","H","I"}),   # M79
        ("L", {"E","H","I","J","K"}),   # M80
        ("D", {"B","E","F","I","J"}),   # M81
        ("G", {"A","E","H","I","J"}),   # M82
        ("B", {"E","F","G","I","J"}),   # M85
        ("K", {"D","E","I","J","L"}),   # M87
    ]

    terceros_asignados = _asignar_terceros(terceros, cruces_terceros)
    if terceros_asignados is None:
        return None

    def _partido(local, visitante):
        return {"local": local, "visitante": visitante,
                "fase": "R32", "goles": None, "ganador": None}

    partidos = [
        _partido(segundos["A"], segundos["B"]),          # M73
        _partido(ganadores["E"], terceros_asignados[0]["nombre"]),  # M74
        _partido(ganadores["F"], segundos["C"]),          # M75
        _partido(ganadores["C"], segundos["F"]),          # M76
        _partido(ganadores["I"], terceros_asignados[1]["nombre"]),  # M77
        _partido(segundos["E"], segundos["I"]),           # M78
        _partido(ganadores["A"], terceros_asignados[2]["nombre"]),  # M79
        _partido(ganadores["L"], terceros_asignados[3]["nombre"]),  # M80
        _partido(ganadores["D"], terceros_asignados[4]["nombre"]),  # M81
        _partido(ganadores["G"], terceros_asignados[5]["nombre"]),  # M82
        _partido(segundos["K"], segundos["L"]),           # M83
        _partido(ganadores["H"], segundos["J"]),          # M84
        _partido(ganadores["B"], terceros_asignados[6]["nombre"]),  # M85
        _partido(ganadores["J"], segundos["H"]),          # M86
        _partido(ganadores["K"], terceros_asignados[7]["nombre"]),  # M87
        _partido(segundos["D"], segundos["G"]),           # M88
    ]

    data_store.ronda_actual = "R32"
    data_store.partidos_ronda = partidos
    return partidos


def _nombre_ronda(fase):
    nombres = {"R32": "Dieciseisavos de Final", "R16": "Octavos de Final",
               "QF": "Cuartos de Final", "SF": "Semifinal", "F": "Final"}
    return nombres.get(fase, fase)


def _proxima_fase(fase):
    orden = ["R32", "R16", "QF", "SF", "F"]
    idx = orden.index(fase)
    if idx + 1 < len(orden):
        return orden[idx + 1]
    return None


def procesar_resultados_ronda(resultados):
    for idx, goles in resultados.items():
        if 0 <= idx < len(data_store.partidos_ronda):
            p = data_store.partidos_ronda[idx]
            goles_local = goles["local"]
            goles_visitante = goles["visitante"]

            if goles_local > goles_visitante:
                p["goles"] = [goles_local, goles_visitante]
                p["ganador"] = p["local"]
            elif goles_visitante > goles_local:
                p["goles"] = [goles_local, goles_visitante]
                p["ganador"] = p["visitante"]
            else:
                # Empate → penales se cargan desde la GUI
                p["goles"] = [goles_local, goles_visitante]
                pen = resultados[idx].get("penales")
                if pen:
                    p["penales"] = [pen[0], pen[1]]
                    p["ganador"] = p["local"] if pen[0] > pen[1] else p["visitante"]
                else:
                    p["penales"] = None
                    p["ganador"] = None

    ganadores_ronda = [p["ganador"] for p in data_store.partidos_ronda if p["ganador"]]

    if len(ganadores_ronda) != len(data_store.partidos_ronda):
        return None
    for g in ganadores_ronda:
        data_store.avances_equipos[g] = data_store.ronda_actual

    fase_actual = data_store.ronda_actual
    prox_fase = _proxima_fase(fase_actual)
    if prox_fase is None or len(ganadores_ronda) < 2:
        return None

    nuevos_partidos = []
    for i in range(0, len(ganadores_ronda) - 1, 2):
        if i + 1 < len(ganadores_ronda):
            nuevos_partidos.append({
                "local": ganadores_ronda[i],
                "visitante": ganadores_ronda[i + 1],
                "fase": prox_fase,
                "goles": None,
                "ganador": None
            })

    # Guardar partidos con penales antes de reemplazar
    for p in data_store.partidos_ronda:
        if p.get("penales"):
            data_store.historial_penales.append(dict(p))

    data_store.ronda_actual = prox_fase
    data_store.partidos_ronda = nuevos_partidos
    return nuevos_partidos


def obtener_estado_eliminatorias():
    return {
        "ronda_actual": data_store.ronda_actual,
        "partidos": data_store.partidos_ronda,
        "nombre_ronda": _nombre_ronda(data_store.ronda_actual) if data_store.ronda_actual else ""
    }


def reiniciar_eliminatorias():
    data_store.ronda_actual = None
    data_store.partidos_ronda = []
    data_store.avances_equipos = {}


def obtener_maximo_avance():
    orden = {"R32": 1, "R16": 2, "QF": 3, "SF": 4, "F": 5}
    orden_inv = {1: "Dieciseisavos", 2: "Octavos", 3: "Cuartos", 4: "Semifinal", 5: "Final"}

    equipos = list(tablagral.keys())
    resultados = []
    for nom in equipos:
        ronda = data_store.avances_equipos.get(nom, None)
        if ronda:
            nivel = orden.get(ronda, 0)
            resultados.append((nom, orden_inv.get(nivel, ronda), nivel))
        else:
            resultados.append((nom, "Fase de Grupos", 0))

    resultados.sort(key=lambda x: -x[2])
    return resultados

