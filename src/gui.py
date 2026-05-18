# ─────────────────────────────────────────────────────────────
#  GUI – Interfaz gráfica del Sistema de Control de Torneo
#  Librerías: solo tkinter + calendar (biblioteca estándar)
# ─────────────────────────────────────────────────────────────

import tkinter as tk
from tkinter import messagebox, ttk
import calendar
from datetime import datetime

# Módulos propios del paquete src/
from . import data_store 
from .models import Equipo
from .services import configuracion, generar_pares_grupo, calcular_tabla_grupo


# ─────────────────────────────────────────────────────────────
#  CalendarPopup – Ventana emergente con calendario mensual
#  Permite navegar meses con ◀ ▶ y elegir un día haciendo clic
# ─────────────────────────────────────────────────────────────

class CalendarPopup:
    MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    DIAS = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback  # función que recibe "DD/MM/AAAA"
        hoy = datetime.now()
        self.anio = hoy.year
        self.mes = hoy.month
        self.win = None

    # Construye y muestra la ventana del calendario
    def _abrir(self):
        self.win = tk.Toplevel(self.parent)
        self.win.title("Seleccionar fecha")
        centrar_ventana(self.win, 280, 260)
        self.win.configure(bg=C["bg"])
        self.win.resizable(False, False)
        self.win.transient(self.parent)
        self.win.grab_set()

        # Barra de navegación: botón ◀, etiqueta mes/año, botón ▶
        nav = tk.Frame(self.win, bg=C["bg"])
        nav.pack(pady=(10, 5))

        tk.Button(nav, text="◀", command=self._mes_prev,
                  bg=C["gray"], fg=C["fg"], bd=0, width=3,
                  font=("Arial", 10, "bold"), cursor="hand2").pack(side="left", padx=5)
        self.lbl_mes = tk.Label(nav, text="", fg=C["cyan"], bg=C["bg"],
                                font=("Arial", 11, "bold"), width=20)
        self.lbl_mes.pack(side="left")
        tk.Button(nav, text="▶", command=self._mes_next,
                  bg=C["gray"], fg=C["fg"], bd=0, width=3,
                  font=("Arial", 10, "bold"), cursor="hand2").pack(side="left", padx=5)

        # Encabezados de los días de la semana
        dias_f = tk.Frame(self.win, bg=C["bg"])
        dias_f.pack(padx=10)
        for i, d in enumerate(self.DIAS):
            color = C["green"] if i >= 5 else C["fg"]
            tk.Label(dias_f, text=d, fg=color, bg=C["bg"],
                     font=("Arial", 9, "bold"), width=4).grid(row=0, column=i, pady=4)

        # Grilla de números de día (se redibuja al cambiar de mes)
        self.grid_frame = tk.Frame(self.win, bg=C["bg"])
        self.grid_frame.pack(padx=10, pady=(0, 10))
        self._dibujar_mes()

    # Dibuja todos los botones de día del mes actual
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

    # Retrocede un mes
    def _mes_prev(self):
        if self.mes == 1:
            self.mes = 12
            self.anio -= 1
        else:
            self.mes -= 1
        self._dibujar_mes()

    # Avanza un mes
    def _mes_next(self):
        if self.mes == 12:
            self.mes = 1
            self.anio += 1
        else:
            self.mes += 1
        self._dibujar_mes()

    # Al hacer clic en un día, ejecuta el callback con la fecha formateada y cierra
    def _seleccionar(self, dia):
        self.callback(f"{dia:02d}/{self.mes:02d}/{self.anio}")
        self.win.destroy()


# ─────────────────────────────────────────────────────────────
#  DateEntry – Campo de fecha con botón que abre el calendario
#  Muestra "DD/MM/AAAA" hasta que se selecciona una fecha
# ─────────────────────────────────────────────────────────────

