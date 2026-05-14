from datetime import datetime

# Estructura principal donde se guardará TODO el torneo
# Clave: Nombre del país | Valor: Diccionario con sus estadísticas y partidos
tablagral = {}

# Variables globales para los datos generales del torneo
nombre_torneo = ""
fecha_inicio = ""
fecha_fin = ""

def menu(contador):
    """ 
    Maneja el flujo principal del programa. 
    Usa un diccionario llamado 'opciones' para ejecutar funciones según la entrada del usuario.
    """
    while True:
        # Muestra el nombre del torneo si ya fue ingresado, sino muestra un genérico
        print(f"\n--- {nombre_torneo if nombre_torneo else 'SISTEMA MUNDIAL'} ---")
        print("1. Configuración del torneo")
        print("2. Registro de resultados")
        print("3. Emisión de informes")
        print("4. Salir")
        print("5. Simulador")
        
        n = input("Elegí una opción: ")
        opciones = {"1": configuracion, "2": registro, "3": emision, "4": salir, "5": simulador}
        
        # Bloqueo de seguridad: Si ya se configuró el torneo (contador == 1), 
        # se elimina la opción 1 del diccionario para que no se pueda sobreescribir.
        if contador == 1:
            if "1" in opciones:
                del opciones["1"]
            
        if n == "4":
            print("¡Chau! ")
            break 
            
        if n in opciones:
            if n == "1":
                # Si elige 1, ejecutamos y guardamos el retorno (1) en contador
                contador = opciones[n]() 
            else:
                opciones[n]()
        else:
            print("Valor inválido!!")

def configuracion():
    """ 
    Captura los datos del torneo y de las 48 selecciones (12 grupos de 4).
    También intenta cargar jugadores desde un archivo externo.
    """
    abc = ["A","B","C","D","E","F","G","H","I","J","L","M"]
    global tablagral, nombre_torneo, fecha_inicio, fecha_fin
    
    # Pedimos los datos iniciales que irán en los encabezados
    nombre_torneo = input("Nombre del Torneo: ")
    fecha_inicio = input("Fecha Inicio (DD/MM/AAAA): ")
    fecha_fin = input("Fecha Fin (DD/MM/AAAA): ")
    
    for x in range(12): # Recorre cada uno de los 12 grupos
        print(f"\n Grupo {abc[x]}")
        equiposdelgrupo = []
        
        for i in range(4): # Carga los 4 equipos de cada grupo
            nombre = input(f"Ingrese el nombre de la selección {i+1}: ")
            abreviatura = input(f"Abreviatura (3 letras): ").upper()
            prefijo = int(input(f"Prefijo telefónico: "))
            
            # Creamos la ficha técnica de cada país dentro del diccionario tablagral
            tablagral[nombre] = {
                "id": f"{abc[x]}{i+1}",
                "abreviatura": abreviatura,
                "prefijo": prefijo,
                "grupo": abc[x],
                "partidos": [], # Aquí se guardarán los resultados después
                "gf": 0, "gc": 0, "puntos": 0, "am": 0, "rj": 0,
                "plantel": [] 
            }
            
            # LECTURA DE ARCHIVO: Si el nombre del país coincide con el del .txt, agrega el jugador
            try:
                with open("jugadores.txt", "r", encoding="utf-8") as archivo:
                    for linea in archivo:
                        partes = linea.strip().split(",") # Divide la línea por la coma
                        if partes[0] == nombre:
                            tablagral[nombre]["plantel"].append(partes[1])
            except FileNotFoundError:
                pass # Si el archivo no existe, no hace nada y continúa

            equiposdelgrupo.append(nombre)
        
        # Al terminar de cargar los 4 equipos, genera el calendario de ese grupo
        fechapartido(equiposdelgrupo, abc[x])
        
    print("\n✅ Configuración cerrada exitosamente.")
    return 1

def fechapartido(listaequipos, nombregrupo):
    """ Genera el fixture 'todos contra todos' dentro de un grupo """
    global tablagral
    partidoscreados = [] 
    for equipo1 in listaequipos:
        for equipo2 in listaequipos:
            # Evita que un equipo juegue contra sí mismo y que se repita el partido (A vs B y B vs A)
            if equipo1 != equipo2 and (equipo1+equipo2 not in partidoscreados and equipo2+equipo1 not in partidoscreados):
                print(f"--- Partido: {equipo1} vs {equipo2} ---")
                fecha = input(f"Fecha (DD/MM/AAAA): ")
                hora = input(f"Hora (HH:MM): ")
                
                # Guarda el partido en la lista de ambos equipos (datos espejo)
                tablagral[equipo1]["partidos"].append({"rival": equipo2, "fecha": fecha, "hora": hora, "goles": None, "tarjetas": None})
                tablagral[equipo2]["partidos"].append({"rival": equipo1, "fecha": fecha, "hora": hora, "goles": None, "tarjetas": None})
                partidoscreados.append(equipo1+equipo2)

