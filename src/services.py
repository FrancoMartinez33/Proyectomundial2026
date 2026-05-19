# ─────────────────────────────────────────────────────────────
#  services.py – Lógica de negocio del torneo
#  Capa de servicios con funciones reutilizables tanto por la
#  CLI como por la GUI. No contiene input() ni tkinter, solo
#  procesamiento de datos puro.
#  Responsabilidad: orquestar la lógica del torneo (cálculo de
#  tablas, informes, clasificación de terceros, fase eliminatoria).
# ─────────────────────────────────────────────────────────────

import os
import random
from datetime import datetime

from . import data_store
from .data_store import tablagral, paises_mundial, prefijos_telefonicos
from .validators import validar_fecha_manual


# ──────────────────────────────────────────────
#  LÓGICA PURA (usada por CLI y GUI)
#  Funciones sin efectos de I/O, operan solo sobre datos.
# ──────────────────────────────────────────────


def generar_pares_grupo(lista_equipos):
    """
    Genera los pares de enfrentamiento de un grupo (todos contra todos, ida).
    Para 4 equipos, genera 6 pares: (e1,e2), (e1,e3), (e1,e4), (e2,e3), (e2,e4), (e3,e4).

    Parámetros:
        lista_equipos (list): lista de nombres de equipos en el grupo.

    Retorna:
        list: lista de tuplas (equipo_local, equipo_visitante) con los enfrentamientos.
    """
    pares = []
    for i in range(len(lista_equipos)):
        for j in range(i + 1, len(lista_equipos)):
            pares.append((lista_equipos[i], lista_equipos[j]))
    return pares


def _prefijo_num(nombre_pais):
    """
    Extrae el valor numérico del prefijo telefónico de un país.
    Se usa como último criterio de desempate en la tabla de posiciones.
    Ejemplo: "+54" → 54, "+591" → 591.

    Parámetros:
        nombre_pais (str): nombre del país.

    Retorna:
        int: valor numérico del prefijo, 0 si no se encuentra.
    """
    p = prefijos_telefonicos.get(nombre_pais, "+0")
    num = ""
    for c in p:
        if c.isdigit():
            num += c
    return int(num) if num else 0


def calcular_tabla_grupo(k):
    """
    Calcula la tabla de posiciones de un grupo.
    Recorre todos los partidos del grupo, suma estadísticas (PJ, puntos, GF, GC)
    y ordena por los siguientes criterios en orden descendente:
        1. Puntos (3 por victoria, 1 por empate)
        2. Diferencia de gol (GF - GC)
        3. Goles a favor (GF)
        4. Prefijo telefónico (menor prefijo = mejor posición)

    Parámetros:
        k (str): letra del grupo (A-L).

    Retorna:
        list: lista de objetos Equipo ordenados por posición en la tabla.
    """
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

    # Ordenamiento burbuja con criterios de desempate
    for x in range(len(temp)):
        for i in range(x + 1, len(temp)):
            a, b = temp[x], temp[i]
            dg_a = a.gf - a.gc
            dg_b = b.gf - b.gc
            if (a.puntos < b.puntos):
                temp[x], temp[i] = temp[i], temp[x]
            elif (a.puntos == b.puntos and dg_a < dg_b):
                temp[x], temp[i] = temp[i], temp[x]
            elif (a.puntos == b.puntos and dg_a == dg_b and a.gf < b.gf):
                temp[x], temp[i] = temp[i], temp[x]
            elif (a.puntos == b.puntos and dg_a == dg_b and a.gf == b.gf
                  and _prefijo_num(a.nombre) > _prefijo_num(b.nombre)):
                temp[x], temp[i] = temp[i], temp[x]

    return temp


# ──────────────────────────────────────────────
#  HELPERS SOLO PARA CLI (compatibilidad hacia atrás)
#  Estas funciones usan input()/print() directamente.
#  La GUI tiene sus propios mecanismos de entrada.
# ──────────────────────────────────────────────


