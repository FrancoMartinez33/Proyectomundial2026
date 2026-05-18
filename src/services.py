from . import data_store
from .data_store import tablagral, paises_mundial
from .validators import validar_fecha_manual


# ──────────────────────────────────────────────
#  PURE LOGIC (used by both CLI and GUI)
# ──────────────────────────────────────────────

def generar_pares_grupo(lista_equipos):
    pares = []
    for i in range(len(lista_equipos)):
        for j in range(i + 1, len(lista_equipos)):
            pares.append((lista_equipos[i], lista_equipos[j]))
    return pares


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

    for x in range(len(temp)):
        for i in range(x + 1, len(temp)):
            if temp[x].puntos < temp[i].puntos:
                temp[x], temp[i] = temp[i], temp[x]

    return temp


# ──────────────────────────────────────────────
#  CLI-ONLY HELPERS (backward compat)
# ──────────────────────────────────────────────

def asignar_tarjetas(nombre_equipo, tipo_tarjeta):
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
#  CLI WRAPPERS (backward compat)
# ──────────────────────────────────────────────

def configuracion(nombre, f_inicio, f_fin):
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
    k = input("Grupo a emitir: ").upper()
    tabla = calcular_tabla_grupo(k)
    print(f"\n--- TABLA GRUPO {k} ---")
    print(f"{'ID':<4} {'EQUIPO':<15} {'PJ':<3} {'PTS':<4} {'AM':<3} {'RJ':<3}")
    for e in tabla:
        print(f"{e.id:<4} {e.nombre:<15} {e.pj:<3} {e.puntos:<4} {e.am:<3} {e.rj:<3}")
