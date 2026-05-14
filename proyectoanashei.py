import datetime

# =================================================================
# 1. DEFINICIÓN DE CLASES (Estructura de Datos - Punto 4 del PDF)
# =================================================================
class Equipo:
    def __init__(self, nombre, abreviatura, prefijo, grupo, id_identificador):
        """
        Clase que representa a una selección nacional.
        Agrupa datos de identidad y estadísticas de juego.
        """
        self.nombre = nombre
        self.abreviatura = abreviatura
        self.prefijo = prefijo
        self.grupo = grupo
        self.id = id_identificador  # Identificador único (Ej: A1, B2)
        
        # Estadísticas inicializadas en cero
        self.puntos = 0
        self.pj = 0  # Partidos Jugados
        self.gf = 0  # Goles a Favor
        self.gc = 0  # Goles en Contra
        self.am = 0  # Amarillas
        self.rj = 0  # Rojas
        
        # Listas para almacenar datos complejos
        self.partidos = []  # Diccionarios con rival, fecha, hora y score
        self.plantel = []   # Nombres de jugadores cargados desde archivo

    def reset_stats(self):
        """Limpia las estadísticas antes de recalcular la tabla de posiciones"""
        self.puntos = 0
        self.pj = 0
        self.gf = 0
        self.gc = 0
        self.am = 0
        self.rj = 0

# =================================================================
# 2. VARIABLES GLOBALES Y LISTA DE PAÍSES
# =================================================================
tablagral = {}  # Diccionario principal: { "NombrePaís": objeto_equipo }
nombre_torneo = ""
fecha_inicio = ""
fecha_fin = ""

# Lista de los 48 países para la selección por número
paises_mundial = [
    "Argentina", "Bolivia", "Brasil", "Chile", "Colombia", "Ecuador", "Paraguay", "Perú", "Uruguay", "Venezuela",
    "México", "Estados Unidos", "Canadá", "Costa Rica", "Panamá", "Jamaica", "Honduras", "El Salvador",
    "España", "Francia", "Inglaterra", "Alemania", "Italia", "Portugal", "Holanda", "Bélgica", "Croacia", "Suiza",
    "Japón", "Corea del Sur", "Australia", "Arabia Saudita", "Irán", "Catar",
    "Egipto", "Marruecos", "Senegal", "Túnez", "Argelia", "Nigeria", "Camerún", "Ghana", "Sudáfrica", "Costa de Marfil",
    "Nueva Zelanda", "Polonia", "Dinamarca", "Serbia"
]

# =================================================================
# 3. LÓGICA DEL MENÚ PRINCIPAL
# =================================================================
def menu(contador):
    global nombre_torneo
    while True:
        # Encabezado dinámico
        print(f"\n--- {nombre_torneo if nombre_torneo else 'SISTEMA MUNDIAL FIFA 2026'} ---")
        print("1. Configuración del torneo")
        print("2. Registro de resultados")
        print("3. Emisión de informes (Tabla de Posiciones)")
        print("4. Salir")
        print("5. Simulador")
        
        n = input("Elegí una opción: ")
        opciones = {"1": configuracion, "2": registro, "3": emision, "4": salir, "5": simulador}
        
        # Lógica de bloqueo: Si ya se configuró (contador=1), se borra la opción 1 del diccionario
        if contador == 1:
            if "1" in opciones:
                del opciones["1"]
            
        if n == "4":
            print("Cerrando sistema... ¡Buen viaje!")
            break 
            
        if n in opciones:
            if n == "1":
                # Al ejecutar configuración, devuelve 1 para bloquearla en la siguiente vuelta
                contador = opciones[n]()
            else:
                opciones[n]()
        else:
            print("¡Opción no válida!")

# =================================================================
# 4. FUNCIONES DE LÓGICA (BACK-END)
# =================================================================

def configuracion():
    """Maneja la carga inicial de países, archivos de texto y generación de fixture"""
    abc = ["A","B","C","D","E","F","G","H","I","J","K","L"] # 12 Grupos
    global tablagral, nombre_torneo, fecha_inicio, fecha_fin, paises_mundial
    
    nombre_torneo = input("Nombre del Torneo: ")
    fecha_inicio = input("Fecha Inicio (DD/MM/AAAA): ")
    fecha_fin = input("Fecha Fin (DD/MM/AAAA): ")

    disponibles = list(paises_mundial) # Copia de trabajo para ir eliminando elegidos
    
    for x in range(12): # Recorre los 12 grupos
        print(f"\n--- CONFIGURANDO GRUPO {abc[x]} ---")
        equipos_grupo_actual = []
        
        for i in range(4): # 4 Equipos por grupo
            # Interfaz de selección de países
            print(f"\nElija país para el slot {abc[x]}{i+1}:")
            for j in range(len(disponibles)):
                print(f"{j+1}. {disponibles[j]}", end="\t" if (j+1)%3 != 0 else "\n")
            
            opcion = int(input(f"\nNúmero: "))
            nombre = disponibles[opcion - 1]
            del disponibles[opcion - 1] # Elimina para que no se repita el país
            
            abreviatura = input(f"Abreviatura para {nombre}: ").upper()
            prefijo = int(input(f"Prefijo telefónico: "))
            id_pos = f"{abc[x]}{i+1}" # Genera ID (A1, A2...)
            
            # Crear el objeto y guardarlo en el diccionario global
            tablagral[nombre] = Equipo(nombre, abreviatura, prefijo, abc[x], id_pos)
            
            # LECTURA DE ARCHIVO: Carga de plantel
            try:
                archivo_j = open("jugadores.txt", "r", encoding="utf-8")
                for linea in archivo_j:
                    partes = linea.strip().split(",")
                    if partes[0].strip() == nombre:
                        tablagral[nombre].plantel.append(partes[1].strip())
                archivo_j.close()
            except FileNotFoundError:
                print("Aviso: archivo 'jugadores.txt' no encontrado.")

            equipos_grupo_actual.append(nombre)
        
        # Generar fixture del grupo actual
        fechapartido(equipos_grupo_actual, abc[x])
        
    return 1 # Devuelve 1 para el contador del menú

