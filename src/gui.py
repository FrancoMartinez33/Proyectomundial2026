# ─────────────────────────────────────────────────────────────
#  GUI – Interfaz gráfica del Sistema de Control de Torneo
#  Librerías: solo tkinter + calendar (biblioteca estándar)
# ─────────────────────────────────────────────────────────────

import tkinter as tk
from tkinter import messagebox, ttk
import calendar
import random
from datetime import datetime

# Módulos propios del paquete src/
from . import data_store 
from .data_store import confederaciones, jugadores_por_equipo
from .models import Equipo
from .services import (configuracion, generar_pares_grupo, calcular_tabla_grupo,
                       randomizar_grupos, generar_informe_equipo, guardar_informe_txt,
                       generar_reporte_completo, partidos_en_fecha, resultados_equipo,
                       proximo_partido_equipo, todas_tablas, calcular_terceros,
                       generar_ronda32, procesar_resultados_ronda, obtener_estado_eliminatorias,
                       reiniciar_eliminatorias, obtener_maximo_avance)
from .persistence import guardar_datos, cargar_datos


# ─────────────────────────────────────────────────────────────
#  CalendarPopup – Ventana emergente con calendario mensual
#  Permite navegar meses con ◀ ▶ y elegir un día haciendo clic
# ─────────────────────────────────────────────────────────────

