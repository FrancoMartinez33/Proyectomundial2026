import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from . import data_store
from .models import Equipo
from .services import configuracion, generar_pares_grupo, calcular_tabla_grupo


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


class InterfazMundial:
    def __init__(self, root):
        self.root = root
        self.root.title("FIFA World Cup 2026 - Sistema de Control")
        self.root.geometry("600x600")
        self.root.configure(bg=C["bg"])

        self.torneo_configurado = False
        self.disponibles = set()
        self.asignaciones = {}
        self.datos_config = None
        self.btn_registro = None

        self.crear_zona_titulos()
        self.crear_identidad_visual()
        self.crear_menu_principal()

    # ── HEADER ──────────────────────────────────

    def crear_zona_titulos(self):
        header = tk.Frame(self.root, bg=C["bg"],
                          highlightbackground=C["cyan"], highlightthickness=1, bd=0)
        header.pack(fill="x", padx=25, pady=20)

        tk.Label(header, text="Algoritmos y Estructuras de Datos II",
                 fg=C["fg"], bg=C["bg"], font=("Arial", 10, "bold")).pack(pady=(8, 2))
        tk.Label(header, text="CONTROL DE TORNEO DEPORTIVO",
                 fg=C["cyan"], bg=C["bg"], font=("Arial", 14, "bold")).pack(pady=2)

        self.lbl_reloj = tk.Label(header, fg=C["green"], bg=C["bg"], font=("Consolas", 11))
        self.lbl_reloj.pack(pady=(2, 8))
        self.actualizar_reloj()

    def actualizar_reloj(self):
        self.lbl_reloj.config(
            text=datetime.now().strftime("Fecha: %d/%m/%Y   |   Hora: %H:%M:%S"))
        self.root.after(1000, self.actualizar_reloj)

    # ── LOGO ────────────────────────────────────

    def crear_identidad_visual(self):
        frame = tk.Frame(self.root, bg=C["bg"])
        frame.pack(pady=10)
        tk.Label(frame, text="2\n6", fg=C["green"], bg=C["bg"],
                 font=("Arial Black", 44), justify="center").pack()
        tk.Label(frame, text="FIFA WORLD CUP", fg=C["fg"], bg=C["bg"],
                 font=("Arial", 9, "bold")).pack()

    # ── MENU ────────────────────────────────────

    def _estilo_boton(self, **kw):
        base = {"fg": C["fg"], "bg": C["gray"],
                "activebackground": C["cyan"], "activeforeground": "#000000",
                "font": ("Arial", 11, "bold"), "width": 32, "bd": 0,
                "cursor": "hand2", "pady": 8}
        base.update(kw)
        return base

    def crear_menu_principal(self):
        frame = tk.Frame(self.root, bg=C["bg"])
        frame.pack(pady=15)

        tk.Label(frame, text="MENÚ PRINCIPAL", fg=C["fg"], bg=C["bg"],
                 font=("Arial", 12, "bold")).pack(pady=(0, 15))

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
                kw = {"bg": C["disabled"], "fg": "#888888", "state": "disabled"}
            elif extra == "red_hover":
                kw = {"activebackground": "#FF3333"}
            btn = tk.Button(frame, text=text, command=cmd, **self._estilo_boton(**kw))
            btn.pack(pady=6)
            self.menu_buttons[text] = btn

    # ── CONFIGURACIÓN ────────────────────────────

    def abrir_configuracion(self):
        win = tk.Toplevel(self.root)
        win.title("Configuración del Torneo")
        win.geometry("420x300")
        win.configure(bg=C["bg"])
        win.transient(self.root)
        win.grab_set()

        card = tk.Frame(win, bg=C["card"], padx=20, pady=20)
        card.pack(pady=20, padx=20, fill="both", expand=True)

        tk.Label(card, text="CONFIGURACIÓN DEL TORNEO", fg=C["cyan"], bg=C["card"],
                 font=("Arial", 12, "bold")).pack(pady=(0, 15))

        def campo(parent, label):
            tk.Label(parent, text=label, fg=C["fg"], bg=C["card"],
                     font=("Arial", 10)).pack(anchor="w")
            e = tk.Entry(parent, bg=C["input_bg"], fg="white",
                         insertbackground="white", relief="flat", font=("Arial", 10))
            e.pack(fill="x", pady=(2, 5))
            return e

        e_nombre = campo(card, "Nombre del torneo")
        e_inicio = campo(card, "Fecha inicio (DD/MM/AAAA)")
        e_fin = campo(card, "Fecha fin (DD/MM/AAAA)")

        def guardar():
            nombre = e_nombre.get().strip()
            inicio = e_inicio.get().strip()
            fin = e_fin.get().strip()
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
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Guardar y Asignar Grupos",
                  command=guardar, **self._estilo_boton(width=28)).pack()

    # ── ASIGNACIÓN DE GRUPOS ──────────────────────

    def abrir_asignacion_grupos(self):
        win = tk.Toplevel(self.root)
        win.title("Asignación de Equipos a Grupos")
        win.geometry("730x560")
        win.configure(bg=C["bg"])
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="ASIGNACIÓN DE EQUIPOS A GRUPOS", fg=C["cyan"], bg=C["bg"],
                 font=("Arial", 12, "bold")).pack(pady=(15, 2))
        tk.Label(win, text="Seleccioná un país disponible y agregalo a un grupo (4 por grupo)",
                 fg=C["green"], bg=C["bg"], font=("Arial", 9)).pack(pady=(0, 8))

        main = tk.Frame(win, bg=C["bg"])
        main.pack(fill="both", expand=True, padx=15, pady=5)

        # ── Left: available pool ─────────────────
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

        # ── Right: group assignment ──────────────
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
        tk.Button(btn_row, text="→ Agregar", command=self._agregar,
                  **self._estilo_boton(width=13, bg=C["cyan"], fg="#000000")).pack(side="left", padx=3)
        tk.Button(btn_row, text="Quitar ←", command=self._quitar,
                  **self._estilo_boton(width=13)).pack(side="right", padx=3)

        self._refrescar_asig()

        # ── Footer ──────────────────────────────
        self.lbl_status = tk.Label(win, text="", fg=C["green"], bg=C["bg"], font=("Consolas", 9))
        self.lbl_status.pack(pady=(0, 5))
        self._actualizar_status()

        tk.Button(win, text="FINALIZAR CONFIGURACIÓN",
                  command=lambda: self._finalizar(win),
                  bg=C["cyan"], fg="#000000",
                  **{k: v for k, v in self._estilo_boton(width=30).items()
                     if k not in ("bg", "fg")}).pack(pady=8)

    def _refrescar_disp(self):
        self.lbox_disp.delete(0, "end")
        for p in sorted(self.disponibles):
            self.lbox_disp.insert("end", p)

    def _refrescar_asig(self, event=None):
        self.lbox_asig.delete(0, "end")
        grupo = self.cb_grupo.get()
        for i, p in enumerate(self.asignaciones.get(grupo, []), 1):
            self.lbox_asig.insert("end", f"{i}. {p}")

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

    def _actualizar_status(self):
        total = sum(len(v) for v in self.asignaciones.values())
        self.lbl_status.config(text=f"Asignados: {total}/48  |  Pendientes: {len(self.disponibles)}")

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
                data_store.tablagral[nom] = Equipo(
                    nombre=nom, abreviatura=abrev, prefijo="",
                    grupo=g, id_identificador=f"{g}{i}"
                )

        for g, eqs in self.asignaciones.items():
            for e1, e2 in generar_pares_grupo(eqs):
                data_store.tablagral[e1].partidos.append(
                    {"rival": e2, "fecha": "", "hora": "", "goles": None})
                data_store.tablagral[e2].partidos.append(
                    {"rival": e1, "fecha": "", "hora": "", "goles": None})

        self.torneo_configurado = True
        self.menu_buttons["2. Registro de Resultados"].config(
            state="normal", bg=C["gray"], fg=C["fg"])
        messagebox.showinfo(
            "Éxito",
            f"Torneo '{data_store.nombre_torneo}' configurado.\n48 equipos en 12 grupos, partidos generados.",
            parent=win)
        win.destroy()

    # ── REGISTRO DE RESULTADOS ─────────────────────

    def abrir_resultados(self):
        if not self.torneo_configurado:
            messagebox.showwarning("Acceso Denegado",
                                   "Primero completá la Configuración del Torneo.")
            return

        win = tk.Toplevel(self.root)
        win.title("Registro de Resultados")
        win.geometry("720x500")
        win.configure(bg=C["bg"])
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="REGISTRO DE RESULTADOS", fg=C["cyan"], bg=C["bg"],
                 font=("Arial", 12, "bold")).pack(pady=(15, 2))
        tk.Label(win, text="Seleccioná un grupo y cargá los goles de cada partido",
                 fg=C["green"], bg=C["bg"], font=("Arial", 9)).pack(pady=(0, 10))

        top = tk.Frame(win, bg=C["bg"])
        top.pack(fill="x", padx=20)
        tk.Label(top, text="Grupo:", fg=C["fg"], bg=C["bg"],
                 font=("Arial", 10, "bold")).pack(side="left", padx=(0, 10))
        cb = ttk.Combobox(top, values=list("ABCDEFGHIJKL"),
                           state="readonly", width=4, font=("Arial", 10))
        cb.pack(side="left")

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
        editando = {}  # {(e1, e2): bool} — tracked separately

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
                    pair = tuple(sorted([e.nombre, p["rival"]]))
                    if pair in mostrados:
                        continue
                    mostrados.add(pair)
                    editando[pair] = False

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

                    match_widgets[pair] = (e_loc, e_vis, e.nombre, p["rival"])

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
                messagebox.showinfo("Guardado", "Resultados guardados correctamente.", parent=win)

        tk.Button(win, text="Guardar Resultados",
                  command=guardar_res,
                  bg=C["cyan"], fg="#000000",
                  **{k: v for k, v in self._estilo_boton(width=20).items()
                     if k not in ("bg", "fg")}).pack(pady=10)

    def _asignar_tarjetas_gui(self, local, visit):
        win = tk.Toplevel(self.root)
        win.title("Tarjetas")
        win.geometry("420x300")
        win.configure(bg=C["bg"])
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="ASIGNAR TARJETAS", fg=C["cyan"], bg=C["bg"],
                 font=("Arial", 11, "bold")).pack(pady=(10, 5))

        main = tk.Frame(win, bg=C["bg"], padx=15, pady=5)
        main.pack(fill="both", expand=True)

        lbl_feedback = tk.Label(main, text="", fg=C["green"], bg=C["bg"], font=("Arial", 9))
        lbl_feedback.pack(pady=3)

        def seccion(team_name):
            frame = tk.LabelFrame(main, text=team_name, fg=C["green"],
                                  bg=C["card"], font=("Arial", 10, "bold"),
                                  padx=8, pady=6)
            frame.pack(fill="x", pady=4)

            row = tk.Frame(frame, bg=C["card"])
            row.pack(fill="x")

            tk.Label(row, text="Jugador:", fg=C["fg"], bg=C["card"],
                     font=("Arial", 9)).pack(side="left")
            e_jug = tk.Entry(row, bg=C["input_bg"], fg="white",
                             insertbackground="white", relief="flat",
                             font=("Arial", 9), width=14)
            e_jug.pack(side="left", padx=4)

            tk.Label(row, text="Tipo:", fg=C["fg"], bg=C["card"],
                     font=("Arial", 9)).pack(side="left")
            cb_tipo = ttk.Combobox(row, values=["Amarilla", "Roja"],
                                    state="readonly", width=9, font=("Arial", 9))
            cb_tipo.pack(side="left", padx=4)
            cb_tipo.set("Amarilla")

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
                      font=("Arial", 9, "bold"), cursor="hand2", width=3).pack(side="left", padx=4)

        seccion(local)
        seccion(visit)

        tk.Button(win, text="Cerrar", command=win.destroy,
                  **self._estilo_boton(width=15)).pack(pady=8)

    # ── EMISIÓN DE INFORMES ────────────────────────

    def abrir_informes(self):
        win = tk.Toplevel(self.root)
        win.title("Emisión de Informes")
        win.geometry("720x500")
        win.configure(bg=C["bg"])
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="EMISIÓN DE INFORMES", fg=C["cyan"], bg=C["bg"],
                 font=("Arial", 12, "bold")).pack(pady=(15, 2))
        tk.Label(win, text="Seleccioná un grupo para ver la tabla de posiciones",
                 fg=C["green"], bg=C["bg"], font=("Arial", 9)).pack(pady=(0, 10))

        top = tk.Frame(win, bg=C["bg"])
        top.pack(fill="x", padx=20)
        tk.Label(top, text="Grupo:", fg=C["fg"], bg=C["bg"],
                 font=("Arial", 10, "bold")).pack(side="left", padx=(0, 10))
        cb = ttk.Combobox(top, values=list("ABCDEFGHIJKL"),
                           state="readonly", width=4, font=("Arial", 10))
        cb.pack(side="left")

        frame = tk.Frame(win, bg=C["bg"])
        frame.pack(fill="both", expand=True, padx=20, pady=15)

        cols = ("ID", "Equipo", "PJ", "PTS", "GF", "GC", "AM", "RJ")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=12)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=70, anchor="center")
        tree.column("Equipo", width=170, anchor="w")
        tree.column("ID", width=40)

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


if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazMundial(root)
    root.mainloop()
