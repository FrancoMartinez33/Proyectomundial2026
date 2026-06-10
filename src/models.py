class Equipo:
    def __init__(self, nombre, abreviatura, prefijo, grupo, id_identificador, confederacion=""):
        self.nombre = nombre
        self.abreviatura = abreviatura
        self.prefijo = prefijo
        self.grupo = grupo
        self.id = id_identificador
        self.confederacion = confederacion

        self.puntos = 0
        self.pj = 0
        self.gf = 0
        self.gc = 0
        self.am = 0
        self.rj = 0

        self.partidos = []
        self.plantel = {}

    def reset_stats(self):
        self.puntos = 0
        self.pj = 0
        self.gf = 0
        self.gc = 0
