from datetime import datetime

tablagral = {}

def menu(contador):
    while True:
        print("\n1. Configuración del torneo")
        print("2. Registro de resultados")
        print("3. Emisión de informes")
        print("4. Salir")
        print("5. Simulador")
        
        n = input("Elegí una opción: ")
        opciones = {"1": configuracion, "2": registro, "3": emision, "4": salir, "5": simulador}
        
        if contador == 1:
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
    abc = ["A","B","C","D","E","F","G","H","I","J","L","M"]
    global tablagral
    
    for x in range(12):
        print(f"\n Grupo {abc[x]}")
        equiposdelgrupo = []
        
        for i in range(4):
            nombre = input(f"Ingrese el nombre de la selección {i+1}: ")
            abreviatura = input(f"Abreviatura para {nombre} (3 letras): ").upper()
            prefijo = int(input(f"Prefijo telefónico de {nombre}: "))
            tablagral[nombre] = {
                "id": f"{abc[x]}{i+1}",
                "abreviatura": abreviatura,
                "prefijo": prefijo,
                "grupo": abc[x],
                "partidos": [] 
            }
            equiposdelgrupo.append(nombre)
        fechapartido(equiposdelgrupo, abc[x])
        
    print("\n✅ Configuración cerrada exitosamente.")
    return 1

def fechapartido(listaequipos, nombregrupo):
    global tablagral
    partidoscreados = []
    
    for equipo1 in listaequipos:
        for equipo2 in listaequipos:
            if equipo1 != equipo2 and (equipo1+equipo2 not in partidoscreados and equipo2+equipo1 not in partidoscreados):
                while True:
                    fecha = input(f"Fecha {equipo1} vs {equipo2} (DD/MM/AAAA): ")
                    try:
                        datetime.strptime(fecha, "%d/%m/%Y")
                        break
                    except ValueError:
                        print("Formato de fecha inválido.")
                
                while True:
                    hora = input(f"Hora del partido {equipo1} vs {equipo2} (HH:MM): ")
                    try:
                        datetime.strptime(hora, "%H:%M")
                        break
                    except ValueError:
                        print("Formato de hora inválido.")
                
                tablagral[equipo1]["partidos"].append({"rival": equipo2, "fecha": fecha, "hora": hora, "goles": None})
                tablagral[equipo2]["partidos"].append({"rival": equipo1, "fecha": fecha, "hora": hora, "goles": None})
                partidoscreados.append(equipo1+equipo2)


    