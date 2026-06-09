import tkinter as tk
from tkinter import messagebox
from datetime import datetime

class InterfazMundial:
    def __init__(self, root):
        self.root = root
        self.root.title("FIFA World Cup 2026 - Sistema de Control")
        self.root.geometry("1280x720")
        self.root.resizable(False, False)
        
        # Paleta de Colores Oficiales (Estilo WE ARE 26)
        self.COLOR_TEXTO = "#FFFFFF"       # Blanco puro
        self.COLOR_CIAN = "#00F0FF"        # Cian neón (Acento principal)
        self.COLOR_VERDE = "#00FF66"       # Verde neón (Acento secundario)

        # --- CARGA DE IMÁGENES ---
        try:
            self.img_fondo = tk.PhotoImage(file="fondo.png")
            self.img_btn_config = tk.PhotoImage(file="Configuracion.png")
            self.img_btn_registro = tk.PhotoImage(file="Registro.png")
            self.img_btn_edicion = tk.PhotoImage(file="Emision.png")
            self.img_btn_salir = tk.PhotoImage(file="Salir.png")
        except Exception as e:
            print("Error al cargar las imágenes. Revisa que estén en la misma carpeta:", e)
            self.img_fondo = None
            self.img_btn_config = None
            self.img_btn_registro = None
            self.img_btn_edicion = None
            self.img_btn_salir = None

        # --- CANVAS PRINCIPAL ---
        self.canvas = tk.Canvas(self.root, width=1280, height=720, highlightthickness=0)
        self.canvas.place(x=0, y=0)
        
        # Dibujar fondo si existe
        if self.img_fondo:
            self.canvas.create_image(0, 0, image=self.img_fondo, anchor="nw")

        # Estado del Torneo (Simulado para el Frontend)
        self.torneo_configurado = False 

        # Construir los bloques visuales de forma nativa en el Canvas
        self.crear_zona_titulos()
        self.crear_menu_principal()

    def crear_zona_titulos(self):
        """Dibuja el encabezado obligatorio directamente en el Canvas (Transparente)."""
        # Borde rectangular Cian
        self.canvas.create_rectangle(25, 20, 1255, 130, outline=self.COLOR_CIAN, width=1)

        # Textos del encabezado
        self.canvas.create_text(640, 45, text="Algoritmos y Estructuras de Datos II", fill=self.COLOR_TEXTO, font=("Arial", 20, "bold"), justify="center")
        self.canvas.create_text(640, 75, text="CONTROL DE TORNEO DEPORTIVO", fill=self.COLOR_CIAN, font=("Arial", 16, "bold"), justify="center")
        
        # Identificador del reloj dinámico para actualizarlo por id
        self.id_reloj = self.canvas.create_text(640, 105, fill=self.COLOR_VERDE, font=("Consolas", 11), justify="center")
        
        self.actualizar_reloj()

    def actualizar_reloj(self):
        """Actualiza la fecha y la hora en tiempo real sobre el objeto del Canvas."""
        ahora = datetime.now()
        formato = ahora.strftime("Fecha: %d/%m/%Y   |   Hora: %H:%M:%S")
        self.canvas.itemconfig(self.id_reloj, text=formato)
        self.root.after(1000, self.actualizar_reloj)

    def crear_menu_principal(self):
        """Dibuja las imágenes de los botones y superpone sus textos alineados limpiamente."""
        # Título del Menú (Bajado un poco más para centrar el bloque visual)
        self.canvas.create_text(640, 310, text="MENÚ PRINCIPAL", fill=self.COLOR_TEXTO, font=("Arial Black", 16, "bold"))

        # Configuración de coordenadas
        y_inicial = 380   # Altura del primer botón
        separacion = 85   # Espaciado vertical entre botones
        x_texto = 560     # Coordenada X donde inician los textos 1, 2 y 3

        # --- BOTÓN 1: CONFIGURACIÓN ---
        if self.img_btn_config:
            self.canvas.create_image(640, y_inicial, image=self.img_btn_config)
        btn1_txt = self.canvas.create_text(
            x_texto, y_inicial, 
            text="1. Configuración del Torneo", 
            fill=self.COLOR_TEXTO, 
            font=("Arial", 11, "bold"), 
            anchor="w"
        )
        self.canvas.tag_bind(btn1_txt, "<Button-1>", lambda e: self.abrir_configuracion())

        # --- BOTÓN 2: REGISTRO DE RESULTADOS ---
        if self.img_btn_registro:
            self.canvas.create_image(640, y_inicial + separacion, image=self.img_btn_registro)
        self.btn2_txt = self.canvas.create_text(
            x_texto, y_inicial + separacion, 
            text="2. Registro de Resultados", 
            fill="#888888",  
            font=("Arial", 11, "bold"), 
            anchor="w"
        )
        self.canvas.tag_bind(self.btn2_txt, "<Button-1>", lambda e: self.abrir_resultados())

        # --- BOTÓN 3: EMISIÓN DE INFORMES ---
        if self.img_btn_edicion:
            self.canvas.create_image(640, y_inicial + (separacion * 2), image=self.img_btn_edicion)
        btn3_txt = self.canvas.create_text(
            x_texto, y_inicial + (separacion * 2), 
            text="3. Emisión de Informes", 
            fill=self.COLOR_TEXTO, 
            font=("Arial", 11, "bold"), 
            anchor="w"
        )
        self.canvas.tag_bind(btn3_txt, "<Button-1>", lambda e: self.abrir_informes())

        # --- BOTÓN 4: SALIR (TEXTO CENTRADO) ---
        if self.img_btn_salir:
            self.canvas.create_image(640, y_inicial + (separacion * 3), image=self.img_btn_salir)
        
        # Al quitar anchor="w", el texto "4. Salir" se posiciona al centro de la X (640)
        btn4_txt = self.canvas.create_text(
            640, y_inicial + (separacion * 3), 
            text="4. Salir", 
            fill=self.COLOR_TEXTO, 
            font=("Arial", 11, "bold")
        )
        self.canvas.tag_bind(btn4_txt, "<Button-1>", lambda e: self.root.quit())

    # --- FUNCIONES DE NAVEGACIÓN ---
    
    def abrir_configuracion(self):
        messagebox.showinfo("Configuración", "Abriendo el módulo de Configuración del Torneo...")
        self.torneo_configurado = True
        self.canvas.itemconfig(self.btn2_txt, text="2. Registro de Resultados", fill=self.COLOR_TEXTO)

    def abrir_resultados(self):
        if self.torneo_configurado:
            messagebox.showinfo("Resultados", "Abriendo el módulo de Registro de Resultados...")
        else:
            messagebox.showwarning("Acceso Denegado", "Primero debe completar la Configuración del Torneo (Opción 1).")

    def abrir_informes(self):
        messagebox.showinfo("Informes", "Abriendo el panel de Emisión de Informes...")

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazMundial(root)
    root.mainloop()