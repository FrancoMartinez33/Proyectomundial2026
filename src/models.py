# ─────────────────────────────────────────────────────────────
#  models.py – Modelo de datos del dominio
#  Define la clase Equipo, que representa una selección
#  nacional con sus estadísticas, plantel y partidos.
#  Responsabilidad: encapsular el estado de cada equipo
#  durante el torneo (grupo, estadísticas, partidos, tarjetas).
# ─────────────────────────────────────────────────────────────

class Equipo:
    """
    Representa una selección nacional participante del torneo.
    Almacena datos fijos (nombre, grupo, ID) y variables
    (estadísticas, partidos, plantel con tarjetas).
    """

    def __init__(self, nombre, abreviatura, prefijo, grupo, id_identificador):
        """
        Constructor del equipo. Recibe los datos que se conocen
        al momento de la configuración del torneo.

        Parámetros:
            nombre (str): nombre del país (ej: "Argentina").
            abreviatura (str): código de 3 letras (ej: "ARG").
            prefijo (str): prefijo telefónico internacional (ej: "+54").
            grupo (str): letra del grupo asignado (A-L).
            id_identificador (str): identificador grupo+posición (ej: "A1", "B3").
        """
        self.nombre = nombre
        self.abreviatura = abreviatura
        self.prefijo = prefijo
        self.grupo = grupo
        self.id = id_identificador

        # Estadísticas que se calculan durante el torneo
        self.puntos = 0      # Puntos acumulados (3 por victoria, 1 por empate)
        self.pj = 0          # Partidos Jugados
        self.gf = 0          # Goles a Favor
        self.gc = 0          # Goles en Contra
        self.am = 0          # Total de tarjetas amarillas del equipo
        self.rj = 0          # Total de tarjetas rojas del equipo

        # Estructuras internas dinámicas
        self.partidos = []   # Lista de dicts con cada partido:
                             #   {"rival": str, "fecha": str, "hora": str, "goles": [int,int] o None}
        self.plantel = {}    # Dict de jugadores con sus tarjetas:
                             #   {"NombreJugador": {"AM": int, "RJ": int}}

    def reset_stats(self):
        """
        Reinicia las estadísticas acumuladas del equipo.
        Se llama antes de recalcular la tabla de posiciones para
        evitar arrastrar valores de cálculos anteriores.
        NOTA: No reinicia partidos ni plantel, solo puntos/PJ/goles.
        """
        self.puntos = 0
        self.pj = 0
        self.gf = 0
        self.gc = 0
