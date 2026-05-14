from datetime import datetime

# Estructura principal donde se guardará TODO el torneo
# Clave: Nombre del país | Valor: Diccionario con sus estadísticas y partidos
tablagral = {}

# Variables globales para los datos generales del torneo
nombre_torneo = ""
fecha_inicio = ""
fecha_fin = ""

def menu(contador):
    """ Gestiona la navegación del programa mediante un diccionario de funciones """
    while True:
        print(f"\n--- {nombre_torneo if nombre_torneo else 'SISTEMA MUNDIAL'} ---")
        print("1. Configuración del torneo")
        print("2. Registro de resultados")
        print("3. Emisión de informes")
        print("4. Salir")
        print("5. Simulador")
        
        n = input("Elegí una opción: ")
        opciones = {"1": configuracion, "2": registro, "3": emision, "4": salir, "5": simulador}
        
        # Bloqueo: Si el torneo ya se configuró (contador == 1), no permite volver a entrar a la opción 1
        if contador == 1:
            if "1" in opciones:
                del opciones["1"]
            
        if n == "4":
            print("¡Chau! ")
            break 
            
        if n in opciones:
            if n == "1":
                contador = opciones[n]() # Ejecuta y actualiza el contador
            else:
                opciones[n]()
        else:
            print("Valor inválido!!")

def configuracion():
    """ Inicializa los datos del torneo, equipos y carga jugadores desde archivo """
    abc = ["A","B","C","D","E","F","G","H","I","J","L","M"]
    global tablagral, nombre_torneo, fecha_inicio, fecha_fin
    
    # Datos generales (Requerimiento de inicialización)
    nombre_torneo = input("Nombre del Torneo: ")
    fecha_inicio = input("Fecha Inicio (DD/MM/AAAA): ")
    fecha_fin = input("Fecha Fin (DD/MM/AAAA): ")
    
    for x in range(12): # Recorre los 12 grupos
        print(f"\n Grupo {abc[x]}")
        equiposdelgrupo = []
        
        for i in range(4): # 4 selecciones por grupo
            nombre = input(f"Ingrese el nombre de la selección {i+1}: ")
            abreviatura = input(f"Abreviatura (3 letras): ").upper()
            prefijo = int(input(f"Prefijo telefónico: "))
            
            # Inicializamos el objeto (diccionario) de cada país
            tablagral[nombre] = {
                "id": f"{abc[x]}{i+1}",
                "abreviatura": abreviatura,
                "prefijo": prefijo,
                "grupo": abc[x],
                "partidos": [],
                "gf": 0, "gc": 0, "puntos": 0, "am": 0, "rj": 0,
                "plantel": [] 
            }
            
            # LECTURA DE ARCHIVO: Buscamos jugadores que pertenezcan a este país en el .txt
            try:
                with open("jugadores.txt", "r", encoding="utf-8") as archivo:
                    for linea in archivo:
                        partes = linea.strip().split(",") # Divide por coma: [Pais, Nombre]
                        if partes[0] == nombre:
                            tablagral[nombre]["plantel"].append(partes[1])
            except FileNotFoundError:
                pass 

            equiposdelgrupo.append(nombre)
        
        # Al terminar de cargar el grupo, generamos sus fechas de partidos automáticamente
        fechapartido(equiposdelgrupo, abc[x])
        
    print("\n✅ Configuración cerrada exitosamente.")
    return 1

def fechapartido(listaequipos, nombregrupo):
    """ Genera el fixture cruzando todos contra todos dentro del grupo """
    global tablagral
    partidoscreados = [] 
    for equipo1 in listaequipos:
        for equipo2 in listaequipos:
            # Evita jugar contra uno mismo y partidos duplicados (A vs B y B vs A)
            if equipo1 != equipo2 and (equipo1+equipo2 not in partidoscreados and equipo2+equipo1 not in partidoscreados):
                print(f"--- Partido: {equipo1} vs {equipo2} ---")
                fecha = input(f"Fecha (DD/MM/AAAA): ")
                hora = input(f"Hora (HH:MM): ")
                
                # Se guarda el partido en ambos equipos (Espejo)
                # 'goles' y 'tarjetas' inician en None hasta que se jueguen
                tablagral[equipo1]["partidos"].append({"rival": equipo2, "fecha": fecha, "hora": hora, "goles": None, "tarjetas": None})
                tablagral[equipo2]["partidos"].append({"rival": equipo1, "fecha": fecha, "hora": hora, "goles": None, "tarjetas": None})
                partidoscreados.append(equipo1+equipo2)

