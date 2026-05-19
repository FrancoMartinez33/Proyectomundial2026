# ⚽ ProyecMundial 2026 — Sistema de Gestión del Mundial FIFA 2026

![Logo FIFA World Cup 2026](https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/2026_FIFA_World_Cup_emblem_%28horizontal%2C_with_wordmark%29.svg/800px-2026_FIFA_World_Cup_emblem_%28horizontal%2C_with_wordmark%29.svg.png)

> **Sistema completo para simular y gestionar la Copa Mundial de la FIFA 2026** — con 48 selecciones, 12 grupos, fase de grupos, octavos, cuartos, semifinales y final. Disponible con interfaz gráfica (Tkinter) y de línea de comandos.

---

## ✨ Funcionalidades

| Funcionalidad | Descripción |
|---|---|
| **Gestión de 48 selecciones** | Organiza los 12 grupos (A–L) con 4 equipos cada uno |
| **Tabla de posiciones** | Puntos, diferencia de gol, goles a favor y desempate por prefijo telefónico |
| **Registro de resultados** | Carga de marcadores, tarjetas amarillas/rojas |
| **Fixture y calendario** | Fixture completo con filtro por fecha |
| **Eliminación directa** | Octavos, cuartos, semis, final con bracket visual |
| **Mejores terceros** | Ranking de los 8 mejores terceros que avanzan |
| **Simulador aleatorio** | Generación automática de resultados |
| **Reportes exportables** | Exportación a `.txt` |
| **Doble interfaz** | GUI (Tkinter) y CLI |

---

## 🖥️ Capturas de la interfaz

### Interfaz Gráfica (Tkinter)

![Vista previa GUI](https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/2026_FIFA_World_Cup_emblem_%28horizontal%2C_with_wordmark%29.svg/600px-2026_FIFA_World_Cup_emblem_%28horizontal%2C_with_wordmark%29.svg.png)

*Ventana principal con tabla de grupos, registro de resultados y bracket de eliminación directa.*

### Interfaz de Línea de Comandos

```
===========================================
      MUNDIAL 2026 - SISTEMA DE GESTIÓN
===========================================
1. Ingresar resultados de la fase de grupos
2. Ver tabla de posiciones
3. Ver fixture
4. Simular resultados aleatorios
5. Ver eliminatorias
6. Generar reporte
7. Salir
===========================================
Seleccione una opción:
```

---

## 🏟️ Sedes del Mundial 2026

La Copa Mundial de la FIFA 2026 se disputará en **3 países anfitriones**:

| País | Sedes |
|---|---|
| 🇺🇸 **Estados Unidos** | 11 sedes (Nueva Jersey, Los Ángeles, Dallas, Houston, etc.) |
| 🇲🇽 **México** | 3 sedes (Ciudad de México, Guadalajara, Monterrey) |
| 🇨🇦 **Canadá** | 2 sedes (Toronto, Vancouver) |

*Fuente: [FIFA World Cup 2026](https://www.fifa.com/es/tournaments/mens/worldcup/canadamexicousa2026)*

---

## 🛠️ Tecnologías utilizadas

- **Python 3.12+**
- **Tkinter** — Interfaz gráfica de escritorio
- **Módulos internos:** `models`, `services`, `gui`, `cli`, `data_store`, `validators`

---

## 📁 Estructura del proyecto

```
mundial-2026/
├── src/
│   ├── __init__.py
│   ├── main.py              # Punto de entrada
│   ├── models.py            # Modelo Equipo
│   ├── data_store.py        # Estado global en memoria
│   ├── services.py          # Lógica de negocio
│   ├── gui.py               # Interfaz gráfica Tkinter
│   ├── cli.py               # Interfaz de consola
│   └── validators.py        # Validaciones de entrada
├── proyectoanashei.py       # Script legacy
├── interfaz mundial.py      # Script legacy
└── README.md
```

---

## 🚀 Cómo ejecutar

```bash
# Clonar el repositorio
git clone git@github.com:eyymaanu/proyecMundial2026.git
cd proyecMundial2026

# Ejecutar con interfaz gráfica (por defecto)
python src/main.py

# Ejecutar con interfaz de línea de comandos
python src/main.py --cli
```

---

## 📄 Licencia

Este proyecto es educativo y no está afiliado ni respaldado por la FIFA.