def asignar_tarjetas(nombre_equipo, tipo_tarjeta):
    """
    Asigna tarjetas a jugadores de un equipo por consola.
    Pregunta cuántas tarjetas cargar, muestra la lista de jugadores
    y permite seleccionar el número del jugador para cada tarjeta.

    Parámetros:
        nombre_equipo (str): nombre del equipo.
        tipo_tarjeta (str): "AM" para amarilla, "RJ" para roja.
    """
    equipo = tablagral[nombre_equipo]
    cant = int(input(f"\u00bfCu\u00e1ntas tarjetas {tipo_tarjeta} para {nombre_equipo}?: "))

    for _ in range(cant):
        nombres_jugadores = list(equipo.plantel.keys())
        print(f"\nJUGADORES DE {nombre_equipo}:")
        for idx in range(len(nombres_jugadores)):
            print(f"{idx+1}. {nombres_jugadores[idx]}")

        sel = int(input(f"Seleccione el n\u00famero del jugador: "))
        jugador_sel = nombres_jugadores[sel - 1]

        equipo.plantel[jugador_sel][tipo_tarjeta] += 1
        if tipo_tarjeta == "AM":
            equipo.am += 1
        else:
            equipo.rj += 1


# ──────────────────────────────────────────────
#  FUNCIONES DE FLUJO (compatibles con CLI original)
#  Orquestan pasos completos del programa desde consola.
# ──────────────────────────────────────────────


def configuracion(nombre, f_inicio, f_fin):
    """
    Inicia la configuración del torneo: guarda nombre y fechas,
    valida que las fechas sean correctas y que el rango sea válido.

    Parámetros:
        nombre (str): nombre del torneo.
        f_inicio (str): fecha de inicio en formato DD/MM/AAAA.
        f_fin (str): fecha de fin en formato DD/MM/AAAA.

    Retorna:
        dict con "disponibles" (lista de países) y "grupos" (letras A-L),
        o str con mensaje de error si las fechas son inválidas.
    """
    data_store.nombre_torneo = nombre
    data_store.fecha_inicio_obj = validar_fecha_manual(f_inicio)
    data_store.fecha_fin_obj = validar_fecha_manual(f_fin)

    if not data_store.fecha_inicio_obj or not data_store.fecha_fin_obj:
        return "ERROR: fechas inv\u00e1lidas"

    if data_store.fecha_fin_obj <= data_store.fecha_inicio_obj:
        return "ERROR: rango de fechas incorrecto"

    disponibles = list(paises_mundial)
    abc = ["A","B","C","D","E","F","G","H","I","J","K","L"]

    return {
        "disponibles": disponibles,
        "grupos": abc
    }


def fechapartido(lista, grupo):
    """
    Carga fecha y hora de cada partido de un grupo por consola.
    Solicita fecha (DD/MM/AAAA) y hora (HH:MM) para cada enfrentamiento,
    validando que la fecha esté dentro del rango del torneo.

    Parámetros:
        lista (list): lista de nombres de equipos del grupo.
        grupo (str): letra del grupo.
    """
    pares = generar_pares_grupo(lista)
    for e1, e2 in pares:
        print(f"--- Partido: {e1} vs {e2} ---")
        while True:
            f = input(f"Fecha (DD/MM/AAAA): ")
            f_obj = validar_fecha_manual(f)
            if f_obj and (data_store.fecha_inicio_obj <= f_obj <= data_store.fecha_fin_obj):
                break
            print("Error: La fecha debe estar dentro del rango del torneo.")

        h = input("Hora (HH:MM): ")
        tablagral[e1].partidos.append({"rival": e2, "fecha": f, "hora": h, "goles": None})
        tablagral[e2].partidos.append({"rival": e1, "fecha": f, "hora": h, "goles": None})


def registro():
    """
    Carga resultados (goles y tarjetas) de un grupo por consola.
    Solicita el grupo, muestra cada partido y pide los goles,
    luego las tarjetas amarillas y rojas para cada equipo.
    """
    mostrados = []
    k = input("\u00bfGrupo? (A-L): ").upper()
    nombres = [n for n in tablagral if tablagral[n].grupo == k]

    for e1 in nombres:
        for p in tablagral[e1].partidos:
            e2 = p["rival"]
            if e1 + e2 not in mostrados and e2 + e1 not in mostrados:
                print(f"\n--- CARGA DE RESULTADO: {e1} vs {e2} ---")
                g1 = int(input(f"Goles {e1}: "))
                g2 = int(input(f"Goles {e2}: "))

                asignar_tarjetas(e1, "AM")
                asignar_tarjetas(e1, "RJ")
                asignar_tarjetas(e2, "AM")
                asignar_tarjetas(e2, "RJ")

                mostrados.append(e1 + e2)
                mostrados.append(e2 + e1)
                p["goles"] = [g1, g2]

                for p_rival in tablagral[e2].partidos:
                    if p_rival["rival"] == e1:
                        p_rival["goles"] = [g2, g1]
    print("\n\u00a1Resultados guardados!")