def registro():
    """ Carga los resultados de los partidos de un grupo específico """
    partidosmostrados = []
    equipos = []
    k = input("¿De qué grupo cargar resultados? (A-M): ").upper()
    
    for nombre in tablagral:
        if tablagral[nombre]["grupo"] == k:
            equipos.append(nombre)
            
    for equipo1 in equipos:
        for partido in tablagral[equipo1]["partidos"]:
            equipo2 = partido["rival"]
            # Solo pedimos el resultado una vez por cada par de equipos
            if equipo1 + equipo2 not in partidosmostrados and equipo2 + equipo1 not in partidosmostrados:
                g = int(input(f"Goles de {equipo1}: "))
                g2 = int(input(f"Goles de {equipo2}: "))
                am1 = int(input(f"Amarillas {equipo1}: "))
                rj1 = int(input(f"Rojas {equipo1}: "))
                am2 = int(input(f"Amarillas {equipo2}: "))
                rj2 = int(input(f"Rojas {equipo2}: "))
                
                partidosmostrados.append(equipo1 + equipo2)
                partidosmostrados.append(equipo2 + equipo1)
                
                # Actualizamos la info en el equipo local
                partido["goles"] = [g, g2]
                partido["tarjetas"] = [am1, rj1]
                
                # Buscamos el mismo partido en el equipo rival para actualizarlo también
                for p in tablagral[equipo2]["partidos"]:
                    if p["rival"] == equipo1:
                        p["goles"] = [g2, g]
                        p["tarjetas"] = [am2, rj2]
    print("\n ¡Resultados cargados!")

def emision():
    """ Calcula estadísticas y ordena la tabla con criterios de desempate """
    k = input("Ingrese el grupo: ").upper()
    listatemporal = []
    
    # 1. CÁLCULO DE ESTADÍSTICAS (Loop de procesamiento)
    for nombre in tablagral:
        if tablagral[nombre]["grupo"] == k:
            puntos = golesf = golesc = amarillas = rojas = 0
            for partido in tablagral[nombre]["partidos"]:
                if partido["goles"] is not None:
                    gfp = partido["goles"][0] # Goles a favor en el partido
                    gcp = partido["goles"][1] # Goles en contra en el partido
                    golesf += gfp
                    golesc += gcp
                    amarillas += partido["tarjetas"][0]
                    rojas += partido["tarjetas"][1]
                    
                    if gfp > gcp: puntos += 3
                    elif gfp == gcp: puntos += 1
            
            # Guardamos los resultados finales en el diccionario principal
            tablagral[nombre].update({"puntos": puntos, "gf": golesf, "gc": golesc, "am": amarillas, "rj": rojas})
            listatemporal.append(nombre)

    # 2. ORDENAMIENTO BURBUJA CON CRITERIOS DE DESEMPATE
    for x in range(len(listatemporal)):
        for i in range(x+1, len(listatemporal)):
            e1, e2 = listatemporal[x], listatemporal[i]
            
            cambiar = False
            # Criterio 1: Puntos
            if tablagral[e1]["puntos"] < tablagral[e2]["puntos"]:
                cambiar = True
            elif tablagral[e1]["puntos"] == tablagral[e2]["puntos"]:
                # Criterio 2: Goles a Favor
                if tablagral[e1]["gf"] < tablagral[e2]["gf"]:
                    cambiar = True
                elif tablagral[e1]["gf"] == tablagral[e2]["gf"]:
                    # Criterio 3: Goles en Contra (Menos es mejor)
                    if tablagral[e1]["gc"] > tablagral[e2]["gc"]:
                        cambiar = True
                    elif tablagral[e1]["gc"] == tablagral[e2]["gc"]:
                        # Criterio 4: Prefijo (Como sorteo aleatorio final)
                        if tablagral[e1]["prefijo"] < tablagral[e2]["prefijo"]:
                            cambiar = True
            
            if cambiar:
                listatemporal[x], listatemporal[i] = listatemporal[i], listatemporal[x]

    # 3. OUTPUT FINAL (Presentación de datos)
    print(f"\nTABLA DEL GRUPO {k} - {nombre_torneo}")
    for nombre in listatemporal:
        p = tablagral[nombre]
        print(f"{nombre}: {p['puntos']} PTS | GF: {p['gf']} | GC: {p['gc']} | AM: {p['am']} | RJ: {p['rj']}")


# Iniciamos el programa
menu(0)
        