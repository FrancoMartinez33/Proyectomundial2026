import datetime

# =================================================================
# 1. MODELO DE DATOS (CLASE EQUIPO)
# =================================================================
# Esta clase es el "molde" de cada selección. Tu amigo del Front 
# debe saber que cada equipo es un objeto con estos atributos.
class Equipo:
    def __init__(self, nombre, abreviatura, prefijo, grupo, id_identificador):
        self.nombre = nombre
        self.abreviatura = abreviatura
        self.prefijo = prefijo
        self.grupo = grupo
        self.id = id_identificador  # Ej: "A1", "B2" (Útil para llaves o IDs en el Front)
        
        # Estadísticas del equipo (Se calculan en la función emision)
        self.puntos = 0
        self.pj = 0  # Partidos Jugados
        self.gf = 0  # Goles a Favor
        self.gc = 0  # Goles en Contra
        self.am = 0  # Total de Amarillas del equipo
        self.rj = 0  # Total de Rojas del equipo
        
        # Estructuras de datos internas
        self.partidos = []  # Lista de diccionarios con info de cada encuentro
        self.plantel = {}   # Diccionario: { "Nombre Jugador": {"AM": 0, "RJ": 0} }

    def reset_stats(self):
        """Limpia puntos y goles para recalcular la tabla sin acumular basura"""
        self.puntos = 0
        self.pj = 0
        self.gf = 0
        self.gc = 0

# =================================================================
# 2. BASE DE DATOS GLOBAL
# =================================================================
# tablagral es un diccionario donde la LLAVE es el nombre del país 
# y el VALOR es el objeto Equipo.
tablagral = {}        
nombre_torneo = ""
fecha_inicio_obj = None 
fecha_fin_obj = None

# Lista fija de 48 países para el selector
paises_mundial = [
    "Argentina", "Bolivia", "Brasil", "Chile", "Colombia", "Ecuador", "Paraguay", "Perú", "Uruguay", "Venezuela",
    "México", "Estados Unidos", "Canadá", "Costa Rica", "Panamá", "Jamaica", "Honduras", "El Salvador",
    "España", "Francia", "Inglaterra", "Alemania", "Italia", "Portugal", "Holanda", "Bélgica", "Croacia", "Suiza",
    "Japón", "Corea del Sur", "Australia", "Arabia Saudita", "Irán", "Catar",
    "Egipto", "Marruecos", "Senegal", "Túnez", "Argelia", "Nigeria", "Camerún", "Ghana", "Sudáfrica", "Costa de Marfil",
    "Nueva Zelanda", "Polonia", "Dinamarca", "Serbia"
]

# =================================================================
# 3. FUNCIONES DE VALIDACIÓN (BACK-END)
# =================================================================
def validar_fecha_manual(texto_fecha):
    """Verifica el formato DD/MM/AAAA y devuelve un objeto fecha para comparar"""
    if len(texto_fecha) == 10 and texto_fecha[2] == "/" and texto_fecha[5] == "/":
        dia = int(texto_fecha[0:2])
        mes = int(texto_fecha[3:5])
        anio = int(texto_fecha[6:10])
        if 1 <= dia <= 31 and 1 <= mes <= 12 and anio > 2000:
            return datetime.datetime(anio, mes, dia)
    return None

def asignar_tarjetas(nombre_equipo, tipo_tarjeta):
    """Interfaz para elegir un jugador del plantel y sumarle una tarjeta"""
    equipo = tablagral[nombre_equipo]
    # Input de cantidad (Front: esto podría ser un modal o un select múltiple)
    cant = int(input(f"¿Cuántas tarjetas {tipo_tarjeta} para {nombre_equipo}?: "))
    
    for _ in range(cant):
        nombres_jugadores = list(equipo.plantel.keys())
        print(f"\nJUGADORES DE {nombre_equipo}:")
        for idx in range(len(nombres_jugadores)):
            print(f"{idx+1}. {nombres_jugadores[idx]}")
        
        sel = int(input(f"Seleccione el número del jugador: "))
        jugador_sel = nombres_jugadores[sel - 1]
        
        # Se guarda el dato en el jugador individual
        equipo.plantel[jugador_sel][tipo_tarjeta] += 1
        # Se acumula en el total del equipo para la tabla general
        if tipo_tarjeta == "AM": equipo.am += 1
        else: equipo.rj += 1

# =================================================================
# 4. PROCESAMIENTO DE DATOS
# =================================================================

def configuracion():
    """Carga inicial: Crea equipos, carga jugadores y genera fixture"""
    abc = ["A","B","C","D","E","F","G","H","I","J","K","L"]
    global tablagral, nombre_torneo, fecha_inicio_obj, fecha_fin_obj
    
    nombre_torneo = input("Nombre del Torneo: ")
    
    # Validación de fechas límite del torneo
    while True:
        f_ini = input("Fecha Inicio (DD/MM/AAAA): ")
        fecha_inicio_obj = validar_fecha_manual(f_ini)
        f_fin = input("Fecha Fin (DD/MM/AAAA): ")
        fecha_fin_obj = validar_fecha_manual(f_fin)
        
        if fecha_inicio_obj and fecha_fin_obj and fecha_fin_obj > fecha_inicio_obj:
            break
        print("Error: Fechas inválidas o rango incoherente.")

    disponibles = list(paises_mundial)
    
    for x in range(12): 
        print(f"\n--- GRUPO {abc[x]} ---")
        equipos_grupo = []
        
        for i in range(4):
            # Imprime países en 3 columnas (UI Limpia)
            for j in range(len(disponibles)):
                print(f"{j+1}. {disponibles[j]}", end="\t" if (j+1)%3 != 0 else "\n")
            
            opcion = int(input(f"\nElija país {abc[x]}{i+1}: "))
            nombre = disponibles[opcion - 1]
            del disponibles[opcion - 1] # Evita repetir país en otro slot
            
            abreviatura = input(f"Abreviatura: ").upper()
            prefijo = int(input(f"Prefijo: "))
            
            # INSTANCIACIÓN: Se crea el objeto Equipo
            tablagral[nombre] = Equipo(nombre, abreviatura, prefijo, abc[x], f"{abc[x]}{i+1}")
            
            # CARGA DE ARCHIVO: Se asocian jugadores al equipo
            archivo = open("jugadores.txt", "r", encoding="utf-8")
            for linea in archivo:
                datos = linea.strip().split(",")
                if datos[0].strip() == nombre:
                    # Se crea el registro de tarjetas del jugador
                    tablagral[nombre].plantel[datos[1].strip()] = {"AM": 0, "RJ": 0}
            archivo.close()
            equipos_grupo.append(nombre)
        
        fechapartido(equipos_grupo, abc[x])
    return 1 # Este '1' es el que bloquea la configuración en el menú