class CalendarPopup:
    MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    DIAS = ["Lun", "Mar", "Mi\u00e9", "Jue", "Vie", "S\u00e1b", "Dom"]

    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback
        hoy = datetime.now()
        self.anio = hoy.year
        self.mes = hoy.month
        self.win = None

    def _abrir(self):
        self.win = tk.Toplevel(self.parent)
        self.win.title("Seleccionar fecha")
        centrar_ventana(self.win, 280, 260)
        self.win.configure(bg=C["bg"])
        self.win.resizable(False, False)
        self.win.transient(self.parent)
        self.win.grab_set()

        nav = tk.Frame(self.win, bg=C["bg"])
        nav.pack(pady=(10, 5))

        tk.Button(nav, text="\u25c0", command=self._mes_prev,
                  bg=C["gray"], fg=C["fg"], bd=0, width=3,
                  font=("Arial", 10, "bold"), cursor="hand2").pack(side="left", padx=5)
        self.lbl_mes = tk.Label(nav, text="", fg=C["cyan"], bg=C["bg"],
                                font=("Arial", 11, "bold"), width=20)
        self.lbl_mes.pack(side="left")
        tk.Button(nav, text="\u25b6", command=self._mes_next,
                  bg=C["gray"], fg=C["fg"], bd=0, width=3,
                  font=("Arial", 10, "bold"), cursor="hand2").pack(side="left", padx=5)

        dias_f = tk.Frame(self.win, bg=C["bg"])
        dias_f.pack(padx=10)
        for i, d in enumerate(self.DIAS):
            color = C["green"] if i >= 5 else C["fg"]
            tk.Label(dias_f, text=d, fg=color, bg=C["bg"],
                     font=("Arial", 9, "bold"), width=4).grid(row=0, column=i, pady=4)

        self.grid_frame = tk.Frame(self.win, bg=C["bg"])
        self.grid_frame.pack(padx=10, pady=(0, 10))
        self._dibujar_mes()

    def _dibujar_mes(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()
        self.lbl_mes.config(text=f"{self.MESES[self.mes-1]} {self.anio}")

        cal = calendar.monthcalendar(self.anio, self.mes)
        for r, semana in enumerate(cal):
            for c, dia in enumerate(semana):
                if dia == 0:
                    tk.Label(self.grid_frame, text="", bg=C["bg"], width=4).grid(row=r, column=c)
                else:
                    btn = tk.Button(self.grid_frame, text=str(dia),
                                    bg=C["card"], fg=C["fg"], bd=0, width=4,
                                    font=("Arial", 9), cursor="hand2",
                                    activebackground=C["cyan"], activeforeground="#000")
                    btn.grid(row=r, column=c, padx=1, pady=1)
                    btn.config(command=lambda d=dia: self._seleccionar(d))

    def _mes_prev(self):
        if self.mes == 1:
            self.mes = 12
            self.anio -= 1
        else:
            self.mes -= 1
        self._dibujar_mes()

    def _mes_next(self):
        if self.mes == 12:
            self.mes = 1
            self.anio += 1
        else:
            self.mes += 1
        self._dibujar_mes()

    def _seleccionar(self, dia):
        self.callback(f"{dia:02d}/{self.mes:02d}/{self.anio}")
        self.win.destroy()


# ─────────────────────────────────────────────────────────────
#  DateEntry – Campo de fecha con botón que abre el calendario
# ─────────────────────────────────────────────────────────────

class DateEntry(tk.Frame):
    def __init__(self, parent, label, **kw):
        super().__init__(parent, **kw)
        self.configure(bg=C["bg"])
        tk.Label(self, text=label, fg=C["fg"], bg=C["bg"],
                 font=("Arial", 10)).pack(anchor="w")
        row = tk.Frame(self, bg=C["bg"])
        row.pack(fill="x")
        self.lbl_fecha = tk.Label(row, text="DD/MM/AAAA", fg=C["disabled"],
                                  bg=C["input_bg"], font=("Arial", 10),
                                  anchor="w", padx=8, pady=4, relief="flat")
        self.lbl_fecha.pack(side="left", fill="x", expand=True)
        tk.Button(row, text="\U0001f4c5", command=self._abrir_calendario,
                  bg=C["gray"], fg=C["fg"], bd=0, width=3,
                  font=("Arial", 10), cursor="hand2").pack(side="right", padx=(4, 0))

    def _abrir_calendario(self):
        cp = CalendarPopup(self, self._set_fecha)
        cp._abrir()

    def _set_fecha(self, fecha):
        self.lbl_fecha.config(text=fecha, fg="white")

    def get(self):
        txt = self.lbl_fecha.cget("text")
        return txt if txt != "DD/MM/AAAA" else ""


# ─────────────────────────────────────────────────────────────
#  C – Paleta de colores (constantes de diseño)
# ─────────────────────────────────────────────────────────────

C = {
    "bg": "#0A0A0A",
    "fg": "#FFFFFF",
    "cyan": "#00F0FF",
    "green": "#00FF66",
    "gray": "#222222",
    "disabled": "#555555",
    "card": "#1A1A1A",
    "input_bg": "#2C2C2C",
}


# ─────────────────────────────────────────────────────────────
#  centrar_ventana – Posiciona una ventana en medio de la pantalla
# ─────────────────────────────────────────────────────────────

def centrar_ventana(win, ancho, alto):
    win.update_idletasks()
    pantalla_ancho = win.winfo_screenwidth()
    pantalla_alto = win.winfo_screenheight()
    x = (pantalla_ancho - ancho) // 2
    y = (pantalla_alto - alto) // 2
    win.geometry(f"{ancho}x{alto}+{x}+{y}")


# ─────────────────────────────────────────────────────────────
#  InterfazMundial – Clase principal de la aplicación
# ─────────────────────────────────────────────────────────────

class InterfazMundial:

    def __init__(self, root):
        self.root = root
        self.root.title("FIFA World Cup 2026 - Sistema de Control")
        self.root.geometry("1280x720")
        self.root.resizable(False, False)
        
        # Paleta de Colores Oficiales (Estilo WE ARE 26)
        self.COLOR_TEXTO = C["fg"]           # Blanco puro
        self.COLOR_CIAN = C["cyan"]          # Cian neón (Acento principal)
        self.COLOR_VERDE = C["green"]        # Verde neón (Acento secundario)
        self.COLOR_BG = C["bg"]              # Fondo oscuro

        self.torneo_configurado = False
        self.disponibles = set()
        self.asignaciones = {}
        self.datos_config = None
        
        # --- CARGA DE IMÁGENES ---
        self.img_fondo = None
        self.img_btn_config = None
        self.img_btn_registro = None
        self.img_btn_edicion = None
        self.img_btn_salir = None
        self._cargar_imagenes()

        # --- CANVAS PRINCIPAL ---
        self.canvas = tk.Canvas(self.root, width=1280, height=720, highlightthickness=0, bg=self.COLOR_BG)
        self.canvas.place(x=0, y=0)
        
        # Dibujar fondo si existe
        if self.img_fondo:
            self.canvas.create_image(0, 0, image=self.img_fondo, anchor="nw")

        self.crear_zona_titulos()
        self.crear_menu_principal()

        cargar_datos()
        if data_store.config_guardada:
            self.torneo_configurado = True
            self._habilitar_btn2()

        self.root.protocol("WM_DELETE_WINDOW", self._salir_guardando)

    # ── CARGAR IMÁGENES ────────────────────────

    def _cargar_imagenes(self):
        try:
            from pathlib import Path
            # Buscar en la carpeta src o en Proyecto_Algo 2_Interfaz
            paths_posibles = [
                Path(__file__).parent,  # src/
                Path(__file__).parent.parent / "Proyecto_Algo 2_Interfaz"  # Proyecto_Algo 2_Interfaz/
            ]
            
            img_files = {
                "fondo.png": None,
                "Configuracion.png": None,
                "Registro.png": None,
                "Emision.png": None,
                "Salir.png": None
            }
            
            for path in paths_posibles:
                if not path.exists():
                    continue
                for filename in img_files.keys():
                    img_path = path / filename
                    if img_path.exists() and img_files[filename] is None:
                        try:
                            img = tk.PhotoImage(file=str(img_path))
                            img_files[filename] = img
                        except Exception as e:
                            print(f"No se pudo cargar {filename}: {e}")
            
            self.img_fondo = img_files.get("fondo.png")
            self.img_btn_config = img_files.get("Configuracion.png")
            self.img_btn_registro = img_files.get("Registro.png")
            self.img_btn_edicion = img_files.get("Emision.png")
            self.img_btn_salir = img_files.get("Salir.png")
            
        except Exception as e:
            print(f"Advertencia: No se pudieron cargar las imágenes. Continuando sin ellas. ({e})")

    # ── HEADER ──────────────────────────────────

    def crear_zona_titulos(self):
        # Borde rectangular Cian
        self.canvas.create_rectangle(25, 20, 1255, 130, outline=self.COLOR_CIAN, width=2)

        # Textos del encabezado
        self.canvas.create_text(640, 45, text="Algoritmos y Estructuras de Datos II", 
                               fill=self.COLOR_TEXTO, font=("Arial", 20, "bold"), justify="center")
        self.canvas.create_text(640, 75, text="CONTROL DE TORNEO DEPORTIVO", 
                               fill=self.COLOR_CIAN, font=("Arial", 16, "bold"), justify="center")
        
        # Identificador del reloj dinámico para actualizarlo por id
        self.id_reloj = self.canvas.create_text(640, 105, fill=self.COLOR_VERDE, 
                                               font=("Consolas", 11), justify="center")
        
        self.actualizar_reloj()

    def actualizar_reloj(self):
        ahora = datetime.now()
        formato = ahora.strftime("Fecha: %d/%m/%Y   |   Hora: %H:%M:%S")
        self.canvas.itemconfig(self.id_reloj, text=formato)
        self.root.after(1000, self.actualizar_reloj)

    # ── MENÚ PRINCIPAL ───────────────────────────

    def crear_menu_principal(self):
        # Título del Menú
        self.canvas.create_text(640, 200, text="MENÚ PRINCIPAL", 
                               fill=self.COLOR_TEXTO, font=("Arial Black", 14, "bold"))

        # Configuración de coordenadas (reducidas para que quepan todos los botones)
        y_inicial = 250
        separacion = 70  # Reducido de 85 a 70
        x_texto = 560

        # --- BOTÓN 1: CONFIGURACIÓN ---
        if self.img_btn_config:
            self.canvas.create_image(640, y_inicial, image=self.img_btn_config)
        btn1_txt = self.canvas.create_text(
            x_texto, y_inicial, 
            text="1. Configuración del Torneo", 
            fill=self.COLOR_TEXTO, 
            font=("Arial", 10, "bold"), 
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
            font=("Arial", 10, "bold"), 
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
            font=("Arial", 10, "bold"), 
            anchor="w"
        )
        self.canvas.tag_bind(btn3_txt, "<Button-1>", lambda e: self.abrir_informes())

        # --- BOTÓN 4: SIMULADOR ---
        if self.img_btn_edicion:
            self.canvas.create_image(640, y_inicial + (separacion * 3), image=self.img_btn_edicion)
        btn4_txt = self.canvas.create_text(
            x_texto, y_inicial + (separacion * 3), 
            text="4. Simulador de Partidos", 
            fill=self.COLOR_TEXTO, 
            font=("Arial", 10, "bold"), 
            anchor="w"
        )
        self.canvas.tag_bind(btn4_txt, "<Button-1>", lambda e: self.abrir_simulador())

        # --- BOTÓN 5: FASE ELIMINATORIA ---
        if self.img_btn_edicion:
            self.canvas.create_image(640, y_inicial + (separacion * 4), image=self.img_btn_edicion)
        btn5_txt = self.canvas.create_text(
            x_texto, y_inicial + (separacion * 4), 
            text="5. Fase Eliminatoria", 
            fill=self.COLOR_TEXTO, 
            font=("Arial", 10, "bold"), 
            anchor="w"
        )
        self.canvas.tag_bind(btn5_txt, "<Button-1>", lambda e: self.abrir_eliminatorias())

        # --- BOTÓN 6: SALIR ---
        if self.img_btn_salir:
            self.canvas.create_image(640, y_inicial + (separacion * 5), image=self.img_btn_salir)
        
        btn6_txt = self.canvas.create_text(
            640, y_inicial + (separacion * 5), 
            text="6. Salir", 
            fill=self.COLOR_TEXTO, 
            font=("Arial", 10, "bold")
        )
        self.canvas.tag_bind(btn6_txt, "<Button-1>", lambda e: self._salir_guardando())

    def _salir_guardando(self):
        guardar_datos()
        self.root.quit()

    def _habilitar_btn2(self):
        self.canvas.itemconfig(self.btn2_txt, fill=self.COLOR_TEXTO)

    def _estilo_boton(self, **kw):
        base = {"fg": C["fg"], "bg": C["gray"],
                "activebackground": C["cyan"], "activeforeground": "#000000",
                "font": ("Arial", 11, "bold"), "width": 32, "bd": 0,
                "cursor": "hand2", "pady": 8}
        base.update(kw)
        return base

    # ── CONFIGURACIÓN DEL TORNEO ─────────────────

    def abrir_configuracion(self):
        if data_store.config_guardada:
            messagebox.showwarning(
                "Acceso Denegado",
                "La configuraci\u00f3n del torneo ya fue finalizada.\nNo se puede modificar.")
            return
        win = tk.Toplevel(self.root)
        win.title("Configuraci\u00f3n del Torneo")
        centrar_ventana(win, 440, 400)
        win.configure(bg=C["bg"])
        win.transient(self.root)
        win.grab_set()

        card = tk.Frame(win, bg=C["card"], padx=20, pady=20)
        card.pack(pady=15, padx=20, fill="both", expand=True)

        tk.Label(card, text="CONFIGURACI\u00d3N DEL TORNEO", fg=C["cyan"], bg=C["card"],
                 font=("Arial", 12, "bold")).pack(pady=(0, 18))

        e_nombre = tk.Entry(card, bg=C["input_bg"], fg="white",
                            insertbackground="white", relief="flat", font=("Arial", 10))
        tk.Label(card, text="Nombre del torneo", fg=C["fg"], bg=C["card"],
                 font=("Arial", 10)).pack(anchor="w")
        e_nombre.pack(fill="x", pady=(2, 12))

        e_inicio = DateEntry(card, "Fecha inicio (DD/MM/AAAA)")
        e_inicio.pack(fill="x", pady=(0, 10))
        e_fin = DateEntry(card, "Fecha fin (DD/MM/AAAA)")
        e_fin.pack(fill="x", pady=(0, 18))

        def guardar():
            nombre = e_nombre.get().strip()
            inicio = e_inicio.get()
            fin = e_fin.get()
            if not nombre:
                messagebox.showerror("Error", "Debe ingresar un nombre.", parent=win)
                return
            res = configuracion(nombre, inicio, fin)
            if isinstance(res, str) and res.startswith("ERROR"):
                messagebox.showerror("Error", res, parent=win)
                return

            self.datos_config = res
            self.disponibles = set(res["disponibles"])
            self.asignaciones = {g: [] for g in res["grupos"]}
            win.destroy()
            self.abrir_asignacion_grupos()

        btn_frame = tk.Frame(win, bg=C["bg"])
        btn_frame.pack(pady=(0, 12))
        tk.Button(btn_frame, text="Guardar y Asignar Grupos",
                  command=guardar, **self._estilo_boton(width=28)).pack()

    # ── ASIGNACIÓN DE EQUIPOS A GRUPOS ───────────

    def abrir_asignacion_grupos(self):
        win = tk.Toplevel(self.root)
        win.title("Asignaci\u00f3n de Equipos a Grupos")
        centrar_ventana(win, 780, 580)
        win.configure(bg=C["bg"])
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="ASIGNACI\u00d3N DE EQUIPOS A GRUPOS", fg=C["cyan"], bg=C["bg"],
                 font=("Arial", 12, "bold")).pack(pady=(15, 2))
        tk.Label(win, text="Seleccion\u00e1 un pa\u00eds disponible y agregalo a un grupo (4 por grupo)",
                 fg=C["green"], bg=C["bg"], font=("Arial", 9)).pack(pady=(0, 2))
        tk.Label(win, text="Regla: m\u00e1x 2 UEFA por grupo; otras confederaciones no pueden repetirse",
                 fg=C["cyan"], bg=C["bg"], font=("Arial", 8)).pack(pady=(0, 8))

        main = tk.Frame(win, bg=C["bg"])
        main.pack(fill="both", expand=True, padx=15, pady=5)

        left = tk.LabelFrame(main, text="PA\u00cdSES DISPONIBLES",
                             fg=C["cyan"], bg=C["card"], font=("Arial", 10, "bold"),
                             padx=5, pady=5)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        search_frame = tk.Frame(left, bg=C["card"])
        search_frame.pack(fill="x", pady=(0, 4))
        tk.Label(search_frame, text="\U0001f50d", fg=C["disabled"], bg=C["card"],
                 font=("Arial", 10)).pack(side="left", padx=(2, 0))
        self.e_busqueda = tk.Entry(search_frame, bg=C["input_bg"], fg="white",
                                    insertbackground="white", relief="flat",
                                    font=("Arial", 10))
        self.e_busqueda.pack(side="left", fill="x", expand=True, padx=(2, 0))
        self.e_busqueda.bind("<KeyRelease>", self._filtrar_disp)

        self.lbox_disp = tk.Listbox(left, bg=C["input_bg"], fg="white",
                                     selectbackground=C["cyan"],
                                     selectforeground="#000000",
                                     relief="flat", font=("Consolas", 10))
        self.lbox_disp.pack(side="left", fill="both", expand=True)

        sd = tk.Scrollbar(left, command=self.lbox_disp.yview)
        sd.pack(side="right", fill="y")
        self.lbox_disp.config(yscrollcommand=sd.set)
        self._refrescar_disp()

        right = tk.Frame(main, bg=C["bg"])
        right.pack(side="right", fill="both", expand=True)

        sel_row = tk.Frame(right, bg=C["bg"])
        sel_row.pack(fill="x", pady=(0, 8))
        tk.Label(sel_row, text="Grupo:", fg=C["fg"], bg=C["bg"],
                 font=("Arial", 10, "bold")).pack(side="left", padx=(0, 5))
        self.cb_grupo = ttk.Combobox(sel_row, values=list("ABCDEFGHIJKL"),
                                      state="readonly", width=4, font=("Arial", 10))
        self.cb_grupo.pack(side="left")
        self.cb_grupo.bind("<<ComboboxSelected>>", self._refrescar_asig)
        self.cb_grupo.set("A")

        self.lbox_asig = tk.Listbox(right, bg=C["input_bg"], fg="white",
                                     selectbackground=C["green"],
                                     selectforeground="#000000",
                                     relief="flat", font=("Consolas", 10), height=6)
        self.lbox_asig.pack(fill="both", expand=True)

        btn_row = tk.Frame(right, bg=C["bg"])
        btn_row.pack(fill="x", pady=10)
        tk.Button(btn_row, text="\u2192 Agregar", command=self._agregar,
                  **self._estilo_boton(width=13, bg=C["cyan"], fg="#000000")).pack(side="left", padx=3)
        tk.Button(btn_row, text="Quitar \u2190", command=self._quitar,
                  **self._estilo_boton(width=13)).pack(side="right", padx=3)

        self._refrescar_asig()

        tk.Button(right, text="\U0001f3b2 Randomizar", command=self._randomizar,
                  **self._estilo_boton(width=13, bg=C["green"], fg="#000000")).pack(pady=(0, 6))

        self.lbl_status = tk.Label(win, text="", fg=C["green"], bg=C["bg"], font=("Consolas", 9))
        self.lbl_status.pack(pady=(0, 5))
        self._actualizar_status()

        tk.Button(win, text="FINALIZAR CONFIGURACI\u00d3N",
                  command=lambda: self._finalizar(win),
                  bg=C["cyan"], fg="#000000",
                  **{k: v for k, v in self._estilo_boton(width=30).items()
                     if k not in ("bg", "fg")}).pack(pady=8)

    def _refrescar_disp(self, filtro=""):
        self.lbox_disp.delete(0, "end")
        for p in sorted(self.disponibles):
            if filtro.lower() in p.lower():
                conf = confederaciones.get(p, "")
                self.lbox_disp.insert("end", f"{p} [{conf}]" if conf else p)

    def _filtrar_disp(self, event=None):
        self._refrescar_disp(filtro=self.e_busqueda.get())

    def _refrescar_asig(self, event=None):
        self.lbox_asig.delete(0, "end")
        grupo = self.cb_grupo.get()
        for i, p in enumerate(self.asignaciones.get(grupo, []), 1):
            self.lbox_asig.insert("end", f"{i}. {p}")

    def _verificar_confederacion(self, pais, grupo):
        conf_pais = confederaciones.get(pais)
        if not conf_pais:
            return True
        if conf_pais == "UEFA":
            uefa_count = sum(1 for eq in self.asignaciones.get(grupo, [])
                             if confederaciones.get(eq) == "UEFA")
            return uefa_count < 2
        for eq in self.asignaciones.get(grupo, []):
            if confederaciones.get(eq) == conf_pais:
                return False
        return True

    def _agregar(self):
        grupo = self.cb_grupo.get()
        sel = self.lbox_disp.curselection()
        if not sel:
            messagebox.showwarning("Seleccionar pa\u00eds", "Seleccion\u00e1 un pa\u00eds de la lista.")
            return
        if len(self.asignaciones[grupo]) >= 4:
            messagebox.showwarning("Grupo completo",
                                   f"El grupo {grupo} ya tiene 4 equipos.")
            return
        texto = self.lbox_disp.get(sel[0])
        pais = texto.split(" [")[0]
        if not self._verificar_confederacion(pais, grupo):
            conf = confederaciones.get(pais, "")
            if conf == "UEFA":
                messagebox.showwarning(
                    "L\u00edmite UEFA",
                    f"{pais} ({conf}) no puede agregarse: m\u00e1ximo 2 equipos UEFA por grupo.")
            else:
                messagebox.showwarning(
                    "Confederaci\u00f3n repetida",
                    f"{pais} ({conf}) no puede estar en el mismo grupo con otro equipo de {conf}.")
            return
        self.disponibles.discard(pais)
        self.asignaciones[grupo].append(pais)
        self._refrescar_disp(filtro=self.e_busqueda.get())
        self._refrescar_asig()
        self._actualizar_status()

    def _quitar(self):
        grupo = self.cb_grupo.get()
        sel = self.lbox_asig.curselection()
        if not sel:
            return
        texto = self.lbox_asig.get(sel[0])
        pais = texto.split(". ", 1)[1]
        self.asignaciones[grupo].remove(pais)
        self.disponibles.add(pais)
        self._refrescar_disp(filtro=self.e_busqueda.get())
        self._refrescar_asig()
        self._actualizar_status()

    def _actualizar_status(self):
        total = sum(len(v) for v in self.asignaciones.values())
        self.lbl_status.config(text=f"Asignados: {total}/48  |  Pendientes: {len(self.disponibles)}")

    def _randomizar(self):
        if not self.disponibles:
            messagebox.showinfo("Info", "Todos los pa\u00edses ya est\u00e1n asignados.")
            return
        self.asignaciones, self.disponibles = randomizar_grupos(
            self.disponibles, self.asignaciones)
        self._refrescar_disp(filtro=self.e_busqueda.get())
        self._refrescar_asig()
        self._actualizar_status()
        total = sum(len(v) for v in self.asignaciones.values())
        if total == 48:
            messagebox.showinfo("Completado", "Todos los grupos tienen 4 equipos asignados.")

    def _finalizar(self, win):
        for g, eqs in self.asignaciones.items():
            if len(eqs) != 4:
                messagebox.showerror("Error",
                                     f"Grupo {g} tiene {len(eqs)} equipos (deben ser 4).",
                                     parent=win)
                return

        for g, eqs in self.asignaciones.items():
            for i, nom in enumerate(eqs, 1):
                abrev = "".join(c for c in nom.upper() if c.isalpha())[:3]
                pref = data_store.prefijos_telefonicos.get(nom, "")
                conf = confederaciones.get(nom, "")
                data_store.tablagral[nom] = Equipo(
                    nombre=nom, abreviatura=abrev, prefijo=pref,
                    grupo=g, id_identificador=f"{g}{i}",
                    confederacion=conf
                )

        for g, eqs in self.asignaciones.items():
            for e1, e2 in generar_pares_grupo(eqs):
                data_store.tablagral[e1].partidos.append(
                    {"rival": e2, "fecha": "", "hora": "", "goles": None})
                data_store.tablagral[e2].partidos.append(
                    {"rival": e1, "fecha": "", "hora": "", "goles": None})

        guardar_datos()
        win.destroy()
        self.abrir_calendario_config()

    # ── CALENDARIO DE PARTIDOS (PASO 3 DE CONFIGURACIÓN) ─────

    def abrir_calendario_config(self):
        win = tk.Toplevel(self.root)
        win.title("Calendario de Partidos")
        centrar_ventana(win, 800, 580)
        win.configure(bg=C["bg"])
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="CALENDARIO DE PARTIDOS", fg=C["cyan"], bg=C["bg"],
                font=("Arial", 12, "bold")).pack(pady=(14, 2))
        tk.Label(win, text="Asigná fecha y hora a cada partido antes de finalizar la configuración",
                fg=C["green"], bg=C["bg"], font=("Arial", 9)).pack(pady=(0, 8))

        top = tk.Frame(win, bg=C["bg"])
        top.pack(fill="x", padx=20, pady=(0, 5))
        tk.Label(top, text="Grupo:", fg=C["fg"], bg=C["bg"],
                font=("Arial", 10, "bold")).pack(side="left", padx=(0, 8))
        cb = ttk.Combobox(top, values=list("ABCDEFGHIJKL"),
                        state="readonly", width=4, font=("Arial", 10))
        cb.pack(side="left", padx=(0, 16))

        def _fecha_hora_aleatoria_cal():
            from datetime import timedelta
            fi = data_store.fecha_inicio_obj
            ff = data_store.fecha_fin_obj
            if fi and ff and ff > fi:
                delta = (ff - fi).days
                dia = fi + timedelta(days=random.randint(0, delta))
                return dia.strftime("%d/%m/%Y"), random.choice(["10:00","12:00","14:00","16:00","18:00","20:00","21:00"])
            return "", ""

        def randomizar_fechas():
            for (e_fecha, e_hora) in cal_widgets.values():
                f, h = _fecha_hora_aleatoria_cal()
                e_fecha.delete(0, "end")
                e_fecha.insert(0, f)
                e_hora.delete(0, "end")
                e_hora.insert(0, h)

        
        tk.Button(top, text="🎲 Randomizar grupo", command=randomizar_fechas,
                bg=C["green"], fg="#000000", font=("Arial", 9, "bold"),
                bd=0, cursor="hand2", padx=10, pady=4).pack(side="left", padx=(0, 6))

        def randomizar_todo():
            from datetime import timedelta
            fi = data_store.fecha_inicio_obj
            ff = data_store.fecha_fin_obj
            horas = ["10:00","12:00","14:00","16:00","18:00","20:00","21:00"]
            procesados = set()
            for equipo in data_store.tablagral.values():
                for p in equipo.partidos:
                    par = tuple(sorted([equipo.nombre, p["rival"]]))
                    if par not in procesados:
                        procesados.add(par)
                        if fi and ff and ff > fi:
                            delta = (ff - fi).days
                            dia = fi + timedelta(days=random.randint(0, delta))
                            fecha_str = dia.strftime("%d/%m/%Y")
                        else:
                            fecha_str = ""
                        hora_str = random.choice(horas)
                        p["fecha"] = fecha_str
                        p["hora"] = hora_str
                        rival = data_store.tablagral.get(p["rival"])
                        if rival:
                            for pp in rival.partidos:
                                if pp["rival"] == equipo.nombre:
                                    pp["fecha"] = fecha_str
                                    pp["hora"] = hora_str
            guardar_datos()
            mostrar_grupo()
            messagebox.showinfo("✓ Listo",
                                "Fechas y horarios asignados a todos los partidos del torneo.",
                                parent=win)

        tk.Button(top, text="🌍 Randomizar Todo", command=randomizar_todo,
                bg="#0088FF", fg="#FFFFFF", font=("Arial", 9, "bold"),
                bd=0, cursor="hand2", padx=10, pady=4).pack(side="left")

        scroll_canvas = tk.Canvas(win, bg=C["bg"], highlightthickness=0)
        scroll_bar = tk.Scrollbar(win, orient="vertical", command=scroll_canvas.yview)
        scroll_frame = tk.Frame(scroll_canvas, bg=C["bg"])
        scroll_frame.bind("<Configure>",
                        lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all")))
        scroll_canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        scroll_canvas.configure(yscrollcommand=scroll_bar.set)
        scroll_canvas.pack(side="left", fill="both", expand=True, padx=20, pady=5)
        scroll_bar.pack(side="right", fill="y")

        cal_widgets = {}

        def mostrar_grupo(event=None):
            for w in scroll_frame.winfo_children():
                w.destroy()
            cal_widgets.clear()
            k = cb.get()
            if not k:
                return
            mostrados = set()
            equipos = [e for e in data_store.tablagral.values() if e.grupo == k]
            for e in equipos:
                for p in e.partidos:
                    par = tuple(sorted([e.nombre, p["rival"]]))
                    if par in mostrados:
                        continue
                    mostrados.add(par)

                    card = tk.Frame(scroll_frame, bg=C["card"], padx=12, pady=8)
                    card.pack(fill="x", pady=4)

                    row = tk.Frame(card, bg=C["card"])
                    row.pack(fill="x")
                    tk.Label(row, text=e.nombre, fg=C["fg"], bg=C["card"],
                            font=("Arial", 10, "bold"), width=20, anchor="w").pack(side="left")
                    tk.Label(row, text="vs", fg=C["cyan"], bg=C["card"],
                            font=("Arial", 10)).pack(side="left", padx=6)
                    tk.Label(row, text=p["rival"], fg=C["fg"], bg=C["card"],
                            font=("Arial", 10, "bold"), width=20, anchor="w").pack(side="left")

                    row2 = tk.Frame(card, bg=C["card"])
                    row2.pack(fill="x", pady=(4, 0))
                    tk.Label(row2, text="Fecha (DD/MM/AAAA):", fg=C["disabled"],
                            bg=C["card"], font=("Arial", 8)).pack(side="left")
                    e_fecha = tk.Entry(row2, bg=C["input_bg"], fg="white",
                                    insertbackground="white", relief="flat",
                                    font=("Arial", 9), width=13, justify="center")
                    e_fecha.pack(side="left", padx=(4, 14))
                    tk.Label(row2, text="Hora (HH:MM):", fg=C["disabled"],
                            bg=C["card"], font=("Arial", 8)).pack(side="left")
                    e_hora = tk.Entry(row2, bg=C["input_bg"], fg="white",
                                    insertbackground="white", relief="flat",
                                    font=("Arial", 9), width=7, justify="center")
                    e_hora.pack(side="left", padx=(4, 0))

                    if p.get("fecha"):
                        e_fecha.insert(0, p["fecha"])
                    if p.get("hora"):
                        e_hora.insert(0, p["hora"])

                    cal_widgets[par] = (e_fecha, e_hora)

        cb.bind("<<ComboboxSelected>>", mostrar_grupo)
        cb.set("A")
        mostrar_grupo()

        def guardar_calendario():
            for par, (e_fecha, e_hora) in cal_widgets.items():
                fecha_val = e_fecha.get().strip()
                hora_val  = e_hora.get().strip()
                e1n, e2n = par
                for nom in (e1n, e2n):
                    team = data_store.tablagral.get(nom)
                    if not team:
                        continue
                    rival = e2n if nom == e1n else e1n
                    for pp in team.partidos:
                        if pp["rival"] == rival:
                            pp["fecha"] = fecha_val
                            pp["hora"]  = hora_val
            guardar_datos()

        def finalizar_config():
            guardar_calendario()
            data_store.config_guardada = True
            self.torneo_configurado = True
            self._habilitar_btn2()
            guardar_datos()
            messagebox.showinfo(
                "✓ Configuración Completa",
                f"Torneo '{data_store.nombre_torneo}' configurado.\n48 equipos, 12 grupos y calendario guardados.",
                parent=win)
            win.destroy()

        btn_frame = tk.Frame(win, bg=C["bg"])
        btn_frame.pack(fill="x", pady=(4, 12))
        tk.Button(btn_frame, text="💾 Guardar fechas del grupo",
                command=guardar_calendario,
                bg=C["gray"], fg=C["fg"],
                font=("Arial", 10, "bold"), bd=0, cursor="hand2",
                padx=14, pady=6).pack(side="left", padx=(20, 10))
        tk.Button(btn_frame, text="✅ FINALIZAR CONFIGURACIÓN",
                command=finalizar_config,
                bg=C["cyan"], fg="#000000",
                font=("Arial", 10, "bold"), bd=0, cursor="hand2",
                padx=14, pady=6).pack(side="left")

    # ── REGISTRO DE RESULTADOS ────────────────────

    def abrir_resultados(self):
        if not self.torneo_configurado:
            messagebox.showwarning("Acceso Denegado",
                                   "Primero complet\u00e1 la Configuraci\u00f3n del Torneo.")
            return

        win = tk.Toplevel(self.root)
        win.title("Registro de Resultados")
        centrar_ventana(win, 760, 540)
        win.configure(bg=C["bg"])
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="REGISTRO DE RESULTADOS", fg=C["cyan"], bg=C["bg"],
                 font=("Arial", 12, "bold")).pack(pady=(18, 2))
        tk.Label(win, text="Seleccion\u00e1 un grupo y carg\u00e1 los goles de cada partido",
                 fg=C["green"], bg=C["bg"], font=("Arial", 9)).pack(pady=(0, 12))

        top = tk.Frame(win, bg=C["bg"])
        top.pack(fill="x", padx=20, pady=(10, 5))
        tk.Label(top, text="Grupo:", fg=C["fg"], bg=C["bg"],
                 font=("Arial", 10, "bold")).pack(side="left", padx=(0, 10))
        cb = ttk.Combobox(top, values=list("ABCDEFGHIJKL"),
                           state="readonly", width=4, font=("Arial", 10))
        cb.pack(side="left", padx=(0, 20))
        
        def randomizar_grupo():
            k = cb.get()
            if not k:
                messagebox.showwarning("Seleccionar grupo", "Selecciona un grupo.", parent=win)
                return
            
            for par, (loc, vis, loc_n, vis_n) in match_widgets.items():
                goles_loc = random.randint(0, 4)
                goles_vis = random.randint(0, 4)
                loc.delete(0, "end")
                vis.delete(0, "end")
                loc.insert(0, str(goles_loc))
                vis.insert(0, str(goles_vis))
                
            
            # Generar tarjetas aleatorias para ambos equipos
            equipos = [e for e in data_store.tablagral.values() if e.grupo == k]
            for e in equipos:
                # Limpiar tarjetas previas
                e.am = 0
                e.rj = 0
                e.plantel = {}
                
                # Generar jugadores si existen en la base de datos
                jugadores = jugadores_por_equipo.get(e.nombre, [])
                if jugadores:
                    # Asignar tarjetas a jugadores aleatorios
                    num_jugadores_tarjetas = random.randint(1, min(5, len(jugadores)))
                    for _ in range(num_jugadores_tarjetas):
                        jug = random.choice(jugadores)
                        if jug not in e.plantel:
                            e.plantel[jug] = {"AM": 0, "RJ": 0}
                        
                        # 80% probabilidad de amarilla, 20% de roja
                        if random.random() < 0.8:
                            e.plantel[jug]["AM"] += 1
                            e.am += 1
                        else:
                            e.plantel[jug]["RJ"] += 1
                            e.rj += 1
        
        def _fecha_hora_aleatoria():
            from datetime import timedelta
            fi = data_store.fecha_inicio_obj
            ff = data_store.fecha_fin_obj
            if fi and ff and ff > fi:
                delta = (ff - fi).days
                dia_aleatorio = fi + timedelta(days=random.randint(0, delta))
                fecha_str = dia_aleatorio.strftime("%d/%m/%Y")
            else:
                fecha_str = ""
            horas = ["10:00", "12:00", "14:00", "16:00", "18:00", "20:00", "21:00"]
            hora_str = random.choice(horas)
            return fecha_str, hora_str

        def simular_todos():
            procesados = set()
            for equipo in data_store.tablagral.values():
                for p in equipo.partidos:
                    par = tuple(sorted([equipo.nombre, p["rival"]]))
                    if par not in procesados:
                        procesados.add(par)
                        fecha_str, hora_str = _fecha_hora_aleatoria()
                        rival = data_store.tablagral.get(p["rival"])
                        if rival:
                            for pp in rival.partidos:
                                if pp["rival"] == equipo.nombre:
                                    if not pp.get("fecha"):
                                        pp["fecha"] = fecha_str
                                        pp["hora"] = hora_str
                    if p["goles"] is None:
                        p["goles"] = [random.randint(0, 4), random.randint(0, 4)]
                    if not p.get("fecha"):
                        fecha_str, hora_str = _fecha_hora_aleatoria()
                        p["fecha"] = fecha_str
                        p["hora"] = hora_str

            for e in data_store.tablagral.values():
                e.am = 0
                e.rj = 0
                e.plantel = {}
                jugadores = jugadores_por_equipo.get(e.nombre, [])
                if jugadores:
                    num_jugadores_tarjetas = random.randint(1, min(5, len(jugadores)))
                    for _ in range(num_jugadores_tarjetas):
                        jug = random.choice(jugadores)
                        if jug not in e.plantel:
                            e.plantel[jug] = {"AM": 0, "RJ": 0}
                        if random.random() < 0.8:
                            e.plantel[jug]["AM"] += 1
                            e.am += 1
                        else:
                            e.plantel[jug]["RJ"] += 1
                            e.rj += 1

            guardar_datos()
            messagebox.showinfo("✓ Simulación Completada",
                                "Se han generado resultados, fechas y horarios aleatorios para todos los partidos.",
                                parent=win)
        
        tk.Button(top, text="🎲 Randomizar", command=randomizar_grupo,
                  bg=C["green"], fg="#000000", font=("Arial", 9, "bold"),
                  bd=0, cursor="hand2", padx=10, pady=4).pack(side="left", padx=(0, 5))
        
        tk.Button(top, text="🌍 Simular Todo", command=simular_todos,
                  bg="#0088FF", fg="#FFFFFF", font=("Arial", 9, "bold"),
                  bd=0, cursor="hand2", padx=10, pady=4).pack(side="left")

        scroll_canvas = tk.Canvas(win, bg=C["bg"], highlightthickness=0)
        scroll_bar = tk.Scrollbar(win, orient="vertical", command=scroll_canvas.yview)
        scroll_frame = tk.Frame(scroll_canvas, bg=C["bg"])
        scroll_frame.bind("<Configure>",
                          lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all")))
        scroll_canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        scroll_canvas.configure(yscrollcommand=scroll_bar.set)

        scroll_canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scroll_bar.pack(side="right", fill="y")

        match_widgets = {}
        editando = {}

        def mostrar_partidos(event=None):
            for w in scroll_frame.winfo_children():
                w.destroy()
            match_widgets.clear()
            editando.clear()

            k = cb.get()
            if not k:
                return
            mostrados = set()
            equipos = [e for e in data_store.tablagral.values() if e.grupo == k]
            for e in equipos:
                for p in e.partidos:
                    par = tuple(sorted([e.nombre, p["rival"]]))
                    if par in mostrados:
                        continue
                    mostrados.add(par)
                    editando[par] = False

                    card = tk.Frame(scroll_frame, bg=C["card"], padx=12, pady=8)
                    card.pack(fill="x", pady=4)

                    row = tk.Frame(card, bg=C["card"])
                    row.pack(fill="x")

                    tk.Label(row, text=e.nombre, fg=C["fg"], bg=C["card"],
                             font=("Arial", 10, "bold"), width=18, anchor="w").pack(side="left")
                    tk.Label(row, text="vs", fg=C["cyan"], bg=C["card"],
                             font=("Arial", 10)).pack(side="left", padx=5)
                    tk.Label(row, text=p["rival"], fg=C["fg"], bg=C["card"],
                             font=("Arial", 10, "bold"), width=18, anchor="w").pack(side="left")

                    tk.Label(row, text="Goles:", fg=C["green"], bg=C["card"],
                             font=("Arial", 9)).pack(side="left", padx=(12, 4))

                    e_loc = tk.Entry(row, bg=C["input_bg"], fg="white",
                                     insertbackground="white", relief="flat",
                                     font=("Arial", 10), width=4, justify="center")
                    e_loc.pack(side="left", padx=1)

                    tk.Label(row, text="-", fg=C["fg"], bg=C["card"],
                             font=("Arial", 10, "bold")).pack(side="left")

                    e_vis = tk.Entry(row, bg=C["input_bg"], fg="white",
                                     insertbackground="white", relief="flat",
                                     font=("Arial", 10), width=4, justify="center")
                    e_vis.pack(side="left", padx=1)

                    if p["goles"] is not None:
                        e_loc.insert(0, str(p["goles"][0]))
                        e_vis.insert(0, str(p["goles"][1]))


                    # Mostrar fecha (solo lectura, se edita en configuración)
                    if p.get("fecha"):
                        row2 = tk.Frame(card, bg=C["card"])
                        row2.pack(fill="x", pady=(2, 0))
                        tk.Label(row2, text=f"📅 {p['fecha']}  🕐 {p.get('hora', '')}",
                                 fg=C["disabled"], bg=C["card"], font=("Arial", 8)).pack(side="left")
                    match_widgets[par] = (e_loc, e_vis, e.nombre, p["rival"])
                    tk.Button(row, text="Tarjetas", font=("Arial", 8),
                              command=lambda t1=e.nombre, t2=p["rival"]:
                                  self._asignar_tarjetas_gui(t1, t2),
                              bg=C["disabled"], fg=C["fg"], bd=0,
                              cursor="hand2", width=8).pack(side="left", padx=(8, 0))

            if not mostrados:
                tk.Label(scroll_frame, text="No hay partidos en este grupo.",
                         fg=C["disabled"], bg=C["bg"], font=("Arial", 10)).pack(pady=20)

        cb.bind("<<ComboboxSelected>>", mostrar_partidos)
        cb.set("A")
        mostrar_partidos()

        def guardar_res():
            k = cb.get()
            if not k:
                messagebox.showwarning("Seleccionar grupo", "Seleccioná un grupo.", parent=win)
                return
            ok = True
            for (e1n, e2n), (loc, vis, loc_n, vis_n) in match_widgets.items():
                g1 = loc.get().strip()
                g2 = vis.get().strip()
                if not g1 or not g2:
                    continue
                try:
                    g1n, g2n = int(g1), int(g2)
                except ValueError:
                    messagebox.showerror("Error",
                                        f"Goles inválidos en {loc_n} vs {vis_n}. Usá números.",
                                        parent=win)
                    ok = False
                    break
                for nom in (loc_n, vis_n):
                    team = data_store.tablagral[nom]
                    rival = vis_n if nom == loc_n else loc_n
                    for pp in team.partidos:
                        if pp["rival"] == rival:
                            pp["goles"] = [g1n, g2n] if nom == loc_n else [g2n, g1n]
            if ok:
                guardar_datos()
                messagebox.showinfo("Guardado", "Resultados guardados correctamente.", parent=win)
                win.destroy()

        btn_frame = tk.Frame(win, bg=C["bg"])
        btn_frame.pack(fill="x", pady=(5, 12))
        
        tk.Button(btn_frame, text="Guardar Resultados",
                  command=guardar_res,
                  bg=C["cyan"], fg="#000000",
                  **{k: v for k, v in self._estilo_boton(width=20).items()
                     if k not in ("bg", "fg")}).pack()

    # ── VENTANA DE TARJETAS ──────────────────────

    def _asignar_tarjetas_gui(self, local, visit):
        win = tk.Toplevel(self.root)
        win.title("Tarjetas")
        centrar_ventana(win, 480, 400)
        win.configure(bg=C["bg"])
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="ASIGNAR TARJETAS", fg=C["cyan"], bg=C["bg"],
                 font=("Arial", 11, "bold")).pack(pady=(12, 8))

        main = tk.Frame(win, bg=C["bg"], padx=15, pady=5)
        main.pack(fill="both", expand=True)

        lbl_feedback = tk.Label(main, text="", fg=C["green"], bg=C["bg"], font=("Arial", 9))
        lbl_feedback.pack(pady=5)

        def seccion(team_name):
            frame = tk.LabelFrame(main, text=team_name, fg=C["green"],
                                  bg=C["card"], font=("Arial", 10, "bold"),
                                  padx=10, pady=8)
            frame.pack(fill="x", pady=5)

            row = tk.Frame(frame, bg=C["card"])
            row.pack(fill="x")

            tk.Label(row, text="Jugador:", fg=C["fg"], bg=C["card"],
                     font=("Arial", 9)).pack(side="left")
            jugadores = jugadores_por_equipo.get(team_name, [])
            cb_jug = ttk.Combobox(row, values=jugadores,
                                   state="normal", width=22, font=("Arial", 9))
            cb_jug.pack(side="left", padx=5)

            tk.Label(row, text="Tipo:", fg=C["fg"], bg=C["card"],
                     font=("Arial", 9)).pack(side="left")
            cb_tipo = ttk.Combobox(row, values=["Amarilla", "Roja"],
                                    state="readonly", width=9, font=("Arial", 9))
            cb_tipo.pack(side="left", padx=5)
            cb_tipo.set("Amarilla")

            def agregar():
                jug = cb_jug.get().strip()
                if not jug:
                    messagebox.showwarning("Nombre", "Seleccion\u00e1 o escrib\u00ed el nombre del jugador.", parent=win)
                    return
                tipo = "AM" if cb_tipo.get() == "Amarilla" else "RJ"
                obj = data_store.tablagral[team_name]
                if jug not in obj.plantel:
                    obj.plantel[jug] = {"AM": 0, "RJ": 0}
                obj.plantel[jug][tipo] += 1
                if tipo == "AM":
                    obj.am += 1
                else:
                    obj.rj += 1
                cb_jug.set("")
                lbl_feedback.config(text=f"{jug} ({cb_tipo.get()}) \u2192 {team_name}")

            tk.Button(row, text="+", command=agregar,
                      bg=C["cyan"], fg="#000000", bd=0,
                      font=("Arial", 9, "bold"), cursor="hand2", width=3).pack(side="left", padx=5)

        seccion(local)
        seccion(visit)

        tk.Button(win, text="Cerrar", command=win.destroy,
                  **self._estilo_boton(width=20)).pack(pady=(10, 12))

    # ── EMISIÓN DE INFORMES (5 TABS) ─────────────

    def abrir_informes(self):
        win = tk.Toplevel(self.root)
        win.title("Emisi\u00f3n de Informes")
        centrar_ventana(win, 850, 620)
        win.configure(bg=C["bg"])
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="EMISI\u00d3N DE INFORMES", fg=C["cyan"], bg=C["bg"],
                 font=("Arial", 12, "bold")).pack(pady=(10, 2))

        # Estilo oscuro para el Notebook
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=C["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", background=C["gray"], foreground="white",
                        padding=[12, 4], font=("Arial", 9, "bold"))
        style.map("TNotebook.Tab", background=[("selected", C["cyan"])],
                  foreground=[("selected", "#000000")])
        style.configure("Treeview", background=C["input_bg"], foreground="white",
                        fieldbackground=C["input_bg"], rowheight=26)
        style.configure("Treeview.Heading", background=C["gray"], foreground="white", relief="flat")
        style.map("Treeview", background=[("selected", C["cyan"])],
                  foreground=[("selected", "#000000")])

        notebook = ttk.Notebook(win)
        notebook.pack(fill="both", expand=True, padx=15, pady=(5, 15))

        # ── TAB 1: Partidos en una fecha ──────────
        tab1 = tk.Frame(notebook, bg=C["bg"])
        notebook.add(tab1, text=" Partidos en fecha ")

        tk.Label(tab1, text="Consultar partidos en una fecha espec\u00edfica",
                 fg=C["green"], bg=C["bg"], font=("Arial", 9)).pack(pady=(10, 5))

        fecha_row = tk.Frame(tab1, bg=C["bg"])
        fecha_row.pack(pady=5)
        tk.Label(fecha_row, text="Fecha (DD/MM/AAAA):", fg=C["fg"], bg=C["bg"],
                 font=("Arial", 10)).pack(side="left", padx=(0, 5))
        e_fecha = tk.Entry(fecha_row, bg=C["input_bg"], fg="white",
                          insertbackground="white", relief="flat", font=("Arial", 10), width=14)
        e_fecha.pack(side="left", padx=5)

        tree1_frame = tk.Frame(tab1, bg=C["bg"])
        tree1_frame.pack(fill="both", expand=True, padx=20, pady=10)

        cols1 = ("Local", "Visitante", "Grupo", "Hora", "Resultado")
        tree1 = ttk.Treeview(tree1_frame, columns=cols1, show="headings", height=10)
        for c in cols1:
            tree1.heading(c, text=c)
            tree1.column(c, width=120, anchor="center")
        tree1.column("Local", width=180, anchor="w")
        tree1.column("Visitante", width=180, anchor="w")

        sv1 = tk.Scrollbar(tree1_frame, orient="vertical", command=tree1.yview)
        tree1.configure(yscrollcommand=sv1.set)
        tree1.pack(side="left", fill="both", expand=True)
        sv1.pack(side="right", fill="y")

        def buscar_partidos():
            for i in tree1.get_children():
                tree1.delete(i)
            fecha = e_fecha.get().strip()
            if not fecha:
                messagebox.showwarning("Fecha", "Ingres\u00e1 una fecha (DD/MM/AAAA).", parent=win)
                return
            resultados = partidos_en_fecha(fecha)
            if not resultados:
                for w in tab1.winfo_children():
                    if isinstance(w, tk.Label):
                        w.destroy()
                tk.Label(tab1, text="No se encontraron partidos en esa fecha.",
                         fg=C["disabled"], bg=C["bg"]).pack()
                return
            for r in resultados:
                tree1.insert("", "end", values=(r["local"], r["visitante"],
                                                r["grupo"], r["hora"], r["resultado"]))

        tk.Button(tab1, text="Buscar", command=buscar_partidos,
                  **self._estilo_boton(width=15, bg=C["cyan"], fg="#000000")).pack(pady=(0, 5))

        # ── TAB 2: Tabla de un grupo ──────────────
        tab2 = tk.Frame(notebook, bg=C["bg"])
        notebook.add(tab2, text=" Tabla de grupo ")

        top2 = tk.Frame(tab2, bg=C["bg"])
        top2.pack(fill="x", padx=20, pady=(10, 5))
        tk.Label(top2, text="Grupo:", fg=C["fg"], bg=C["bg"],
                 font=("Arial", 10, "bold")).pack(side="left", padx=(0, 10))
        cb2 = ttk.Combobox(top2, values=list("ABCDEFGHIJKL"),
                            state="readonly", width=4, font=("Arial", 10))
        cb2.pack(side="left")

        tree2_frame = tk.Frame(tab2, bg=C["bg"])
        tree2_frame.pack(fill="both", expand=True, padx=20, pady=10)

        cols2 = ("ID", "Equipo", "PJ", "PTS", "DG", "GF", "GC", "AM", "RJ")
        tree2 = ttk.Treeview(tree2_frame, columns=cols2, show="headings", height=10)
        for c in cols2:
            tree2.heading(c, text=c)
            tree2.column(c, width=70, anchor="center")
        tree2.column("Equipo", width=180, anchor="w")
        tree2.column("ID", width=40)

        sv2 = tk.Scrollbar(tree2_frame, orient="vertical", command=tree2.yview)
        tree2.configure(yscrollcommand=sv2.set)
        tree2.pack(side="left", fill="both", expand=True)
        sv2.pack(side="right", fill="y")

        def actualizar_tabla(event=None):
            for i in tree2.get_children():
                tree2.delete(i)
            k = cb2.get()
            if not k:
                return
            for e in calcular_tabla_grupo(k):
                tree2.insert("", "end", values=(
                    e.id or "", e.nombre, e.pj, e.puntos, e.gf - e.gc,
                    e.gf, e.gc, e.am, e.rj))

        cb2.bind("<<ComboboxSelected>>", actualizar_tabla)
        cb2.set("A")
        actualizar_tabla()

        # ── TAB 3: Resultados de un equipo ────────
        tab3 = tk.Frame(notebook, bg=C["bg"])
        notebook.add(tab3, text=" Resultados de equipo ")

        tk.Label(tab3, text="Ver informaci\u00f3n detallada de un equipo",
                 fg=C["green"], bg=C["bg"], font=("Arial", 9)).pack(pady=(10, 5))

        top3 = tk.Frame(tab3, bg=C["bg"])
        top3.pack(fill="x", padx=20)
        tk.Label(top3, text="Equipo:", fg=C["fg"], bg=C["bg"],
                 font=("Arial", 10, "bold")).pack(side="left", padx=(0, 5))
        cb3 = ttk.Combobox(top3, values=sorted(data_store.tablagral.keys()),
                           state="readonly", width=25, font=("Arial", 10))
        cb3.pack(side="left")

        text3 = tk.Text(tab3, bg=C["input_bg"], fg="white", font=("Consolas", 9),
                        relief="flat", wrap="none", padx=10, pady=10)
        text3.pack(fill="both", expand=True, padx=20, pady=10)

        sv3 = tk.Scrollbar(text3, orient="vertical", command=text3.yview)
        text3.configure(yscrollcommand=sv3.set)
        sv3.pack(side="right", fill="y")

        def mostrar_resultados():
            text3.delete("1.0", "end")
            team = cb3.get()
            if not team:
                messagebox.showwarning("Equipo", "Seleccion\u00e1 un equipo.", parent=win)
                return
            res = resultados_equipo(team)
            if not res:
                text3.insert("end", "Equipo no encontrado.")
                return
            lineas = []
            lineas.append("=" * 50)
            lineas.append(f"EQUIPO: {res['nombre']} ({res['abreviatura']})")
            lineas.append(f"Grupo: {res['grupo']}  |  ID: {res['id']}")
            lineas.append("=" * 50)
            lineas.append(f"\nEstad\u00edsticas:")
            lineas.append(f"  PJ: {res['pj']}  PTS: {res['puntos']}  DG: {res['dg']:+d}")
            lineas.append(f"  GF: {res['gf']}  GC: {res['gc']}  AM: {res['am']}  RJ: {res['rj']}")
            lineas.append(f"\nPartidos:")
            for p in res['partidos']:
                lineas.append(f"  vs {p['rival']:<18}  {p['resultado']:>9}")
            if res['plantel']:
                lineas.append(f"\nPlantel / Tarjetas:")
                for j in res['plantel']:
                    lineas.append(f"  {j['nombre']:<20}  AM={j['am']}  RJ={j['rj']}")
            text3.insert("1.0", "\n".join(lineas))

            # Botón para guardar .txt
            def guardar():
                contenido = generar_informe_equipo(team)
                archivo = guardar_informe_txt(contenido)
                messagebox.showinfo("Informe generado",
                                    f"Guardado en:\n{archivo}", parent=win)

            btn_frame3 = tk.Frame(tab3, bg=C["bg"])
            btn_frame3.pack(fill="x", padx=20, pady=(0, 5))
            tk.Button(btn_frame3, text="\U0001f4c4 Generar Informe .txt", command=guardar,
                      **self._estilo_boton(width=22, bg=C["cyan"], fg="#000000")).pack()

        cb3.bind("<<ComboboxSelected>>", lambda e: mostrar_resultados())
        if cb3.get():
            mostrar_resultados()

        # ── TAB 4: Próximo partido ────────────────
        tab4 = tk.Frame(notebook, bg=C["bg"])
        notebook.add(tab4, text=" Próximo partido ")

        tk.Label(tab4, text="Ver el próximo partido pendiente de un equipo para una fecha dada",
                fg=C["green"], bg=C["bg"], font=("Arial", 9)).pack(pady=(10, 5))

        top4 = tk.Frame(tab4, bg=C["bg"])
        top4.pack(fill="x", padx=20)
        tk.Label(top4, text="Equipo:", fg=C["fg"], bg=C["bg"],
                font=("Arial", 10, "bold")).pack(side="left", padx=(0, 5))
        cb4 = ttk.Combobox(top4, values=sorted(data_store.tablagral.keys()),
                        state="readonly", width=25, font=("Arial", 10))
        cb4.pack(side="left", padx=(0, 15))

        tk.Label(top4, text="Fecha (DD/MM/AAAA):", fg=C["fg"], bg=C["bg"],
                font=("Arial", 10, "bold")).pack(side="left", padx=(0, 5))
        e_fecha4 = tk.Entry(top4, bg=C["input_bg"], fg="white",
                            insertbackground="white", relief="flat",
                            font=("Arial", 10), width=13, justify="center")
        e_fecha4.pack(side="left")

        frame4 = tk.Frame(tab4, bg=C["card"], padx=20, pady=20)
        frame4.pack(fill="both", expand=True, padx=20, pady=20)

        lbl4_info = tk.Label(frame4, text="Seleccioná un equipo y una fecha.",
                            fg=C["disabled"], bg=C["card"], font=("Arial", 12), justify="center")
        lbl4_info.pack(expand=True)

        def mostrar_proximo():
            team = cb4.get()
            fecha_input = e_fecha4.get().strip()
            if not team:
                return

            try:
                fecha_desde = datetime.strptime(fecha_input, "%d/%m/%Y") if fecha_input else None
            except ValueError:
                lbl4_info.config(text="Fecha inválida. Usá el formato DD/MM/AAAA.", fg="#FF4444")
                return

            equipo = data_store.tablagral.get(team)
            if not equipo:
                return

            candidatos = []
            for p in equipo.partidos:
                if p.get("goles") is not None:
                    continue
                if p.get("fecha"):
                    try:
                        fecha_partido = datetime.strptime(p["fecha"], "%d/%m/%Y")
                        if fecha_desde and fecha_partido < fecha_desde:
                            continue
                        candidatos.append((fecha_partido, p))
                    except ValueError:
                        candidatos.append((datetime.max, p))
                else:
                    candidatos.append((datetime.max, p))

            if candidatos:
                candidatos.sort(key=lambda x: x[0])
                proximo = candidatos[0][1]
                fecha_txt = proximo.get("fecha") or "Sin asignar"
                hora_txt  = proximo.get("hora")  or "Sin asignar"
                texto = (f"Próximo partido de {team}:\n\n"
                        f"  vs {proximo['rival']}\n"
                        f"  Grupo: {equipo.grupo}\n"
                        f"  Fecha: {fecha_txt}\n"
                        f"  Hora:  {hora_txt}")
                lbl4_info.config(text=texto, fg=C["green"])
            else:
                # Fase de grupos completada: buscar en eliminatorias
                r32 = data_store.partidos_ronda
                if not r32:
                    lbl4_info.config(
                        text=f"{team} completó la fase de grupos.\nEsperando la generación de la Ronda 32.",
                        fg=C["cyan"])
                else:
                    rival = None
                    for p in r32:
                        if p.get("goles") is not None:
                            continue
                        if p["local"] == team:
                            rival = p["visitante"]
                        elif p["visitante"] == team:
                            rival = p["local"]
                    if rival:
                        lbl4_info.config(
                            text=("Próximo partido de {}\n\n"
                                  "  vs {}\n"
                                  "  Fase: Dieciseisavos de Final").format(team, rival),
                            fg=C["green"])
                    else:
                        lbl4_info.config(
                            text=f"{team} no clasificó a la fase eliminatoria.",
                            fg="#FF4444")

        tk.Button(tab4, text="Buscar", command=mostrar_proximo,
                bg=C["cyan"], fg="#000000", font=("Arial", 10, "bold"),
                bd=0, cursor="hand2", padx=14, pady=5).pack(pady=(0, 5))

        cb4.bind("<<ComboboxSelected>>", lambda e: mostrar_proximo())

        # ── TAB 5: Todas las tablas ───────────────
        tab5 = tk.Frame(notebook, bg=C["bg"])
        notebook.add(tab5, text=" Todas las tablas ")

        tk.Label(tab5, text="Tablas de posiciones de todos los grupos",
                 fg=C["green"], bg=C["bg"], font=("Arial", 9)).pack(pady=(10, 5))

        canvas5 = tk.Canvas(tab5, bg=C["bg"], highlightthickness=0)
        sv5 = tk.Scrollbar(tab5, orient="vertical", command=canvas5.yview)
        scroll5 = tk.Frame(canvas5, bg=C["bg"])
        scroll5.bind("<Configure>", lambda e: canvas5.configure(scrollregion=canvas5.bbox("all")))
        canvas5.create_window((0, 0), window=scroll5, anchor="nw")
        canvas5.configure(yscrollcommand=sv5.set)
        canvas5.pack(side="left", fill="both", expand=True, padx=10)
        sv5.pack(side="right", fill="y")

        def construir_todas_tablas():
            for w in scroll5.winfo_children():
                w.destroy()
            tabs = todas_tablas()
            for g in "ABCDEFGHIJKL":
                gf = tk.Frame(scroll5, bg=C["card"], padx=10, pady=5)
                gf.pack(fill="x", pady=3, padx=5)

                inner = tk.Frame(gf, bg=C["card"])
                inner.pack(anchor="w")

                tk.Label(inner, text=f"GRUPO {g}", fg=C["cyan"], bg=C["card"],
                         font=("Arial", 10, "bold")).pack(anchor="w", pady=(2, 2))

                enc = f"{'ID':<4} {'EQUIPO':<18} {'PJ':<3} {'PTS':<4} {'DG':<4} {'GF':<3}"
                tk.Label(inner, text=enc, fg=C["green"], bg=C["card"],
                         font=("Consolas", 9, "bold")).pack(anchor="w")

                for e in tabs[g]:
                    dg_str = f"{e['dg']:+d}"
                    linea = f"{e['id']:<4} {e['nombre']:<18} {e['pj']:<3} {e['puntos']:<4} {dg_str:<4} {e['gf']:<3}"
                    tk.Label(inner, text=linea, fg=C["fg"], bg=C["card"],
                             font=("Consolas", 9)).pack(anchor="w")

        construir_todas_tablas()

        # Botón para generar reporte completo .txt
        botom_frame = tk.Frame(win, bg=C["bg"])
        botom_frame.pack(fill="x", padx=15, pady=(0, 10))

        def generar_completo():
            contenido = generar_reporte_completo()
            archivo = guardar_informe_txt(contenido, "informe_completo.txt")
            messagebox.showinfo("Informe completo",
                                f"Informe completo guardado en:\n{archivo}", parent=win)

        tk.Button(botom_frame, text="\U0001f4c4 Generar Informe Completo .txt",
                  command=generar_completo,
                  bg=C["green"], fg="#000000",
                  **{k: v for k, v in self._estilo_boton(width=28).items()
                     if k not in ("bg", "fg")}).pack()

        # ── TAB 6: Clasificación de Terceros ─────
        tab6 = tk.Frame(notebook, bg=C["bg"])
        notebook.add(tab6, text=" Terceros ")

        tk.Label(tab6, text="CLASIFICACIÓN DE TERCEROS", fg=C["cyan"], bg=C["bg"],
                 font=("Arial", 11, "bold")).pack(pady=(10, 2))
        tk.Label(tab6, text="Los 8 mejores terceros lugares avanzan a la fase eliminatoria",
                 fg=C["green"], bg=C["bg"], font=("Arial", 9)).pack(pady=(0, 10))

        frame6 = tk.Frame(tab6, bg=C["bg"])
        frame6.pack(fill="both", expand=True, padx=20, pady=10)

        cols6 = ("#", "Equipo", "Grupo", "PTS", "DG", "GF", "Prefijo")
        tree6 = ttk.Treeview(frame6, columns=cols6, show="headings", height=12)
        for c in cols6:
            tree6.heading(c, text=c)
            tree6.column(c, width=80, anchor="center")
        tree6.column("Equipo", width=200, anchor="w")
        tree6.column("Prefijo", width=80, anchor="center")

        sv6 = tk.Scrollbar(frame6, orient="vertical", command=tree6.yview)
        tree6.configure(yscrollcommand=sv6.set)
        tree6.pack(side="left", fill="both", expand=True)
        sv6.pack(side="right", fill="y")

        def actualizar_terceros():
            for i in tree6.get_children():
                tree6.delete(i)
            terceros = calcular_terceros()
            for w in tab6.winfo_children():
                if isinstance(w, tk.Label):
                    w.destroy()
            if not terceros:
                tk.Label(tab6, text="No hay datos suficientes. Carga resultados de grupos primero.",
                         fg=C["disabled"], bg=C["bg"], font=("Arial", 10)).pack(pady=10)
            else:
                for i, t in enumerate(terceros, 1):
                    tree6.insert("", "end", values=(i, t["nombre"], t["grupo"],
                                                   t["puntos"], t["dg"], t["gf"],
                                                   data_store.prefijos_telefonicos.get(t["nombre"], "")))

        actualizar_terceros()

        # Botón para refrescar
        btn6_frame = tk.Frame(tab6, bg=C["bg"])
        btn6_frame.pack(fill="x", padx=20, pady=5)
        tk.Button(btn6_frame, text="🔄 Actualizar", command=actualizar_terceros,
                  bg=C["cyan"], fg="#000000", font=("Arial", 9, "bold"),
                  bd=0, cursor="hand2", padx=10, pady=4).pack()

        # Info de criterios
        tk.Label(tab6, 
                text="Criterios: Puntos → Diferencia de Gol → GF → Prefijo telefónico",
                fg=C["disabled"], bg=C["bg"], font=("Arial", 8)).pack(pady=5)

    # ── FASE ELIMINATORIA ─────────────────────────

    def abrir_eliminatorias(self):
        if not self.torneo_configurado:
            messagebox.showwarning("Acceso Denegado",
                                   "Primero complet\u00e1 la Configuraci\u00f3n del Torneo.")
            return

        win = tk.Toplevel(self.root)
        win.title("Fase Eliminatoria")
        centrar_ventana(win, 850, 640)
        win.configure(bg=C["bg"])
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="FASE ELIMINATORIA", fg=C["cyan"], bg=C["bg"],
                 font=("Arial", 12, "bold")).pack(pady=(12, 2))

        lbl_ronda = tk.Label(win, text="", fg=C["green"], bg=C["bg"],
                             font=("Arial", 11, "bold"))
        lbl_ronda.pack(pady=(0, 5))

        frame = tk.Frame(win, bg=C["bg"])
        frame.pack(fill="both", expand=True, padx=15, pady=5)

        # Área scrolleable para los partidos
        canvas = tk.Canvas(frame, bg=C["bg"], highlightthickness=0)
        scroll_bar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scroll_inner = tk.Frame(canvas, bg=C["bg"])
        scroll_inner.bind("<Configure>",
                          lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_inner, anchor="nw")
        canvas.configure(yscrollcommand=scroll_bar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scroll_bar.pack(side="right", fill="y")

        match_widgets = {}

        def construir_partidos():
            for w in scroll_inner.winfo_children():
                w.destroy()
            match_widgets.clear()

            estado = obtener_estado_eliminatorias()
            if not estado["partidos"]:
                tk.Label(scroll_inner, text="No hay partidos generados.\nGener\u00e1 la Ronda 32 para comenzar.",
                         fg=C["disabled"], bg=C["bg"], font=("Arial", 12)).pack(pady=40)
                lbl_ronda.config(text="Sin ronda activa")
                return

            lbl_ronda.config(text=f"Ronda actual: {estado['nombre_ronda']}")

            for idx, p in enumerate(estado["partidos"]):
                card = tk.Frame(scroll_inner, bg=C["card"], padx=15, pady=8)
                card.pack(fill="x", pady=4, padx=5)

                row = tk.Frame(card, bg=C["card"])
                row.pack(fill="x")

                tk.Label(row, text=p["local"], fg=C["fg"], bg=C["card"],
                         font=("Arial", 10, "bold"), width=20, anchor="w").pack(side="left")
                tk.Label(row, text="vs", fg=C["cyan"], bg=C["card"],
                         font=("Arial", 10)).pack(side="left", padx=5)
                tk.Label(row, text=p["visitante"], fg=C["fg"], bg=C["card"],
                         font=("Arial", 10, "bold"), width=20, anchor="w").pack(side="left")

                if p["goles"] is not None:
                    g1, g2 = p["goles"]
                    penales = p.get("penales")
                    if penales:
                        resultado_txt = f"{g1} - {g2}  (pen {penales[0]}-{penales[1]})"
                    else:
                        resultado_txt = f"{g1} - {g2}"
                    tk.Label(row, text=resultado_txt, fg=C["green"], bg=C["card"],
                             font=("Arial", 11, "bold")).pack(side="left", padx=(15, 0))
                    ganador = p.get("ganador", "")
                    tk.Label(row, text=f"→ {ganador}", fg=C["cyan"], bg=C["card"],
                             font=("Arial", 10)).pack(side="left", padx=(8, 0))
                else:
                    tk.Label(row, text="Goles:", fg=C["green"], bg=C["card"],
                             font=("Arial", 9)).pack(side="left", padx=(12, 4))
                    e1 = tk.Entry(row, bg=C["input_bg"], fg="white",
                                  insertbackground="white", relief="flat",
                                  font=("Arial", 10), width=4, justify="center")
                    e1.pack(side="left", padx=1)
                    tk.Label(row, text="-", fg=C["fg"], bg=C["card"],
                             font=("Arial", 10, "bold")).pack(side="left")
                    e2 = tk.Entry(row, bg=C["input_bg"], fg="white",
                                  insertbackground="white", relief="flat",
                                  font=("Arial", 10), width=4, justify="center")
                    e2.pack(side="left", padx=1)
                    match_widgets[idx] = (e1, e2)
        construir_partidos()

        # ── Botones de control ──
        btn_frame = tk.Frame(win, bg=C["bg"])
        btn_frame.pack(fill="x", padx=15, pady=(5, 10))

        def generar_r32():
            if data_store.ronda_actual is not None:
                resp = messagebox.askyesno(
                    "Confirmar",
                    "Ya hay una eliminatoria en curso.\n\u00bfGenerar de nuevo desde Ronda 32?",
                    parent=win)
                if not resp:
                    return
                reiniciar_eliminatorias()
            if generar_ronda32() is None:
                messagebox.showerror("Error",
                    "No se puede generar la Ronda 32.\nAsegurate de tener todos los grupos completos con resultados.",
                    parent=win)
                construir_partidos()
                return
            construir_partidos()
            messagebox.showinfo("Ronda 32",
                                "Dieciseisavos de final generados.\nIngres\u00e1 los resultados.", parent=win)

        def guardar_y_avanzar():
            if not data_store.partidos_ronda:
                messagebox.showwarning("Sin partidos",
                                       "Gener\u00e1 la Ronda 32 primero.", parent=win)
                return

            resultados = {}
            for idx, widgets in match_widgets.items():
                e1, e2 = widgets[0], widgets[1]
                g1 = e1.get().strip()
                g2 = e2.get().strip()
                if not g1 or not g2:
                    continue
                try:
                    g1n, g2n = int(g1), int(g2)
                    resultado = {"local": g1n, "visitante": g2n}

                    if g1n == g2n:
                        # Popup para ingresar penales
                        p = data_store.partidos_ronda[idx]
                        pen_win = tk.Toplevel(win)
                        pen_win.title("Penales")
                        centrar_ventana(pen_win, 380, 220)
                        pen_win.configure(bg=C["bg"])
                        pen_win.transient(win)
                        pen_win.grab_set()

                        tk.Label(pen_win,
                                 text=f"⚽ EMPATE: {p['local']} vs {p['visitante']}",
                                 fg=C["cyan"], bg=C["bg"],
                                 font=("Arial", 11, "bold")).pack(pady=(15, 5))
                        tk.Label(pen_win,
                                 text=f"Resultado: {g1n} - {g2n}\nIngresá los goles de penales:",
                                 fg=C["fg"], bg=C["bg"],
                                 font=("Arial", 10)).pack(pady=(0, 10))

                        row_pen = tk.Frame(pen_win, bg=C["bg"])
                        row_pen.pack()

                        tk.Label(row_pen, text=p["local"], fg=C["green"], bg=C["bg"],
                                 font=("Arial", 10, "bold")).pack(side="left", padx=5)
                        ep1 = tk.Entry(row_pen, bg=C["input_bg"], fg="white",
                                       insertbackground="white", relief="flat",
                                       font=("Arial", 12), width=4, justify="center")
                        ep1.pack(side="left", padx=3)
                        tk.Label(row_pen, text="-", fg=C["fg"], bg=C["bg"],
                                 font=("Arial", 12, "bold")).pack(side="left")
                        ep2 = tk.Entry(row_pen, bg=C["input_bg"], fg="white",
                                       insertbackground="white", relief="flat",
                                       font=("Arial", 12), width=4, justify="center")
                        ep2.pack(side="left", padx=3)
                        tk.Label(row_pen, text=p["visitante"], fg=C["cyan"], bg=C["bg"],
                                 font=("Arial", 10, "bold")).pack(side="left", padx=5)

                        penales_resultado = [None]
                        error_lbl = tk.Label(pen_win, text="", fg="#FF4444", bg=C["bg"],
                                             font=("Arial", 9))
                        error_lbl.pack()

                        def confirmar_penales(ep1=ep1, ep2=ep2):
                            try:
                                pn1 = int(ep1.get().strip())
                                pn2 = int(ep2.get().strip())
                                if pn1 == pn2:
                                    error_lbl.config(
                                        text="Los penales no pueden empatar.")
                                    return
                                penales_resultado[0] = [pn1, pn2]
                                pen_win.destroy()
                            except ValueError:
                                error_lbl.config(text="Ingresá números válidos.")

                        tk.Button(pen_win, text="✅ Confirmar",
                                  command=confirmar_penales,
                                  bg=C["cyan"], fg="#000000",
                                  font=("Arial", 10, "bold"),
                                  bd=0, cursor="hand2",
                                  padx=14, pady=6).pack(pady=10)

                        pen_win.wait_window()

                        if penales_resultado[0] is None:
                            return  # Cerró el popup sin confirmar
                        resultado["penales"] = penales_resultado[0]

                    resultados[idx] = resultado

                except ValueError:
                    messagebox.showerror("Error",
                                         f"Goles inválidos en partido {idx+1}.",
                                         parent=win)
                    return

            if len(resultados) != len(match_widgets):
                faltan = len(match_widgets) - len(resultados)
                messagebox.showwarning("Resultados incompletos",
                                       f"Faltan {faltan} partido(s) por completar.\nComplet\u00e1 todos los resultados antes de avanzar.",
                                       parent=win)
                return

            penales_antes = len(data_store.historial_penales)
            nuevos = procesar_resultados_ronda(resultados)
            guardar_datos()

            # Mostrar penales nuevos de esta ronda
            nuevos_penales = data_store.historial_penales[penales_antes:]
            for p in nuevos_penales:
                pen = p["penales"]
                messagebox.showinfo(
                    "⚽ Desempate por Penales",
                    f"{p['local']}  vs  {p['visitante']}\n\n"
                    f"Resultado 90': {p['goles'][0]} - {p['goles'][1]}\n"
                    f"Penales: {pen[0]} - {pen[1]}\n\n"
                    f"✅ Avanza: {p['ganador']}",
                    parent=win)
            if nuevos is None:
                if not data_store.partidos_ronda:
                    messagebox.showwarning("Error", "No hay partidos en esta ronda.", parent=win)
                    return
                ganador = data_store.partidos_ronda[0]["ganador"]
                if data_store.ronda_actual == "F":
                    msg = f"\u00a1Torneo finalizado!\n\nCampe\u00f3n: {ganador}"
                    messagebox.showinfo("Final", msg, parent=win)
                elif len(data_store.partidos_ronda) >= 2:
                    if len(data_store.partidos_ronda) == 2:
                        ganador2 = data_store.partidos_ronda[1]["ganador"]
                        messagebox.showinfo("Semifinales completadas",
                            f"Finalistas: {ganador} vs {ganador2}", parent=win)
                    else:
                        messagebox.showinfo("Ronda completada",
                            "Resultados guardados.", parent=win)
                construir_partidos()
                return

            if nuevos:
                ronda_nombre = obtener_estado_eliminatorias()["nombre_ronda"]
                messagebox.showinfo("Avanzar",
                                    f"Resultados guardados. Se gener\u00f3 {ronda_nombre}.",
                                    parent=win)
                construir_partidos()

        def mostrar_avances():
            avances = obtener_maximo_avance()
            av_win = tk.Toplevel(win)
            av_win.title("M\u00e1ximo Avance de Equipos")
            centrar_ventana(av_win, 600, 500)
            av_win.configure(bg=C["bg"])
            av_win.transient(win)
            av_win.grab_set()

            tk.Label(av_win, text="M\u00c1XIMO AVANCE DE EQUIPOS", fg=C["cyan"], bg=C["bg"],
                     font=("Arial", 12, "bold")).pack(pady=(15, 10))

            av_frame = tk.Frame(av_win, bg=C["bg"])
            av_frame.pack(fill="both", expand=True, padx=20)

            av_tree = ttk.Treeview(av_frame, columns=("Equipo", "M\u00e1ximo Avance", "Nivel"),
                                   show="headings", height=20)
            av_tree.heading("Equipo", text="Equipo")
            av_tree.heading("M\u00e1ximo Avance", text="M\u00e1ximo Avance")
            av_tree.heading("Nivel", text="Nivel")
            av_tree.column("Equipo", width=200, anchor="w")
            av_tree.column("M\u00e1ximo Avance", width=200, anchor="center")
            av_tree.column("Nivel", width=80, anchor="center")

            av_sv = tk.Scrollbar(av_frame, orient="vertical", command=av_tree.yview)
            av_tree.configure(yscrollcommand=av_sv.set)
            av_tree.pack(side="left", fill="both", expand=True)
            av_sv.pack(side="right", fill="y")

            # Estilo
            style_av = ttk.Style()
            style_av.theme_use("clam")
            style_av.configure("Treeview", background=C["input_bg"], foreground="white",
                               fieldbackground=C["input_bg"], rowheight=24)
            style_av.configure("Treeview.Heading", background=C["gray"], foreground="white")

            for nom, ronda, nivel in sorted(avances, key=lambda x: -x[2]):
                av_tree.insert("", "end", values=(nom, ronda, nivel))

        tk.Button(btn_frame, text="\U0001f3b2 Generar Ronda 32", command=generar_r32,
                  **self._estilo_boton(width=18, bg=C["cyan"], fg="#000000")).pack(side="left", padx=3)
        tk.Button(btn_frame, text="\u25b6 Guardar y Avanzar", command=guardar_y_avanzar,
                  **self._estilo_boton(width=18, bg=C["green"], fg="#000000")).pack(side="left", padx=3)
        tk.Button(btn_frame, text="\U0001f4ca M\u00e1ximo Avance", command=mostrar_avances,
                  **self._estilo_boton(width=18)).pack(side="right", padx=3)

    # ── SIMULADOR DE PARTIDOS ───────────────────

    def abrir_simulador(self):
        win = tk.Toplevel(self.root)
        win.title("Simulador de Partidos")
        centrar_ventana(win, 600, 400)
        win.configure(bg=C["bg"])
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="SIMULADOR DE PARTIDOS", fg=C["cyan"], bg=C["bg"],
                 font=("Arial", 12, "bold")).pack(pady=(15, 10))

        # Obtener lista de países disponibles en el mundial
        paises_disp = sorted(data_store.paises_mundial)

        # Frame para equipo local
        frame1 = tk.Frame(win, bg=C["card"], padx=15, pady=10)
        frame1.pack(fill="x", padx=20, pady=5)

        tk.Label(frame1, text="🏠 Equipo Local", fg=C["green"], bg=C["card"],
                 font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        cb1 = ttk.Combobox(frame1, values=paises_disp, state="readonly", width=40,
                          font=("Arial", 10))
        cb1.pack(fill="x")

        # Frame para equipo visitante
        frame2 = tk.Frame(win, bg=C["card"], padx=15, pady=10)
        frame2.pack(fill="x", padx=20, pady=5)

        tk.Label(frame2, text="✈️ Equipo Visitante", fg=C["cyan"], bg=C["card"],
                 font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        cb2 = ttk.Combobox(frame2, values=paises_disp, state="readonly", width=40,
                          font=("Arial", 10))
        cb2.pack(fill="x")

        # Botón Iniciar Simulación
        def iniciar_simulacion():
            local = cb1.get().strip()
            visitante = cb2.get().strip()

            if not local or not visitante:
                messagebox.showwarning("Seleccionar países", 
                                      "Debes seleccionar ambos equipos.", parent=win)
                return
            
            # Validar que ambos países estén en el mundial
            if local not in paises_disp:
                messagebox.showwarning("País no válido",
                                      f"'{local}' no está en el mundial.", parent=win)
                return
            if visitante not in paises_disp:
                messagebox.showwarning("País no válido",
                                      f"'{visitante}' no está en el mundial.", parent=win)
                return
            
            if local == visitante:
                messagebox.showwarning("Equipos diferentes",
                                      "No puede haber dos equipos iguales.", parent=win)
                return

            win.destroy()
            self._iniciar_partido_simulado(local, visitante)

        btn_frame = tk.Frame(win, bg=C["bg"])
        btn_frame.pack(fill="x", pady=(20, 15))
        tk.Button(btn_frame, text="▶ Iniciar Simulación",
                  command=iniciar_simulacion,
                  bg=C["cyan"], fg="#000000", font=("Arial", 11, "bold"),
                  bd=0, cursor="hand2", padx=20, pady=8).pack()

    def _iniciar_partido_simulado(self, local, visitante):

        # Crear ventana principal del simulador
        win_sim = tk.Toplevel(self.root)
        win_sim.title(f"SIMULACIÓN: {local} vs {visitante}")
        centrar_ventana(win_sim, 1000, 700)
        win_sim.configure(bg=C["bg"])
        win_sim.transient(self.root)
        win_sim.grab_set()

        # Variables de control
        tiempo_minuto = [0]  # Minuto actual (0-90)
        simulando = [True]  # Si está corriendo
        eventos_log = []  # Registro de eventos
        goles = [0, 0]  # Goles [local, visitante]
        tarjetas = [[{"AM": 0, "RJ": 0}], [{"AM": 0, "RJ": 0}]]  # Tarjetas por equipo
        última_generación = [0]  # Último minuto donde se generó evento

        # ── HEADER ──────────────────────────────
        header = tk.Frame(win_sim, bg=C["cyan"], height=60)
        header.pack(fill="x", padx=5, pady=5)

        info_text = f"🏆 {local.upper()} {goles[0]} - {goles[1]} {visitante.upper()}"
        lbl_header = tk.Label(header, text=info_text, fg="#000000", bg=C["cyan"],
                             font=("Arial", 16, "bold"), padx=10, pady=10)
        lbl_header.pack(expand=True)

        # ── CRONÓMETRO ──────────────────────────
        frame_tiempo = tk.Frame(win_sim, bg=C["card"], padx=15, pady=10)
        frame_tiempo.pack(fill="x", padx=5, pady=5)

        lbl_tiempo = tk.Label(frame_tiempo, text="00:00", fg=C["green"], bg=C["card"],
                             font=("Consolas", 28, "bold"))
        lbl_tiempo.pack()
        
        lbl_tiempo_info = tk.Label(frame_tiempo, text="(Primer tiempo)", fg=C["disabled"], bg=C["card"],
                                   font=("Consolas", 9))
        lbl_tiempo_info.pack()

        # ── EVENTOS LOG ─────────────────────────
        frame_log = tk.Frame(win_sim, bg=C["bg"])
        frame_log.pack(fill="both", expand=True, padx=5, pady=5)

        text_log = tk.Text(frame_log, bg=C["input_bg"], fg="white", font=("Consolas", 9),
                          relief="flat", height=15)
        text_log.pack(fill="both", expand=True)

        scroll_log = tk.Scrollbar(text_log, orient="vertical", command=text_log.yview)
        text_log.configure(yscrollcommand=scroll_log.set)
        scroll_log.pack(side="right", fill="y")

        # ── CONTROLES ───────────────────────────
        frame_btn = tk.Frame(win_sim, bg=C["bg"])
        frame_btn.pack(fill="x", padx=5, pady=5)

        def toggle_simulacion():
            simulando[0] = not simulando[0]
            btn_play.config(text="⏸ Pausar" if simulando[0] else "▶ Reanudar")

        def skip_evento():
            tiempo_minuto[0] += 5
            if tiempo_minuto[0] > 90:
                tiempo_minuto[0] = 90
            generar_evento()
            minutos = tiempo_minuto[0]
            lbl_tiempo.config(text=f"{minutos:02d}:00")
            if minutos <= 45:
                lbl_tiempo_info.config(text="(Primer tiempo)")
            else:
                lbl_tiempo_info.config(text=f"(Segundo tiempo - {minutos - 45}' del ST)")

        def finalizar():
            win_sim.destroy()

        btn_play = tk.Button(frame_btn, text="⏸ Pausar", command=toggle_simulacion,
                           bg=C["green"], fg="#000000", font=("Arial", 10, "bold"),
                           bd=0, cursor="hand2", padx=12, pady=6)
        btn_play.pack(side="left", padx=5)

        tk.Button(frame_btn, text="⏩ Skip", command=skip_evento,
                 bg=C["cyan"], fg="#000000", font=("Arial", 10, "bold"),
                 bd=0, cursor="hand2", padx=12, pady=6).pack(side="left", padx=5)

        tk.Button(frame_btn, text="❌ Finalizar", command=finalizar,
                 bg="#FF3333", fg="white", font=("Arial", 10, "bold"),
                 bd=0, cursor="hand2", padx=12, pady=6).pack(side="left", padx=5)

        # ── LÓGICA DE SIMULACIÓN ────────────────
        def _marcar_suplentes(lista):
            jug = []
            for i, j in enumerate(lista):
                jug.append(j if i < 11 else j + " (s)")
            return jug

        jugadores_local = _marcar_suplentes(jugadores_por_equipo.get(local, []))
        jugadores_visitante = _marcar_suplentes(jugadores_por_equipo.get(visitante, []))

        salidos_local = set()
        salidos_visitante = set()

        def _titulares(lista):
            return [j for j in lista if "(s)" not in j]

        def _en_campo(lista, salidos):
            return [j for j in lista if "(s)" not in j and j not in salidos]

        cambios_efectuados = [0, 0]

        def generar_evento():
            if tiempo_minuto[0] >= 90:
                return

            eventos_posibles = []

            # Gol
            if random.random() < 0.06:
                equipo = random.choice([0, 1])
                salidos = [salidos_local, salidos_visitante][equipo]
                en_campo = _en_campo([jugadores_local, jugadores_visitante][equipo], salidos)
                if not en_campo:
                    return
                jug = random.choice(en_campo)
                goles[equipo] += 1
                evento = f"{tiempo_minuto[0]:02d}' ⚽ GOL de {jug}"
                eventos_posibles.append(evento)

            # Tarjeta amarilla
            elif random.random() < 0.08:
                equipo = random.choice([0, 1])
                salidos = [salidos_local, salidos_visitante][equipo]
                en_campo = _en_campo([jugadores_local, jugadores_visitante][equipo], salidos)
                if not en_campo:
                    return
                jug = random.choice(en_campo)
                tarjetas[equipo][0]["AM"] += 1
                evento = f"{tiempo_minuto[0]:02d}' 🟨 TARJETA AMARILLA: {jug}"
                eventos_posibles.append(evento)

            # Tarjeta roja
            elif random.random() < 0.02:
                equipo = random.choice([0, 1])
                jugadores = [jugadores_local, jugadores_visitante][equipo]
                salidos = [salidos_local, salidos_visitante][equipo]
                en_campo = _en_campo(jugadores, salidos)
                if not en_campo:
                    return
                jug = random.choice(en_campo)
                tarjetas[equipo][0]["RJ"] += 1
                evento = f"{tiempo_minuto[0]:02d}' 🔴 TARJETA ROJA: {jug}"
                eventos_posibles.append(evento)
                salidos.add(jug)

                if jug == jugadores[0] and len(jugadores) > 11:
                    arquero_suplente = jugadores[11]
                    jugadores[0] = arquero_suplente
                    evento += f"\n{tiempo_minuto[0]:02d}' 🔄 Entra {arquero_suplente} (arquero suplente)"
                    eventos_posibles[-1] = evento

            # Cambio local
            elif random.random() < 0.04 and cambios_efectuados[0] < 3:
                en_campo = _en_campo(jugadores_local, salidos_local)
                suplentes = [j for j in jugadores_local if "(s)" in j and j not in salidos_local]
                if suplentes and en_campo:
                    jug_sale = random.choice(en_campo)
                    jug_entra = random.choice(suplentes)
                    idx_sale = jugadores_local.index(jug_sale)
                    idx_entra = jugadores_local.index(jug_entra)
                    jugadores_local[idx_sale] = jug_sale + " (s)"
                    jugadores_local[idx_entra] = jug_entra.replace(" (s)", "")
                    salidos_local.add(jug_sale)
                    cambios_efectuados[0] += 1
                    evento = f"{tiempo_minuto[0]:02d}' 🔄 CAMBIO {local}: sale {jug_sale}, entra {jug_entra.replace(' (s)', '')}"
                    eventos_posibles.append(evento)

            # Cambio visitante
            elif random.random() < 0.04 and cambios_efectuados[1] < 3:
                en_campo = _en_campo(jugadores_visitante, salidos_visitante)
                suplentes = [j for j in jugadores_visitante if "(s)" in j and j not in salidos_visitante]
                if suplentes and en_campo:
                    jug_sale = random.choice(en_campo)
                    jug_entra = random.choice(suplentes)
                    idx_sale = jugadores_visitante.index(jug_sale)
                    idx_entra = jugadores_visitante.index(jug_entra)
                    jugadores_visitante[idx_sale] = jug_sale + " (s)"
                    jugadores_visitante[idx_entra] = jug_entra.replace(" (s)", "")
                    salidos_visitante.add(jug_sale)
                    cambios_efectuados[1] += 1
                    evento = f"{tiempo_minuto[0]:02d}' 🔄 CAMBIO {visitante}: sale {jug_sale}, entra {jug_entra.replace(' (s)', '')}"
                    eventos_posibles.append(evento)

            # Falta
            elif random.random() < 0.10:
                equipo = random.choice([0, 1])
                salidos = [salidos_local, salidos_visitante][equipo]
                en_campo = _en_campo([jugadores_local, jugadores_visitante][equipo], salidos)
                if not en_campo:
                    return
                jug = random.choice(en_campo)
                evento = f"{tiempo_minuto[0]:02d}' ⚠️  FALTA: {jug}"
                eventos_posibles.append(evento)

            if eventos_posibles:
                evento = eventos_posibles[0]
                eventos_log.append(evento)
                text_log.insert("end", evento + "\n")
                text_log.see("end")

                # Actualizar header con nuevos goles
                info_text = f"🏆 {local.upper()} {goles[0]} - {goles[1]} {visitante.upper()}"
                lbl_header.config(text=info_text)

        def actualizar_simulacion():
            if simulando[0] and tiempo_minuto[0] < 90:
                # Avanzar tiempo (cada 1000ms = 1 segundo real = 1 minuto de juego)
                tiempo_minuto[0] += 1

                # Generar eventos aleatorios cada cierto tiempo
                if random.random() < 0.20:  # 20% cada actualización
                    generar_evento()

            elif tiempo_minuto[0] >= 90 and simulando[0]:
                # Partido finalizado - detener simulación
                simulando[0] = False

            # Actualizar cronómetro visual (en formato MM:SS)
            minutos = tiempo_minuto[0]
            tiempo_str = f"{minutos:02d}:00"
            lbl_tiempo.config(text=tiempo_str)
            
            # Actualizar texto de tiempo (primer o segundo tiempo)
            if minutos <= 45:
                lbl_tiempo_info.config(text="(Primer tiempo)")
            else:
                lbl_tiempo_info.config(text=f"(Segundo tiempo - {minutos - 45}' del ST)")

            # Programar siguiente actualización (cada 1000ms = 1 segundo)
            if tiempo_minuto[0] < 90:
                win_sim.after(1000, actualizar_simulacion)
            else:
                win_sim.after(500, lambda: None)  # Pequeña espera final

        # Iniciar actualización
        actualizar_simulacion()


# ── PUNTO DE ENTRADA ────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazMundial(root)
    root.mainloop()
