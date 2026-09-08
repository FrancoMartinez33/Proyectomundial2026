from pathlib import Path
import faulthandler
import sys
import traceback

from src.gui import InterfazMundial
import tkinter as tk

# Registro de crash: guarda en error.log cualquier excepción no controlada
# o falla nativa (segfault) para poder diagnosticar si la app se cierra sola.
_LOG = Path(__file__).with_name("error.log")


def _iniciar_log():
    try:
        flog = open(_LOG, "a")
        faulthandler.enable(flog)
    except Exception:
        pass

    def hook(exc_type, exc, tb):
        try:
            with open(_LOG, "a") as f:
                f.write("\n=== EXCEPCION NO CONTROLADA ===\n")
                traceback.print_exception(exc_type, exc, tb, file=f)
        except Exception:
            pass
        sys.__excepthook__(exc_type, exc, tb)

    sys.excepthook = hook


if __name__ == "__main__":
    _iniciar_log()
    root = tk.Tk()
    InterfazMundial(root)
    root.mainloop()