def fechapartido(lista, grupo):
    """Genera los enfrentamientos y valida que la fecha esté en rango"""
    creados = [] 
    for e1 in lista:
        for e2 in lista:
            if e1 != e2 and (e1+e2 not in creados and e2+e1 not in creados):
                print(f"--- Partido: {e1} vs {e2} ---")
                while True:
                    f = input(f"Fecha (DD/MM/AAAA): ")
                    f_obj = validar_fecha_manual(f)
                    if f_obj and (fecha_inicio_obj <= f_obj <= fecha_fin_obj):
                        break
                    print("Error: La fecha debe estar dentro del rango del torneo.")
                
                h = input("Hora (HH:MM): ")
                # Se guarda el partido en la lista de ambos rivales
                tablagral[e1].partidos.append({"rival": e2, "fecha": f, "hora": h, "goles": None})
                tablagral[e2].partidos.append({"rival": e1, "fecha": f, "hora": h, "goles": None})
                creados.append(e1+e2)

def registro():
    """Carga resultados de goles y dispara la asignación de tarjetas"""
    mostrados = []
    k = input("¿Grupo? (A-L): ").upper()
    nombres = [n for n in tablagral if tablagral[n].grupo == k]
            
    for e1 in nombres:
        for p in tablagral[e1].partidos:
            e2 = p["rival"]
            if e1 + e2 not in mostrados and e2 + e1 not in mostrados:
                print(f"\n--- CARGA DE RESULTADO: {e1} vs {e2} ---")
                g1 = int(input(f"Goles {e1}: "))
                g2 = int(input(f"Goles {e2}: "))
                
                # Proceso de asignación de tarjetas a jugadores
                asignar_tarjetas(e1, "AM")
                asignar_tarjetas(e1, "RJ")
                asignar_tarjetas(e2, "AM")
                asignar_tarjetas(e2, "RJ")
                
                mostrados.append(e1 + e2)
                mostrados.append(e2 + e1)
                p["goles"] = [g1, g2]
                
                # Sincroniza los goles en el objeto del equipo rival
                for p_rival in tablagral[e2].partidos:
                    if p_rival["rival"] == e1:
                        p_rival["goles"] = [g2, g1]
    print("\n¡Resultados guardados!")

def emision():
    """Genera la tabla de posiciones filtrada por grupo y ordenada"""
    k = input("Grupo a emitir: ").upper()
    temp = []
    for nombre in tablagral:
        e = tablagral[nombre]
        if e.grupo == k:
            e.reset_stats() 
            for p in e.partidos:
                if p["goles"] is not None:
                    gf, gc = p["goles"][0], p["goles"][1]
                    e.pj += 1
                    e.gf += gf
                    e.gc += gc
                    if gf > gc: e.puntos += 3
                    elif gf == gc: e.puntos += 1
            temp.append(nombre)
    
    # ORDENAMIENTO BURBUJA: Ordena por puntos de mayor a menor
    for x in range(len(temp)):
        for i in range(x+1, len(temp)):
            if tablagral[temp[x]].puntos < tablagral[temp[i]].puntos:
                temp[x], temp[i] = temp[i], temp[x]

    # UI: Informe Final
    print(f"\n--- TABLA GRUPO {k} ---")
    print(f"{'ID':<4} {'EQUIPO':<15} {'PJ':<3} {'PTS':<4} {'AM':<3} {'RJ':<3}")
    for n in temp:
        e = tablagral[n]
        print(f"{e.id:<4} {e.nombre:<15} {e.pj:<3} {e.puntos:<4} {e.am:<3} {e.rj:<3}")

# =================================================================
# 5. MENÚ PRINCIPAL (CONTROL DE FLUJO)
# =================================================================
def menu(contador):
    global nombre_torneo
    while True:
        print(f"\n--- {nombre_torneo if nombre_torneo else 'SISTEMA MUNDIAL'} ---")
        print("1. Configuración del torneo")
        print("2. Registro de resultados")
        print("3. Emisión de informes")
        print("4. Salir")
        print("5. Simulador")
        
        n = input("Opción: ")
        # El diccionario de opciones ayuda al Front a mapear botones a funciones
        opciones = {"1": configuracion, "2": registro, "3": emision, "4": "salir", "5": "sim"}
        
        # Bloqueo de Configuración: Si contador es 1, ya no se puede entrar a la opción 1
        if contador == 1 and "1" in opciones:
            del opciones["1"]
            
        if n == "4": break 
            
        if n in opciones:
            if n == "1":
                contador = opciones[n]() # Ejecuta y guarda el estado (1)
            else:
                if n == "2": registro()
                elif n == "3": emision()
        else:
            print("Opción inválida.")

# Ejecución inicial
menu(0)