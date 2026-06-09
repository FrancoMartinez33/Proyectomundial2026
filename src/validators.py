# ─────────────────────────────────────────────────────────────
#  validators.py – Funciones de validación de datos
#  Contiene utilidades para verificar formato y coherencia
#  de la información ingresada por el usuario.
#  Responsabilidad: garantizar que los datos de entrada
#  cumplan con los formatos esperados antes de procesarlos.
# ─────────────────────────────────────────────────────────────

import datetime


def validar_fecha_manual(texto_fecha):
    """
    Valida una fecha en formato DD/MM/AAAA.
    Verifica que la cadena tenga exactamente 10 caracteres,
    que las barras estén en las posiciones correctas,
    que día, mes y año sean numéricamente válidos.

    Parámetros:
        texto_fecha (str): fecha en formato DD/MM/AAAA.

    Retorna:
        datetime o None: objeto datetime si la fecha es válida,
        None si el formato es incorrecto.
    """
    if len(texto_fecha) == 10 and texto_fecha[2] == "/" and texto_fecha[5] == "/":
        dia = int(texto_fecha[0:2])
        mes = int(texto_fecha[3:5])
        anio = int(texto_fecha[6:10])
        if 1 <= dia <= 31 and 1 <= mes <= 12 and anio > 2000:
            return datetime.datetime(anio, mes, dia)
    return None
