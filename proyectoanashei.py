# --- CLASE EQUIPO (Requisito del PDF para diseño de datos) ---
class Equipo:
    def __init__(self, nombre, abreviatura, prefijo, grupo, id_identificador):
        self.nombre = nombre
        self.abreviatura = abreviatura
        self.prefijo = prefijo
        self.grupo = grupo
        self.id = id_identificador # Identificador tipo A1, A2, etc.
        # Estadísticas originales
        self.puntos = 0
        self.gf = 0
        self.gc = 0
        self.am = 0
        self.rj = 0
        self.partidos = []  
        self.plantel = []

    def reset_stats(self):
        self.puntos = 0
        self.gf = 0
        self.gc = 0
        self.am = 0
        self.rj = 0

# Variables globales originales
tablagral = {}
nombre_torneo = ""
fecha_inicio = ""
fecha_fin = ""

# --- TU LÓGICA DE MENÚ ORIGINAL ---
def menu(contador):
    while True:
        # Muestra el nombre del torneo si ya fue ingresado
        print(f"\n--- {nombre_torneo if nombre_torneo else 'SISTEMA MUNDIAL'} ---")
        print("1. Configuración del torneo")
        print("2. Registro de resultados")
        print("3. Emisión de informes")
        print("4. Salir")
        print("5. Simulador")
        
        n = input("Elegí una opción: ")
        opciones = {"1": configuracion, "2": registro, "3": emision, "4": salir, "5": simulador}
        
        # Tu bloqueo de seguridad para la opción 1
        if contador == 1:
            if "1" in opciones:
                del opciones["1"]
            
        if n == "4":
            print("¡Chau! ")
            break 
            
        if n in opciones:
            if n == "1":
                # Ejecuta configuración y guarda el retorno en contador
                contador = opciones[n]() 
            else:
                opciones[n]()
        else:
            print("Valor inválido!!")

def configuracion():
    abc = ["A","B","C","D","E","F","G","H","I","J","L","M"]
    global tablagral, nombre_torneo, fecha_inicio, fecha_fin
    
    nombre_torneo = input("Nombre del Torneo: ")
    fecha_inicio = input("Fecha Inicio: ")
    fecha_fin = input("Fecha Fin: ")
    
    for x in range(12):
        print(f"\n Grupo {abc[x]}")
        equiposdelgrupo = []
        
        for i in range(4):
            nombre = input(f"Nombre selección {i+1}: ")
            abreviatura = input(f"Abreviatura: ").upper()
            prefijo = int(input(f"Prefijo: "))
            
            # Identificador solicitado (A1, A2, etc)
            id_identificador = f"{abc[x]}{i+1}"
            
            # Instanciamos la clase Equipo
            tablagral[nombre] = Equipo(nombre, abreviatura, prefijo, abc[x], id_identificador)
            
            # Tu lógica de lectura de jugadores
            archivo_j = open("jugadores.txt", "r", encoding="utf-8")
            for linea in archivo_j:
                partes = linea.strip().split(",")
                if partes[0] == nombre:
                    tablagral[nombre].plantel.append(partes[1])
            archivo_j.close()

            equiposdelgrupo.append(nombre)
        
        fechapartido(equiposdelgrupo, abc[x])
        
    print("\n✅ Configuración cerrada.")
    return 1

def fechapartido(listaequipos, nombregrupo):
    partidoscreados = [] 
    for equipo1 in listaequipos:
        for equipo2 in listaequipos:
            if equipo1 != equipo2 and (equipo1+equipo2 not in partidoscreados and equipo2+equipo1 not in partidoscreados):
                print(f"--- Partido: {equipo1} vs {equipo2} ---")
                fecha = input(f"Fecha: ")
                hora = input(f"Hora: ")
                
                tablagral[equipo1].partidos.append({"rival": equipo2, "fecha": fecha, "hora": hora, "goles": None, "tarjetas": None})
                tablagral[equipo2].partidos.append({"rival": equipo1, "fecha": fecha, "hora": hora, "goles": None, "tarjetas": None})
                partidoscreados.append(equipo1+equipo2)

def registro():
    partidosmostrados = []
    equipos_nombres = []
    k = input("¿Grupo? (A-M): ").upper()
    
    for nombre in tablagral:
        if tablagral[nombre].grupo == k:
            equipos_nombres.append(nombre)
            
    for equipo1 in equipos_nombres:
        for partido in tablagral[equipo1].partidos:
            equipo2 = partido["rival"]
            if equipo1 + equipo2 not in partidosmostrados and equipo2 + equipo1 not in partidosmostrados:
                g = int(input(f"Goles {equipo1}: "))
                g2 = int(input(f"Goles {equipo2}: "))
                am1 = int(input(f"AM {equipo1}: "))
                rj1 = int(input(f"RJ {equipo1}: "))
                am2 = int(input(f"AM {equipo2}: "))
                rj2 = int(input(f"RJ {equipo2}: "))
                
                partidosmostrados.append(equipo1 + equipo2)
                partidosmostrados.append(equipo2 + equipo1)
                
                partido["goles"] = [g, g2]
                partido["tarjetas"] = [am1, rj1]
                
                for p in tablagral[equipo2].partidos:
                    if p["rival"] == equipo1:
                        p["goles"] = [g2, g]
                        p["tarjetas"] = [am2, rj2]
    print("\nResultados cargados!")

def emision():
    k = input("Ingrese el grupo: ").upper()
    listatemporal = []
    
    for nombre in tablagral:
        equipo = tablagral[nombre]
        if equipo.grupo == k:
            equipo.reset_stats() 
            for partido in equipo.partidos:
                if partido["goles"] is not None:
                    gfp = partido["goles"][0]
                    gcp = partido["goles"][1]
                    
                    equipo.gf += gfp
                    equipo.gc += gcp
                    equipo.am += partido["tarjetas"][0]
                    equipo.rj += partido["tarjetas"][1]
                    
                    if gfp > gcp: equipo.puntos += 3
                    elif gfp == gcp: equipo.puntos += 1
            
            listatemporal.append(nombre)

    # Tu Lógica de Ordenamiento Burbuja
    for x in range(len(listatemporal)):
        for i in range(x+1, len(listatemporal)):
            e1 = tablagral[listatemporal[x]]
            e2 = tablagral[listatemporal[i]]
            
            cambiar = False
            if e1.puntos < e2.puntos:
                cambiar = True
            elif e1.puntos == e2.puntos:
                if e1.gf < e2.gf:
                    cambiar = True
                elif e1.gf == e2.gf:
                    if e1.gc > e2.gc: 
                        cambiar = True
                    elif e1.gc == e2.gc:
                        if e1.prefijo < e2.prefijo: 
                            cambiar = True
            
            if cambiar:
                listatemporal[x], listatemporal[i] = listatemporal[i], listatemporal[x]

    print(f"\nTABLA DEL GRUPO {k} - {nombre_torneo}")
    for nombre in listatemporal:
        e = tablagral[nombre]
        print(f"ID: {e.id} | {nombre}: {e.puntos} PTS | GF: {e.gf} | GC: {e.gc}")

def simulador(): pass
def salir(): pass

# Iniciamos el menú con contador 0
menu(0)