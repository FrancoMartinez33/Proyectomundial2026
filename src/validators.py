# ─────────────────────────────────────────────────────────────
#  validators.py – Funciones de validación de datos
#  Contiene utilidades para verificar formato y coherencia
#  de la información ingresada por el usuario.
# ─────────────────────────────────────────────────────────────

import datetime


# Valida una fecha en formato DD/MM/AAAA y devuelve un objeto
# datetime si es correcta, o None si no lo es
def validar_fecha_manual(texto_fecha):
    if len(texto_fecha) == 10 and texto_fecha[2] == "/" and texto_fecha[5] == "/":
        dia = int(texto_fecha[0:2])
        mes = int(texto_fecha[3:5])
        anio = int(texto_fecha[6:10])
        if 1 <= dia <= 31 and 1 <= mes <= 12 and anio > 2000:
            return datetime.datetime(anio, mes, dia)
    return None