class DateEntry(tk.Frame):
    def __init__(self, parent, label, **kw):
        super().__init__(parent, **kw)
        self.configure(bg=C["bg"])
        # Etiqueta del campo (ej: "Fecha inicio")
        tk.Label(self, text=label, fg=C["fg"], bg=C["bg"],
                 font=("Arial", 10)).pack(anchor="w")
        # Fila con label de fecha + botón calendario
        row = tk.Frame(self, bg=C["bg"])
        row.pack(fill="x")
        self.lbl_fecha = tk.Label(row, text="DD/MM/AAAA", fg=C["disabled"],
                                  bg=C["input_bg"], font=("Arial", 10),
                                  anchor="w", padx=8, pady=4, relief="flat")
        self.lbl_fecha.pack(side="left", fill="x", expand=True)
        tk.Button(row, text="📅", command=self._abrir_calendario,
                  bg=C["gray"], fg=C["fg"], bd=0, width=3,
                  font=("Arial", 10), cursor="hand2").pack(side="right", padx=(4, 0))

    # Abre el popup del calendario
    def _abrir_calendario(self):
        cp = CalendarPopup(self, self._set_fecha)
        cp._abrir()

    # Recibe la fecha desde CalendarPopup y la muestra
    def _set_fecha(self, fecha):
        self.lbl_fecha.config(text=fecha, fg="white")

    # Devuelve la fecha seleccionada o cadena vacía si no se eligió
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
#  Administra todas las ventanas y la navegación entre ellas
# ─────────────────────────────────────────────────────────────