def emision():
    """
    Muestra la tabla de posiciones de un grupo por consola.
    Pide la letra del grupo y muestra ID, nombre, PJ, PTS, DG, GF, AM, RJ.
    """
    k = input("Grupo a emitir: ").upper()
    tabla = calcular_tabla_grupo(k)
    print(f"\n--- TABLA GRUPO {k} ---")
    print(f"{'ID':<4} {'EQUIPO':<15} {'PJ':<3} {'PTS':<4} {'DG':<4} {'GF':<3} {'AM':<3} {'RJ':<3}")
    for e in tabla:
        dg = e.gf - e.gc
        print(f"{e.id:<4} {e.nombre:<15} {e.pj:<3} {e.puntos:<4} {dg:<4} {e.gf:<3} {e.am:<3} {e.rj:<3}")


# ──────────────────────────────────────────────
#  FUNCIONES NUEVAS (randomizar + informes)
# ──────────────────────────────────────────────


def randomizar_grupos(disponibles, asignaciones):
    """
    Asigna aleatoriamente los países disponibles a grupos con cupos libres.
    Mezcla la lista de países y los distribuye en los grupos hasta
    completar 4 por grupo o agotar disponibles.

    Parámetros:
        disponibles (set): conjunto de países sin asignar.
        asignaciones (dict): { grupo: [lista de países asignados] }.

    Retorna:
        tuple: (asignaciones actualizadas, restantes como set).
    """
    disponibles = list(disponibles)
    random.shuffle(disponibles)
    idx = 0
    for g in asignaciones:
        while len(asignaciones[g]) < 4 and idx < len(disponibles):
            asignaciones[g].append(disponibles[idx])
            idx += 1
    restantes = set(disponibles[idx:])
    return asignaciones, restantes


# ──────────────────────────────────────────────
#  INFORME 1: Partidos en una fecha específica
# ──────────────────────────────────────────────


def partidos_en_fecha(fecha_str):
    """
    Busca todos los partidos programados en una fecha específica.
    Recorre todos los equipos y sus partidos, filtrando por fecha.

    Parámetros:
        fecha_str (str): fecha en formato DD/MM/AAAA.

    Retorna:
        list: lista de dicts con local, visitante, grupo, hora, resultado, goles.
    """
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


# ──────────────────────────────────────────────
#  INFORME 3: Resultados de un equipo
# ──────────────────────────────────────────────


def resultados_equipo(nombre):
    """
    Obtiene la información completa de un equipo: estadísticas,
    lista de partidos con resultados y plantel con tarjetas.
    Devuelve un dict estructurado para consumo de la GUI.

    Parámetros:
        nombre (str): nombre del equipo.

    Retorna:
        dict con datos del equipo, o None si no existe.
    """
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


# ──────────────────────────────────────────────
#  INFORME 4: Próximo partido de un equipo
# ──────────────────────────────────────────────


def proximo_partido_equipo(nombre):
    """
    Busca el primer partido pendiente (sin goles cargados) de un equipo.

    Parámetros:
        nombre (str): nombre del equipo.

    Retorna:
        dict con local, visitante, grupo, fecha, hora; o None si no hay pendientes.
    """
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
                "hora": p.get("hora", "Sin asignar")
            }
    return None


# ──────────────────────────────────────────────
#  INFORME 5: Todas las tablas de grupos
# ──────────────────────────────────────────────


def todas_tablas():
    """
    Calcula y devuelve las tablas de posiciones de todos los grupos (A-L).
    Cada grupo contiene una lista de dicts con id, nombre, pj, puntos, gf, gc, dg, am, rj.

    Retorna:
        dict: { letra_grupo: [lista de dicts con datos de cada equipo] }.
    """
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


# ──────────────────────────────────────────────
#  Genera reporte .txt completo de todos los informes
# ──────────────────────────────────────────────


