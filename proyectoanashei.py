# --- CLASE EQUIPO ---
class Equipo:
    def __init__(self, nombre, abreviatura, prefijo, grupo, id_identificador):
        self.nombre = nombre
        self.abreviatura = abreviatura
        self.prefijo = prefijo
        self.grupo = grupo
        self.id = id_identificador
        self.puntos = 0
        self.pj = 0  # Partidos Jugados
        self.gf = 0
        self.gc = 0
        self.am = 0
        self.rj = 0
        self.partidos = []  
        self.plantel = []

    def reset_stats(self):
        self.puntos = 0
        self.pj = 0
        self.gf = 0
        self.gc = 0
        self.am = 0
        self.rj = 0

# --- VARIABLES GLOBALES ---
tablagral = {}
nombre_torneo = ""
fecha_inicio = ""
fecha_fin = ""

paises_mundial = [
    "Argentina", "Bolivia", "Brasil", "Chile", "Colombia", "Ecuador", "Paraguay", "Perú", "Uruguay", "Venezuela",
    "México", "Estados Unidos", "Canadá", "Costa Rica", "Panamá", "Jamaica", "Honduras", "El Salvador",
    "España", "Francia", "Inglaterra", "Alemania", "Italia", "Portugal", "Holanda", "Bélgica", "Croacia", "Suiza",
    "Japón", "Corea del Sur", "Australia", "Arabia Saudita", "Irán", "Catar",
    "Egipto", "Marruecos", "Senegal", "Túnez", "Argelia", "Nigeria", "Camerún", "Ghana", "Sudáfrica", "Costa de Marfil",
    "Nueva Zelanda", "Polonia", "Dinamarca", "Serbia"
]

def menu(contador):
    global nombre_torneo
    while True:
        print(f"\n--- {nombre_torneo if nombre_torneo else 'SISTEMA MUNDIAL'} ---")
        print("1. Configuración del torneo")
        print("2. Registro de resultados")
        print("3. Emisión de informes")
        print("4. Salir")
        print("5. Simulador")
        
        n = input("Elegí una opción: ")
        opciones = {"1": configuracion, "2": registro, "3": emision, "4": salir, "5": simulador}
        
        if contador == 1:
            if "1" in opciones:
                del opciones["1"]
            
        if n == "4":
            print("¡Chau! ")
            break 
            
        if n in opciones:
            if n == "1":
                contador = opciones[n]()
            else:
                opciones[n]()
        else:
            print("Valor inválido!!")

def configuracion():
    abc = ["A","B","C","D","E","F","G","H","I","J","K","L"]
    global tablagral, nombre_torneo, fecha_inicio, fecha_fin, paises_mundial
    
    nombre_torneo = input("Nombre del Torneo: ")
    fecha_inicio = input("Fecha Inicio: ")
    fecha_fin = input("Fecha Fin: ")

    disponibles = list(paises_mundial)
    
    for x in range(12):
        print(f"\n--- GRUPO {abc[x]} ---")
        equiposdelgrupo = []
        
        for i in range(4):
            print(f"\nSeleccione país para {abc[x]}{i+1}:")
            for j in range(len(disponibles)):
                print(f"{j+1}. {disponibles[j]}", end="\t" if (j+1)%3 != 0 else "\n")
            
            opcion = int(input(f"\nNúmero: "))
            indice = opcion - 1
            nombre = disponibles[indice]
            del disponibles[indice]
            
            abreviatura = input(f"Abreviatura para {nombre}: ").upper()
            prefijo = int(input(f"Prefijo: "))
            id_pos = f"{abc[x]}{i+1}"
            
            tablagral[nombre] = Equipo(nombre, abreviatura, prefijo, abc[x], id_pos)
            
            archivo_j = open("jugadores.txt", "r", encoding="utf-8")
            for linea in archivo_j:
                partes = linea.strip().split(",")
                if partes[0].strip() == nombre:
                    tablagral[nombre].plantel.append(partes[1].strip())
            archivo_j.close()

            equiposdelgrupo.append(nombre)
        
        fechapartido(equiposdelgrupo, abc[x])
        
    print("\n✅ Configuración terminada.")
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
    k = input("¿Grupo? (A-L): ").upper()
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
    k = input("Ingrese grupo: ").upper()
    listatemporal = []
    for nombre in tablagral:
        equipo = tablagral[nombre]
        if equipo.grupo == k:
            equipo.reset_stats() 
            for partido in equipo.partidos:
                if partido["goles"] is not None:
                    gfp, gcp = partido["goles"][0], partido["goles"][1]
                    equipo.pj += 1 # Suma partido jugado
                    equipo.gf += gfp
                    equipo.gc += gcp
                    equipo.am += partido["tarjetas"][0]
                    equipo.rj += partido["tarjetas"][1]
                    if gfp > gcp: equipo.puntos += 3
                    elif gfp == gcp: equipo.puntos += 1
            listatemporal.append(nombre)

    # Burbuja
    for x in range(len(listatemporal)):
        for i in range(x+1, len(listatemporal)):
            e1, e2 = tablagral[listatemporal[x]], tablagral[listatemporal[i]]
            if e1.puntos < e2.puntos:
                listatemporal[x], listatemporal[i] = listatemporal[i], listatemporal[x]

    print(f"\n--- TABLA DE POSICIONES GRUPO {k} ---")
    print(f"{'ID':<4} {'EQUIPO':<15} {'PJ':<3} {'PTS':<4} {'GF':<3} {'GC':<3}")
    print("-" * 40)
    for nombre in listatemporal:
        e = tablagral[nombre]
        # Imprime todos los datos solicitados
        print(f"{e.id:<4} {nombre:<15} {e.pj:<3} {e.puntos:<4} {e.gf:<3} {e.gc:<3}")

def simulador(): pass
def salir(): pass

menu(0)