class InterfazMundial:

    # ── Inicialización ────────────────────────────
    # Configura la ventana raíz a pantalla completa vertical
    # y construye los componentes fijos (header, logo, menú)

    def __init__(self, root):
        self.root = root
        self.root.title("FIFA World Cup 2026 - Sistema de Control")
        self.root.configure(bg=C["bg"])
        pantalla_h = self.root.winfo_screenheight()
        self.root.geometry(f"500x{pantalla_h}+{(self.root.winfo_screenwidth()-500)//2}+0")

        # Estado de la aplicación
        self.torneo_configurado = False
        self.disponibles = set()      # países aún no asignados a grupos
        self.asignaciones = {}        # { grupo: [lista de países] }
        self.datos_config = None      # resultado de la configuración inicial
        self.btn_registro = None

        self.crear_zona_titulos()
        self.crear_identidad_visual()
        self.crear_menu_principal()

    # ── HEADER ──────────────────────────────────
    # Barra superior con nombre de la materia, título y reloj en vivo

    def crear_zona_titulos(self):
        header = tk.Frame(self.root, bg=C["bg"],
                          highlightbackground=C["cyan"], highlightthickness=1, bd=0)
        header.pack(fill="x", padx=25, pady=(15, 5))

        tk.Label(header, text="Algoritmos y Estructuras de Datos II",
                 fg=C["fg"], bg=C["bg"], font=("Arial", 10, "bold")).pack(pady=(8, 2))
        tk.Label(header, text="CONTROL DE TORNEO DEPORTIVO",
                 fg=C["cyan"], bg=C["bg"], font=("Arial", 14, "bold")).pack(pady=2)

        self.lbl_reloj = tk.Label(header, fg=C["green"], bg=C["bg"], font=("Consolas", 11))
        self.lbl_reloj.pack(pady=(2, 8))
        self.actualizar_reloj()

    # Actualiza el reloj cada 1 segundo
    def actualizar_reloj(self):
        self.lbl_reloj.config(
            text=datetime.now().strftime("Fecha: %d/%m/%Y   |   Hora: %H:%M:%S"))
        self.root.after(1000, self.actualizar_reloj)

    # ── LOGO ────────────────────────────────────
    # Logo visual "26" + "FIFA WORLD CUP"

    def crear_identidad_visual(self):
        frame = tk.Frame(self.root, bg=C["bg"])
        frame.pack(pady=(0, 5))
        tk.Label(frame, text="2\n6", fg=C["green"], bg=C["bg"],
                 font=("Arial Black", 44), justify="center").pack()
        tk.Label(frame, text="FIFA WORLD CUP", fg=C["fg"], bg=C["bg"],
                 font=("Arial", 9, "bold")).pack()

    # ── MENÚ PRINCIPAL ───────────────────────────
    # Botones de navegación centrados verticalmente
    # con espaciadores expandibles arriba y abajo

    def _estilo_boton(self, **kw):
        # Base de estilo reutilizable para todos los botones
        base = {"fg": C["fg"], "bg": C["gray"],
                "activebackground": C["cyan"], "activeforeground": "#000000",
                "font": ("Arial", 11, "bold"), "width": 32, "bd": 0,
                "cursor": "hand2", "pady": 8}
        base.update(kw)
        return base

    def crear_menu_principal(self):
        frame = tk.Frame(self.root, bg=C["bg"])
        frame.pack(fill="both", expand=True, padx=25)

        tk.Label(frame, text="MENÚ PRINCIPAL", fg=C["fg"], bg=C["bg"],
                 font=("Arial", 12, "bold")).pack(pady=(10, 5))

        botones_frame = tk.Frame(frame, bg=C["bg"])
        botones_frame.pack(fill="both", expand=True)

        # Espaciador superior: empuja los botones hacia el centro
        espaciador_top = tk.Frame(botones_frame, bg=C["bg"])
        espaciador_top.pack(fill="both", expand=True)

        buttons = [
            ("1. Configuración del Torneo", self.abrir_configuracion, None),
            ("2. Registro de Resultados", self.abrir_resultados, "disabled"),
            ("3. Emisión de Informes", self.abrir_informes, None),
            ("4. Salir", self.root.quit, "red_hover"),
        ]
        self.menu_buttons = {}
        for text, cmd, extra in buttons:
            kw = {}
            if extra == "disabled":
                # Botón deshabilitado hasta configurar torneo
                kw = {"bg": C["disabled"], "fg": "#888888", "state": "disabled"}
            elif extra == "red_hover":
                # Botón de salir con hover rojo
                kw = {"activebackground": "#FF3333"}
            btn = tk.Button(botones_frame, text=text, command=cmd, **self._estilo_boton(**kw))
            btn.pack(pady=5, anchor="center")
            self.menu_buttons[text] = btn

        # Espaciador inferior: equilibra el espacio vertical
        espaciador_bottom = tk.Frame(botones_frame, bg=C["bg"])
        espaciador_bottom.pack(fill="both", expand=True)

    # ── CONFIGURACIÓN DEL TORNEO ─────────────────
    # Ventana con nombre del torneo y dos fechas (con calendario)

    def abrir_configuracion(self):
        win = tk.Toplevel(self.root)
        win.title("Configuración del Torneo")
        centrar_ventana(win, 440, 400)
        win.configure(bg=C["bg"])
        win.transient(self.root)
        win.grab_set()

        card = tk.Frame(win, bg=C["card"], padx=20, pady=20)
        card.pack(pady=15, padx=20, fill="both", expand=True)

        tk.Label(card, text="CONFIGURACIÓN DEL TORNEO", fg=C["cyan"], bg=C["card"],
                 font=("Arial", 12, "bold")).pack(pady=(0, 18))

        # Campo: Nombre del torneo
        e_nombre = tk.Entry(card, bg=C["input_bg"], fg="white",
                            insertbackground="white", relief="flat", font=("Arial", 10))
        tk.Label(card, text="Nombre del torneo", fg=C["fg"], bg=C["card"],
                 font=("Arial", 10)).pack(anchor="w")
        e_nombre.pack(fill="x", pady=(2, 12))

        # Campos de fecha con calendario visual
        e_inicio = DateEntry(card, "Fecha inicio (DD/MM/AAAA)")
        e_inicio.pack(fill="x", pady=(0, 10))
        e_fin = DateEntry(card, "Fecha fin (DD/MM/AAAA)")
        e_fin.pack(fill="x", pady=(0, 18))

        # Guarda la configuración y pasa a asignación de grupos
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
    # Interfaz de dos listas: países disponibles (izq) y grupo (der)

    def abrir_asignacion_grupos(self):
        win = tk.Toplevel(self.root)
        win.title("Asignación de Equipos a Grupos")
        centrar_ventana(win, 780, 580)
        win.configure(bg=C["bg"])
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="ASIGNACIÓN DE EQUIPOS A GRUPOS", fg=C["cyan"], bg=C["bg"],
                 font=("Arial", 12, "bold")).pack(pady=(15, 2))
        tk.Label(win, text="Seleccioná un país disponible y agregalo a un grupo (4 por grupo)",
                 fg=C["green"], bg=C["bg"], font=("Arial", 9)).pack(pady=(0, 8))

        main = tk.Frame(win, bg=C["bg"])
        main.pack(fill="both", expand=True, padx=15, pady=5)

        # ── Panel izquierdo: lista de países sin asignar
        left = tk.LabelFrame(main, text="PAÍSES DISPONIBLES",
                             fg=C["cyan"], bg=C["card"], font=("Arial", 10, "bold"),
                             padx=5, pady=5)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.lbox_disp = tk.Listbox(left, bg=C["input_bg"], fg="white",
                                     selectbackground=C["cyan"],
                                     selectforeground="#000000",
                                     relief="flat", font=("Consolas", 10))
        self.lbox_disp.pack(side="left", fill="both", expand=True)

        sd = tk.Scrollbar(left, command=self.lbox_disp.yview)
        sd.pack(side="right", fill="y")
        self.lbox_disp.config(yscrollcommand=sd.set)
        self._refrescar_disp()

        # ── Panel derecho: selector de grupo + asignaciones
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

        # Lista de equipos ya asignados al grupo seleccionado
        self.lbox_asig = tk.Listbox(right, bg=C["input_bg"], fg="white",
                                     selectbackground=C["green"],
                                     selectforeground="#000000",
                                     relief="flat", font=("Consolas", 10), height=6)
        self.lbox_asig.pack(fill="both", expand=True)

        # Botones Agregar / Quitar
        btn_row = tk.Frame(right, bg=C["bg"])
        btn_row.pack(fill="x", pady=10)
        tk.Button(btn_row, text="→ Agregar", command=self._agregar,
                  **self._estilo_boton(width=13, bg=C["cyan"], fg="#000000")).pack(side="left", padx=3)
        tk.Button(btn_row, text="Quitar ←", command=self._quitar,
                  **self._estilo_boton(width=13)).pack(side="right", padx=3)

        self._refrescar_asig()

        # ── Barra de estado: contador asignados/pendientes
        self.lbl_status = tk.Label(win, text="", fg=C["green"], bg=C["bg"], font=("Consolas", 9))
        self.lbl_status.pack(pady=(0, 5))
        self._actualizar_status()

        # Botón final: crea los objetos Equipo y los partidos
        tk.Button(win, text="FINALIZAR CONFIGURACIÓN",
                  command=lambda: self._finalizar(win),
                  bg=C["cyan"], fg="#000000",
                  **{k: v for k, v in self._estilo_boton(width=30).items()
                     if k not in ("bg", "fg")}).pack(pady=8)

    # Refresca la lista de países disponibles desde el conjunto
    def _refrescar_disp(self):
        self.lbox_disp.delete(0, "end")
        for p in sorted(self.disponibles):
            self.lbox_disp.insert("end", p)

    # Refresca la lista de asignados del grupo seleccionado
    def _refrescar_asig(self, event=None):
        self.lbox_asig.delete(0, "end")
        grupo = self.cb_grupo.get()
        for i, p in enumerate(self.asignaciones.get(grupo, []), 1):
            self.lbox_asig.insert("end", f"{i}. {p}")

    # Mueve un país de disponibles al grupo seleccionado
    def _agregar(self):
        grupo = self.cb_grupo.get()
        sel = self.lbox_disp.curselection()
        if not sel:
            messagebox.showwarning("Seleccionar país", "Seleccioná un país de la lista.")
            return
        if len(self.asignaciones[grupo]) >= 4:
            messagebox.showwarning("Grupo completo",
                                   f"El grupo {grupo} ya tiene 4 equipos.")
            return
        pais = self.lbox_disp.get(sel[0])
        self.disponibles.discard(pais)
        self.asignaciones[grupo].append(pais)
        self._refrescar_disp()
        self._refrescar_asig()
        self._actualizar_status()

    # Devuelve un país del grupo a la lista de disponibles
    def _quitar(self):
        grupo = self.cb_grupo.get()
        sel = self.lbox_asig.curselection()
        if not sel:
            return
        texto = self.lbox_asig.get(sel[0])
        pais = texto.split(". ", 1)[1]
        self.asignaciones[grupo].remove(pais)
        self.disponibles.add(pais)
        self._refrescar_disp()
        self._refrescar_asig()
        self._actualizar_status()

    # Actualiza el texto del label de estado
    def _actualizar_status(self):
        total = sum(len(v) for v in self.asignaciones.values())
        self.lbl_status.config(text=f"Asignados: {total}/48  |  Pendientes: {len(self.disponibles)}")

    # Finaliza la configuración: valida, crea objetos Equipo y genera partidos
    def _finalizar(self, win):
        # Validar que cada grupo tenga exactamente 4 equipos
        for g, eqs in self.asignaciones.items():
            if len(eqs) != 4:
                messagebox.showerror("Error",
                                     f"Grupo {g} tiene {len(eqs)} equipos (deben ser 4).",
                                     parent=win)
                return

        # Crear objetos Equipo en data_store.tablagral
        for g, eqs in self.asignaciones.items():
            for i, nom in enumerate(eqs, 1):
                abrev = "".join(c for c in nom.upper() if c.isalpha())[:3]
                data_store.tablagral[nom] = Equipo(
                    nombre=nom, abreviatura=abrev, prefijo="",
                    grupo=g, id_identificador=f"{g}{i}"
                )

        # Generar los enfrentamientos de cada grupo
        for g, eqs in self.asignaciones.items():
            for e1, e2 in generar_pares_grupo(eqs):
                data_store.tablagral[e1].partidos.append(
                    {"rival": e2, "fecha": "", "hora": "", "goles": None})
                data_store.tablagral[e2].partidos.append(
                    {"rival": e1, "fecha": "", "hora": "", "goles": None})

        # Habilitar el botón de registro de resultados
        self.torneo_configurado = True
        self.menu_buttons["2. Registro de Resultados"].config(
            state="normal", bg=C["gray"], fg=C["fg"])
        messagebox.showinfo(
            "Éxito",
            f"Torneo '{data_store.nombre_torneo}' configurado.\n48 equipos en 12 grupos, partidos generados.",
            parent=win)
        win.destroy()

    # ── REGISTRO DE RESULTADOS ────────────────────
    # Ventana con scroll que muestra los partidos de un grupo
    # y permite ingresar goles y tarjetas

    def abrir_resultados(self):
        if not self.torneo_configurado:
            messagebox.showwarning("Acceso Denegado",
                                   "Primero completá la Configuración del Torneo.")
            return

        win = tk.Toplevel(self.root)
        win.title("Registro de Resultados")
        centrar_ventana(win, 760, 540)
        win.configure(bg=C["bg"])
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="REGISTRO DE RESULTADOS", fg=C["cyan"], bg=C["bg"],
                 font=("Arial", 12, "bold")).pack(pady=(18, 2))
        tk.Label(win, text="Seleccioná un grupo y cargá los goles de cada partido",
                 fg=C["green"], bg=C["bg"], font=("Arial", 9)).pack(pady=(0, 12))

        # Selector de grupo
        top = tk.Frame(win, bg=C["bg"])
        top.pack(fill="x", padx=20)
        tk.Label(top, text="Grupo:", fg=C["fg"], bg=C["bg"],
                 font=("Arial", 10, "bold")).pack(side="left", padx=(0, 10))
        cb = ttk.Combobox(top, values=list("ABCDEFGHIJKL"),
                           state="readonly", width=4, font=("Arial", 10))
        cb.pack(side="left")

        # Área scrolleable con Canvas para los partidos
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

        # Construye las tarjetas de partido para el grupo seleccionado
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

                    # Tarjeta visual por partido
                    card = tk.Frame(scroll_frame, bg=C["card"], padx=12, pady=8)
                    card.pack(fill="x", pady=4)

                    row = tk.Frame(card, bg=C["card"])
                    row.pack(fill="x")

                    # Nombres de los equipos
                    tk.Label(row, text=e.nombre, fg=C["fg"], bg=C["card"],
                             font=("Arial", 10, "bold"), width=18, anchor="w").pack(side="left")
                    tk.Label(row, text="vs", fg=C["cyan"], bg=C["card"],
                             font=("Arial", 10)).pack(side="left", padx=5)
                    tk.Label(row, text=p["rival"], fg=C["fg"], bg=C["card"],
                             font=("Arial", 10, "bold"), width=18, anchor="w").pack(side="left")

                    # Campos de goles: "Goles: [  ] - [  ]"
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

                    # Si ya tenía goles cargados, mostrarlos
                    if p["goles"] is not None:
                        e_loc.insert(0, str(p["goles"][0]))
                        e_vis.insert(0, str(p["goles"][1]))

                    match_widgets[par] = (e_loc, e_vis, e.nombre, p["rival"])

                    # Botón para abrir la ventana de tarjetas
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

        # Guarda los resultados ingresados en los objetos del data_store
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
                messagebox.showinfo("Guardado", "Resultados guardados correctamente.", parent=win)

        btn_frame = tk.Frame(win, bg=C["bg"])
        btn_frame.pack(fill="x", pady=(5, 12))
        tk.Button(btn_frame, text="Guardar Resultados",
                  command=guardar_res,
                  bg=C["cyan"], fg="#000000",
                  **{k: v for k, v in self._estilo_boton(width=20).items()
                     if k not in ("bg", "fg")}).pack()

    # ── VENTANA DE TARJETAS ──────────────────────
    # Permite asignar tarjetas amarillas/rojas a jugadores
    # de ambos equipos de un partido

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

        # Crea una sección por equipo con campo: Jugador, Tipo, botón +
        def seccion(team_name):
            frame = tk.LabelFrame(main, text=team_name, fg=C["green"],
                                  bg=C["card"], font=("Arial", 10, "bold"),
                                  padx=10, pady=8)
            frame.pack(fill="x", pady=5)

            row = tk.Frame(frame, bg=C["card"])
            row.pack(fill="x")

            tk.Label(row, text="Jugador:", fg=C["fg"], bg=C["card"],
                     font=("Arial", 9)).pack(side="left")
            e_jug = tk.Entry(row, bg=C["input_bg"], fg="white",
                             insertbackground="white", relief="flat",
                             font=("Arial", 9), width=16)
            e_jug.pack(side="left", padx=5)

            tk.Label(row, text="Tipo:", fg=C["fg"], bg=C["card"],
                     font=("Arial", 9)).pack(side="left")
            cb_tipo = ttk.Combobox(row, values=["Amarilla", "Roja"],
                                    state="readonly", width=9, font=("Arial", 9))
            cb_tipo.pack(side="left", padx=5)
            cb_tipo.set("Amarilla")

            # Agrega la tarjeta al jugador en el data_store
            def agregar():
                jug = e_jug.get().strip()
                if not jug:
                    messagebox.showwarning("Nombre", "Escribí el nombre del jugador.", parent=win)
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
                e_jug.delete(0, "end")
                lbl_feedback.config(text=f"{jug} ({cb_tipo.get()}) → {team_name}")

            tk.Button(row, text="+", command=agregar,
                      bg=C["cyan"], fg="#000000", bd=0,
                      font=("Arial", 9, "bold"), cursor="hand2", width=3).pack(side="left", padx=5)

        seccion(local)
        seccion(visit)

        tk.Button(win, text="Cerrar", command=win.destroy,
                  **self._estilo_boton(width=20)).pack(pady=(10, 12))

    # ── EMISIÓN DE INFORMES ──────────────────────
    # Ventana con tabla de posiciones (Treeview) filtrada por grupo

    def abrir_informes(self):
        win = tk.Toplevel(self.root)
        win.title("Emisión de Informes")
        centrar_ventana(win, 780, 560)
        win.configure(bg=C["bg"])
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="EMISIÓN DE INFORMES", fg=C["cyan"], bg=C["bg"],
                 font=("Arial", 12, "bold")).pack(pady=(18, 2))
        tk.Label(win, text="Seleccioná un grupo para ver la tabla de posiciones",
                 fg=C["green"], bg=C["bg"], font=("Arial", 9)).pack(pady=(0, 12))

        # Selector de grupo
        top = tk.Frame(win, bg=C["bg"])
        top.pack(fill="x", padx=20)
        tk.Label(top, text="Grupo:", fg=C["fg"], bg=C["bg"],
                 font=("Arial", 10, "bold")).pack(side="left", padx=(0, 10))
        cb = ttk.Combobox(top, values=list("ABCDEFGHIJKL"),
                           state="readonly", width=4, font=("Arial", 10))
        cb.pack(side="left")

        # Treeview con las columnas de la tabla
        frame = tk.Frame(win, bg=C["bg"])
        frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        cols = ("ID", "Equipo", "PJ", "PTS", "GF", "GC", "AM", "RJ")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=12)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=70, anchor="center")
        tree.column("Equipo", width=170, anchor="w")
        tree.column("ID", width=40)

        # Estilo oscuro para el Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background=C["input_bg"],
                        foreground="white",
                        fieldbackground=C["input_bg"],
                        rowheight=26)
        style.configure("Treeview.Heading",
                        background=C["gray"],
                        foreground="white",
                        relief="flat")
        style.map("Treeview",
                  background=[("selected", C["cyan"])],
                  foreground=[("selected", "#000000")])

        sv = tk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sv.set)
        tree.pack(side="left", fill="both", expand=True)
        sv.pack(side="right", fill="y")

        # Al cambiar de grupo, recalcula y refresca la tabla
        def actualizar(event=None):
            for i in tree.get_children():
                tree.delete(i)
            k = cb.get()
            if not k:
                return
            for e in calcular_tabla_grupo(k):
                tree.insert("", "end", values=(
                    e.id or "", e.nombre, e.pj, e.puntos, e.gf, e.gc, e.am, e.rj))

        cb.bind("<<ComboboxSelected>>", actualizar)
        cb.set("A")
        actualizar()


# ── PUNTO DE ENTRADA ────────────────────────────
# Al ejecutar `python src/gui.py` directamente

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazMundial(root)
    root.mainloop()
