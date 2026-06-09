import datetime

# =================================================================
# 1. MODELO DE DATOS (CLASE EQUIPO)
# =================================================================
class Equipo:
    def __init__(self, nombre, abreviatura, prefijo, grupo, id_identificador):
        self.nombre = nombre
        self.abreviatura = abreviatura
        self.prefijo = prefijo
        self.grupo = grupo
        self.id = id_identificador  
        
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

# =================================================================
# 2. BASE DE DATOS GLOBAL
# =================================================================
tablagral = {}        
nombre_torneo = ""
fecha_inicio_obj = None 
fecha_fin_obj = None

paises_mundial = [
    "México", "Sudáfrica", "Corea del Sur", "República Checa", "Canadá", "Bosnia-Herzegovina", 
    "Qatar", "Suiza", "Brasil", "Marruecos", "Haití", "Escocia", "EE. UU.", "Paraguay", 
    "Australia", "Turquía", "Alemania", "Curazao", "Costa de Marfil", "Ecuador", 
    "Países Bajos", "Japón", "Suecia", "Túnez", "Bélgica", "Egipto", "Irán", 
    "Nueva Zelanda", "España", "Uruguay", "Cabo Verde", "Arabia Saudita", "Francia", 
    "Senegal", "Irak", "Noruega", "Argentina", "Argelia", "Austria", "Jordania", 
    "Portugal", "Colombia", "RD Congo", "Uzbekistán", "Inglaterra", "Croacia", 
    "Ghana", "Panamá"
]

# =================================================================
# 3. FUNCIONES DE VALIDACIÓN (BACK-END)
# =================================================================
def validar_fecha_manual(texto_fecha):
    if len(texto_fecha) == 10 and texto_fecha[2] == "/" and texto_fecha[5] == "/":
        dia = int(texto_fecha[0:2])
        mes = int(texto_fecha[3:5])
        anio = int(texto_fecha[6:10])
        if 1 <= dia <= 31 and 1 <= mes <= 12 and anio > 2000:
            return datetime.datetime(anio, mes, dia)
    return None

def asignar_tarjetas(nombre_equipo, tipo_tarjeta):
    equipo = tablagral[nombre_equipo]
    cant = int(input(f"¿Cuántas tarjetas {tipo_tarjeta} para {nombre_equipo}?: "))
    
    for x in range(cant):
        nombres_jugadores = list(equipo.plantel.keys())
        print(f"\nJUGADORES DE {nombre_equipo}:")
        for id in range(len(nombres_jugadores)):
            print(f"{id+1}. {nombres_jugadores[id]}")
        
        sel = int(input(f"Seleccione el número del jugador: "))
        jugador_sel = nombres_jugadores[sel - 1]
        
        equipo.plantel[jugador_sel][tipo_tarjeta] += 1
        if tipo_tarjeta == "AM": equipo.am += 1
        else: equipo.rj += 1

# =================================================================
# 4. PROCESAMIENTO DE DATOS
# =================================================================

def configuracion():
    abc = ["A","B","C","D","E","F","G","H","I","J","K","L"]
    global tablagral, nombre_torneo, fecha_inicio_obj, fecha_fin_obj
    
    nombre_torneo = input("Nombre del Torneo: ")
    
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
            for j in range(len(disponibles)):
                print(f"{j+1}. {disponibles[j]}", end="\t" if (j+1)%3 != 0 else "\n")
            
            opcion = int(input(f"\nElija país {abc[x]}{i+1}: "))
            nombre = disponibles[opcion - 1]
            del disponibles[opcion - 1] 
            
            # --- LECTURA AUTOMÁTICA DE PAISES.TXT ---
            abreviatura = ""
            prefijo = 0
            archivo_p = open("paises.txt", "r", encoding="utf-8")
            for linea in archivo_p:
                datos_p = linea.strip().split(",")
                if datos_p[0].strip() == nombre:
                    abreviatura = datos_p[1].strip()
                    prefijo = int(datos_p[2].strip().replace("+", ""))
            archivo_p.close()
            
            tablagral[nombre] = Equipo(nombre, abreviatura, prefijo, abc[x], f"{abc[x]}{i+1}")
            
            archivo = open("jugadores.txt", "r", encoding="utf-8")
            for linea in archivo:
                datos = linea.strip().split(",")
                if datos[0].strip() == nombre:
                    tablagral[nombre].plantel[datos[1].strip()] = {"AM": 0, "RJ": 0}
            archivo.close()
            equipos_grupo.append(nombre)
        
        fechapartido(equipos_grupo, abc[x])
    return 1 

def fechapartido(lista, grupo):
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
                tablagral[e1].partidos.append({"rival": e2, "fecha": f, "hora": h, "goles": None})
                tablagral[e2].partidos.append({"rival": e1, "fecha": f, "hora": h, "goles": None})
                creados.append(e1+e2)

def registro():
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
    print("\n¡Resultados guardados!")

def emision():
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
    
    for x in range(len(temp)):
        for i in range(x+1, len(temp)):
            if tablagral[temp[x]].puntos < tablagral[temp[i]].puntos:
                temp[x], temp[i] = temp[i], temp[x]

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
        opciones = {"1": configuracion, "2": registro, "3": emision, "4": "salir", "5": "sim"}
        
        if contador == 1 and "1" in opciones:
            del opciones["1"]
            
        if n == "4": break 
            
        if n in opciones:
            if n == "1":
                contador = opciones[n]() 
            else:
                if n == "2": registro()
                elif n == "3": emision()
        else:
            print("Opción inválida.")

menu(0)