def fechapartido(listaequipos, nombregrupo):
    """Crea los encuentros entre los 4 equipos de un grupo (6 partidos)"""
    partidos_creados = [] 
    for e1 in listaequipos:
        for e2 in listaequipos:
            if e1 != e2 and (e1+e2 not in partidos_creados and e2+e1 not in partidos_creados):
                print(f"--- Definir Partido: {e1} vs {e2} ---")
                fecha = input(f"Fecha: ")
                hora = input(f"Hora: ")
                
                # Se registra el partido en ambos equipos para sincronización
                tablagral[e1].partidos.append({"rival": e2, "fecha": fecha, "hora": hora, "goles": None, "tarjetas": None})
                tablagral[e2].partidos.append({"rival": e1, "fecha": fecha, "hora": hora, "goles": None, "tarjetas": None})
                partidos_creados.append(e1+e2)

def registro():
    """Carga los resultados de goles y tarjetas para un grupo específico"""
    mostrados = []
    k = input("¿De qué grupo cargar resultados? (A-L): ").upper()
    
    # Filtrar nombres de equipos del grupo k
    nombres = [n for n in tablagral if tablagral[n].grupo == k]
            
    for e1 in nombres:
        for partido in tablagral[e1].partidos:
            e2 = partido["rival"]
            # Evitar pedir el mismo partido dos veces
            if e1 + e2 not in mostrados and e2 + e1 not in mostrados:
                print(f"\n--- Resultado: {e1} vs {e2} ---")
                g1 = int(input(f"Goles {e1}: "))
                g2 = int(input(f"Goles {e2}: "))
                am1 = int(input(f"Amarillas {e1}: "))
                rj1 = int(input(f"Rojas {e1}: "))
                am2 = int(input(f"Amarillas {e2}: "))
                rj2 = int(input(f"Rojas {e2}: "))
                
                mostrados.append(e1 + e2)
                mostrados.append(e2 + e1)
                
                # Guardar datos en el equipo 1
                partido["goles"] = [g1, g2]
                partido["tarjetas"] = [am1, rj1]
                
                # Sincronizar datos en el equipo 2 (Rival)
                for p_rival in tablagral[e2].partidos:
                    if p_rival["rival"] == e1:
                        p_rival["goles"] = [g2, g1]
                        p_rival["tarjetas"] = [am2, rj2]
    print("\nResultados guardados.")

def emision():
    """Calcula estadísticas finales y muestra la tabla de posiciones del grupo"""
    k = input("Ingrese el grupo para ver la tabla: ").upper()
    temporal = []
    
    # 1. Resetear y calcular estadísticas de los equipos del grupo
    for nombre in tablagral:
        equipo = tablagral[nombre]
        if equipo.grupo == k:
            equipo.reset_stats() 
            for p in equipo.partidos:
                if p["goles"] is not None: # Si el partido ya se jugó
                    g_favor, g_contra = p["goles"][0], p["goles"][1]
                    equipo.pj += 1
                    equipo.gf += g_favor
                    equipo.gc += g_contra
                    
                    if g_favor > g_contra: equipo.puntos += 3
                    elif g_favor == g_contra: equipo.puntos += 1
            temporal.append(nombre)

    # 2. Ordenamiento BURBUJA (Criterio: Puntos)
    for x in range(len(temporal)):
        for i in range(x+1, len(temporal)):
            e1, e2 = tablagral[temporal[x]], tablagral[temporal[i]]
            if e1.puntos < e2.puntos:
                temporal[x], temporal[i] = temporal[i], temporal[x]

    # 3. IMPRESIÓN FINAL DE LA TABLA (Formateada para el Front/Usuario)
    print(f"\n--- TABLA DE POSICIONES GRUPO {k} ---")
    print(f"{'ID':<4} {'EQUIPO':<15} {'PJ':<3} {'PTS':<4} {'GF':<3} {'GC':<3}")
    print("-" * 40)
    for nombre in temporal:
        e = tablagral[nombre]
        print(f"{e.id:<4} {nombre:<15} {e.pj:<3} {e.puntos:<4} {e.gf:<3} {e.gc:<3}")

def simulador(): print("Módulo de simulación próximamente...")
def salir(): pass

# =================================================================
# 5. INICIO DE LA APLICACIÓN
# =================================================================
if __name__ == "__main__":
    menu(0) # Inicia con contador en 0 para permitir la configuración inicial