def generar_reporte_completo():
    """
    Genera un reporte de texto completo con todas las tablas de grupos
    y la clasificación de los 8 mejores terceros lugares.
    Se guarda en la carpeta informes/ mediante guardar_informe_txt().

    Retorna:
        str: contenido del reporte en texto plano.
    """
    lineas = []
    lineas.append("=" * 60)
    lineas.append(f"INFORME COMPLETO DEL TORNEO: {data_store.nombre_torneo}")
    lineas.append(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    lineas.append("=" * 60)

    # Tablas de todos los grupos
    lineas.append("\n\n" + "=" * 60)
    lineas.append("TABLAS DE POSICIONES - TODOS LOS GRUPOS")
    lineas.append("=" * 60)
    tabs = todas_tablas()
    for g in "ABCDEFGHIJKL":
        lineas.append(f"\n--- GRUPO {g} ---")
        lineas.append(f"{'ID':<4} {'EQUIPO':<18} {'PJ':<3} {'PTS':<4} {'DG':<4} {'GF':<3}")
        for e in tabs[g]:
            lineas.append(f"{e['id']:<4} {e['nombre']:<18} {e['pj']:<3} {e['puntos']:<4} {e['dg']:<4} {e['gf']:<3}")

    # Clasificación de terceros
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
    """
    Genera un reporte en texto plano con la información completa de un equipo.
    Incluye estadísticas, lista de partidos y detalle de plantel/tarjetas.
    Se usa para generar el archivo .txt individual de cada equipo.

    Parámetros:
        nombre_equipo (str): nombre del equipo.

    Retorna:
        str: contenido del reporte en texto plano.
    """
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
    """
    Guarda el contenido de texto en un archivo .txt dentro de la carpeta informes/.
    Crea la carpeta informes/ si no existe.
    Si no se especifica nombre, genera uno con timestamp.

    Parámetros:
        contenido (str): texto a guardar.
        nombre_archivo (str, opcional): nombre del archivo .txt.

    Retorna:
        str: ruta completa del archivo guardado.
    """
    os.makedirs("informes", exist_ok=True)
    if nombre_archivo is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"informe_{timestamp}.txt"
    ruta = os.path.join("informes", nombre_archivo)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido)
    return ruta


# ──────────────────────────────────────────────
#  CLASIFICACIÓN DE TERCEROS
#  Calcula los 8 mejores terceros lugares de los 12 grupos.
#  Criterios: Puntos → Diferencia de Gol → Goles a Favor → Prefijo telefónico.
#  Los 8 clasificados avanzan a la fase eliminatoria.
# ──────────────────────────────────────────────


def calcular_terceros():
    """
    Obtiene el tercer equipo de cada grupo y los ordena según:
    Puntos (desc) → DG (desc) → GF (desc) → Prefijo telefónico (asc).
    Devuelve los 8 mejores.

    Retorna:
        list: hasta 8 dicts con nombre, grupo, puntos, dg, gf, prefijo, equipo.
    """
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


def clasificados_terceros():
    """
    Alias público para calcular_terceros().
    Retorna la lista de los 8 mejores terceros lugares clasificados.

    Retorna:
        list: hasta 8 dicts con datos de los terceros clasificados.
    """
    return calcular_terceros()


# ──────────────────────────────────────────────
#  FASE ELIMINATORIA
#  Genera los enfrentamientos de la fase eliminatoria:
#  Ronda 32 (Dieciseisavos), Ronda 16 (Octavos),
#  Cuartos de Final, Semifinal y Final.
#  Los ganadores de la Ronda 32 avanzan a la Ronda 16, etc.
# ──────────────────────────────────────────────


def _ganadores_grupos():
    """
    Obtiene el equipo que quedó primero (ganador) de cada grupo.

    Retorna:
        dict: { letra_grupo: nombre_del_equipo }.
    """
    res = {}
    for g in "ABCDEFGHIJKL":
        tabla = calcular_tabla_grupo(g)
        if len(tabla) >= 1:
            res[g] = tabla[0].nombre
    return res


def _segundos_grupos():
    """
    Obtiene el equipo que quedó segundo de cada grupo.

    Retorna:
        dict: { letra_grupo: nombre_del_equipo }.
    """
    res = {}
    for g in "ABCDEFGHIJKL":
        tabla = calcular_tabla_grupo(g)
        if len(tabla) >= 2:
            res[g] = tabla[1].nombre
    return res


