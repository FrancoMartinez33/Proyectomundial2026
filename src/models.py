# ─────────────────────────────────────────────────────────────
#  models.py – Modelo de datos del dominio
#  Define la clase Equipo, que representa una selección
#  nacional con sus estadísticas, plantel y partidos.
# ─────────────────────────────────────────────────────────────

class Equipo:
    # Constructor: recibe los datos fijos del equipo
    def __init__(self, nombre, abreviatura, prefijo, grupo, id_identificador):
        self.nombre = nombre
        self.abreviatura = abreviatura
        self.prefijo = prefijo
        self.grupo = grupo
        self.id = id_identificador  # ej: "A1", "B2" (grupo+posición)

        # Estadísticas que se calculan durante el torneo
        self.puntos = 0
        self.pj = 0      # Partidos Jugados
        self.gf = 0      # Goles a Favor
        self.gc = 0      # Goles en Contra
        self.am = 0      # Total tarjetas amarillas
        self.rj = 0      # Total tarjetas rojas

        # Estructuras internas
        self.partidos = []                   # lista de dicts con info de cada encuentro
        self.plantel = {}                    # {"Jugador": {"AM": 0, "RJ": 0}}

    # Reinicia estadísticas para recalcular sin arrastrar valores viejos
    def reset_stats(self):
        self.puntos = 0
        self.pj = 0
        self.gf = 0
        self.gc = 0