def registro():
    """ Permite al usuario cargar los goles y tarjetas de los partidos de un grupo """
    partidosmostrados = []
    equipos = []
    k = input("¿De qué grupo cargar resultados? (A-M): ").upper()
    
    # Filtra los equipos que pertenecen al grupo ingresado
    for nombre in tablagral:
        if tablagral[nombre]["grupo"] == k:
            equipos.append(nombre)
            
    for equipo1 in equipos:
        for partido in tablagral[equipo1]["partidos"]:
            equipo2 = partido["rival"]
            # Control para no pedir dos veces el mismo resultado
            if equipo1 + equipo2 not in partidosmostrados and equipo2 + equipo1 not in partidosmostrados:
                g = int(input(f"Goles de {equipo1}: "))
                g2 = int(input(f"Goles de {equipo2}: "))
                am1 = int(input(f"Amarillas {equipo1}: "))
                rj1 = int(input(f"Rojas {equipo1}: "))
                am2 = int(input(f"Amarillas {equipo2}: "))
                rj2 = int(input(f"Rojas {equipo2}: "))
                
                partidosmostrados.append(equipo1 + equipo2)
                partidosmostrados.append(equipo2 + equipo1)
                
                # Actualiza los goles y tarjetas en el equipo 1
                partido["goles"] = [g, g2]
                partido["tarjetas"] = [am1, rj1]
                
                # Busca el partido correspondiente en el equipo rival para actualizarlo también
                for p in tablagral[equipo2]["partidos"]:
                    if p["rival"] == equipo1:
                        p["goles"] = [g2, g]
                        p["tarjetas"] = [am2, rj2]
    print("\n ¡Resultados cargados!")

def emision():
    """ 
    Calcula los puntos totales basándose en los goles registrados 
    y muestra la tabla de posiciones ordenada por criterios de desempate.
    """
    k = input("Ingrese el grupo: ").upper()
    listatemporal = []
    
    # 1. Bucle para procesar cada equipo del grupo seleccionado
    for nombre in tablagral:
        if tablagral[nombre]["grupo"] == k:
            puntos = golesf = golesc = amarillas = rojas = 0
            # Recorre los partidos de este equipo para sumar sus estadísticas
            for partido in tablagral[nombre]["partidos"]:
                if partido["goles"] is not None:
                    gfp = partido["goles"][0] # Goles a Favor en este partido
                    gcp = partido["goles"][1] # Goles en Contra en este partido
                    amp = partido["tarjetas"][0]
                    rjp = partido["tarjetas"][1]
                    
                    golesf += gfp
                    golesc += gcp
                    amarillas += amp
                    rojas += rjp
                    
                    # Lógica de puntos: Gana (3), Empata (1), Pierde (0)
                    if gfp > gcp: puntos += 3
                    elif gfp == gcp: puntos += 1
            
            # Actualiza el diccionario global con los cálculos nuevos
            tablagral[nombre]["puntos"] = puntos
            tablagral[nombre]["gf"] = golesf
            tablagral[nombre]["gc"] = golesc
            tablagral[nombre]["am"] = amarillas
            tablagral[nombre]["rj"] = rojas
            # Agrega el nombre del equipo a una lista para ordenarla después
            listatemporal.append(nombre)

    # 2. Ordenamiento Burbuja: Compara equipos y los intercambia de lugar según los criterios
    for x in range(len(listatemporal)):
        for i in range(x+1, len(listatemporal)):
            equipo1 = listatemporal[x]
            equipo2 = listatemporal[i]
            
            # Criterio principal: Puntos
            if tablagral[equipo1]["puntos"] < tablagral[equipo2]["puntos"]:
                listatemporal[x], listatemporal[i] = listatemporal[i], listatemporal[x]
            # Si empatan en puntos, mira Goles a Favor
            elif tablagral[equipo1]["puntos"] == tablagral[equipo2]["puntos"]:
                if tablagral[equipo1]["gf"] < tablagral[equipo2]["gf"]:
                    listatemporal[x], listatemporal[i] = listatemporal[i], listatemporal[x]
                # Si empatan en goles a favor, mira Goles en Contra
                elif tablagral[equipo1]["gf"] == tablagral[equipo2]["gf"]:
                    if tablagral[equipo1]["gc"] < tablagral[equipo2]["gc"]:
                        listatemporal[x], listatemporal[i] = listatemporal[i], listatemporal[x]
                    # Si empatan en todo, usa el Prefijo como desempate final
                    elif tablagral[equipo1]["gc"] == tablagral[equipo2]["gc"]:
                        if tablagral[equipo1]["prefijo"] < tablagral[equipo2]["prefijo"]:
                            listatemporal[x], listatemporal[i] = listatemporal[i], listatemporal[x]

    # 3. Muestra los resultados en pantalla
    print(f"\nTABLA DEL GRUPO {k} - {nombre_torneo}")
    for nombre in listatemporal:
        p = tablagral[nombre]
        print(f"{nombre}: {p['puntos']} PTS | GF: {p['gf']} | GC: {p['gc']} | AM: {p['am']} | RJ: {p['rj']}")

# Funciones vacías para evitar errores de ejecución
def simulador(): 
def salir(): 

# Llama al menú para iniciar el programa
menu(0)
        