def generar_ronda32():
    """
    Genera los 16 partidos de la Ronda 32 (Dieciseisavos de Final).
    Empareja:
      - 8 ganadores de grupo (A, B, D, E, G, I, K, L) vs 8 mejores terceros.
      - 4 ganadores restantes (C, F, H, J) vs segundos de sus mismos grupos.
      - Segundos restantes se emparejan entre sí.
    Almacena los partidos en data_store.partidos_ronda.

    Retorna:
        list: lista de dicts con los partidos generados.
    """
    ganadores = _ganadores_grupos()
    segundos = _segundos_grupos()
    terceros = clasificados_terceros()

    # Grupos cuyos ganadores enfrentan a terceros
    pares_terceros = {
        "A": 0, "B": 1, "D": 2, "E": 3,
        "G": 4, "I": 5, "K": 6, "L": 7
    }

    partidos = []
    for i, t in enumerate(terceros):
        grupo_ganador = list(pares_terceros.keys())[i]
        partidos.append({
            "local": ganadores[grupo_ganador],
            "visitante": t["nombre"],
            "fase": "R32",
            "goles": None,
            "ganador": None
        })

    # Los 4 ganadores restantes (C, F, H, J) enfrentan a segundos
    restantes = ["C", "F", "H", "J"]
    for g in restantes:
        if g in segundos:
            partidos.append({
                "local": ganadores[g],
                "visitante": segundos[g],
                "fase": "R32",
                "goles": None,
                "ganador": None
            })

    # Segundos restantes se emparejan entre sí
    segundos_usados = set()
    for p in partidos:
        if p["visitante"] in segundos.values():
            for g, nom in segundos.items():
                if nom == p["visitante"]:
                    segundos_usados.add(g)

    segundos_libres = [(g, nom) for g, nom in segundos.items() if g not in segundos_usados]
    for i in range(0, len(segundos_libres) - 1, 2):
        if i + 1 < len(segundos_libres):
            partidos.append({
                "local": segundos_libres[i][1],
                "visitante": segundos_libres[i + 1][1],
                "fase": "R32",
                "goles": None,
                "ganador": None
            })

    data_store.ronda_actual = "R32"
    data_store.partidos_ronda = partidos
    return partidos


def _nombre_ronda(fase):
    """
    Convierte el código de fase a su nombre en español.

    Parámetros:
        fase (str): código "R32", "R16", "QF", "SF" o "F".

    Retorna:
        str: nombre legible de la fase.
    """
    nombres = {"R32": "Dieciseisavos de Final", "R16": "Octavos de Final",
               "QF": "Cuartos de Final", "SF": "Semifinal", "F": "Final"}
    return nombres.get(fase, fase)


def _proxima_fase(fase):
    """
    Devuelve el código de la siguiente fase en la eliminatoria.
    R32 → R16 → QF → SF → F → None.

    Parámetros:
        fase (str): código de fase actual.

    Retorna:
        str o None: código de la siguiente fase.
    """
    orden = ["R32", "R16", "QF", "SF", "F"]
    idx = orden.index(fase)
    if idx + 1 < len(orden):
        return orden[idx + 1]
    return None


def procesar_resultados_ronda(resultados):
    """
    Procesa los resultados de una ronda eliminatoria:
      1. Asigna goles y determina ganador de cada partido.
      2. Registra el avance de los equipos ganadores.
      3. Genera los partidos de la siguiente ronda emparejando a los ganadores.
    Si es la Final, retorna None (el torneo terminó).

    Parámetros:
        resultados (dict): { indice_partido: {"local": goles, "visitante": goles} }.

    Retorna:
        list o None: lista de partidos de la siguiente ronda, o None si terminó.
    """
    for idx, goles in resultados.items():
        if 0 <= idx < len(data_store.partidos_ronda):
            p = data_store.partidos_ronda[idx]
            p["goles"] = [goles["local"], goles["visitante"]]
            if goles["local"] > goles["visitante"]:
                p["ganador"] = p["local"]
            elif goles["visitante"] > goles["local"]:
                p["ganador"] = p["visitante"]
            else:
                p["ganador"] = p["local"]

    # Registrar avances
    ganadores_ronda = [p["ganador"] for p in data_store.partidos_ronda if p["ganador"]]
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

    data_store.ronda_actual = prox_fase
    data_store.partidos_ronda = nuevos_partidos
    return nuevos_partidos


def obtener_estado_eliminatorias():
    """
    Devuelve el estado actual de la fase eliminatoria:
    ronda actual, lista de partidos y nombre legible de la ronda.

    Retorna:
        dict: con claves "ronda_actual", "partidos", "nombre_ronda".
    """
    return {
        "ronda_actual": data_store.ronda_actual,
        "partidos": data_store.partidos_ronda,
        "nombre_ronda": _nombre_ronda(data_store.ronda_actual) if data_store.ronda_actual else ""
    }


def reiniciar_eliminatorias():
    """
    Reinicia el estado de la fase eliminatoria a su valor inicial.
    Limpia la ronda actual, los partidos y los registros de avance.
    """
    data_store.ronda_actual = None
    data_store.partidos_ronda = []
    data_store.avances_equipos = {}


def obtener_maximo_avance():
    """
    Obtiene el máximo avance alcanzado por cada equipo en la fase eliminatoria.
    Los equipos que no avanzaron aparecen como "Fase de Grupos".
    El resultado se ordena por nivel de avance descendente.

    Retorna:
        list: tuplas (nombre_equipo, nombre_ronda, nivel_numérico).
    """
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
