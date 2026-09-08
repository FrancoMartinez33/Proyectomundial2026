# ─────────────────────────────────────────────────────────────
#  Música – Reproductor de playlist para el menú
#  Usa pygame-ce (importado como pygame); si no está instalado
#  o no hay canciones, la app sigue funcionando sin audio.
# ─────────────────────────────────────────────────────────────

from pathlib import Path
import random

EXTENSIONES = (".mp3", ".wav", ".ogg", ".flac", ".m4a", ".wma", ".opus")


class ReproductorMusica:
    """Administra la playlist de una carpeta y el audio con pygame."""

    def __init__(self, carpeta=None):
        self.carpeta = Path(carpeta) if carpeta else Path(__file__).parent.parent / "musica"
        self.pistas = []
        self.actual = -1
        self.reproduciendo = False
        self.pausado = False
        self._pygame = None
        self._init_pygame()

    def _init_pygame(self):
        try:
            import pygame
            if pygame.mixer.get_init() is None:
                # Buffer mayor: reduce los cuelgues/segfaults intermitentes de
                # SDL_mixer cuando corre junto al lazo de mensajes de tkinter.
                pygame.mixer.pre_init(44100, -16, 2, 1024)
                pygame.mixer.init()
            self._pygame = pygame
        except Exception as e:
            print(f"[musica] No se pudo iniciar el audio: {e}")

    @property
    def disponible(self):
        return self._pygame is not None

    def _refrescar_pistas(self):
        self.pistas = []
        if self.carpeta.exists():
            for ext in EXTENSIONES:
                self.pistas.extend(sorted(self.carpeta.glob(f"*{ext}")))
        return self.pistas

    def nombre_actual(self, idx=None):
        idx = self.actual if idx is None else idx
        if 0 <= idx < len(self.pistas):
            return self.pistas[idx].name
        return ""

    def reproducir(self, idx):
        """Reproduce la pista idx (cíclico). Devuelve True si lo logró."""
        if not self.disponible:
            return False
        self._refrescar_pistas()
        if not self.pistas:
            return False
        idx = idx % len(self.pistas)
        try:
            self._pygame.mixer.music.stop()
            self._pygame.mixer.music.load(str(self.pistas[idx]))
            self._pygame.mixer.music.play()
            self.actual = idx
            self.reproduciendo = True
            self.pausado = False
            return True
        except Exception as e:
            print(f"[musica] Error al reproducir {self.pistas[idx].name}: {e}")
            return False

    def reproducir_aleatoria(self):
        """Reproduce una pista al azar de la playlist. Devuelve True si lo logró."""
        self._refrescar_pistas()
        if not self.pistas:
            return False
        return self.reproducir(random.randrange(len(self.pistas)))

    def siguiente(self):
        if self.pistas:
            return self.reproducir(self.actual + 1)
        return False

    def anterior(self):
        if self.pistas:
            return self.reproducir(self.actual - 1)
        return False

    def reanudar(self):
        """Continúa la pista actual o arranca la primera si no hay ninguna."""
        if not self.disponible:
            return False
        if self.pausado:
            self._pygame.mixer.music.unpause()
            self.pausado = False
            self.reproduciendo = True
            return True
        if not self.pistas:
            self._refrescar_pistas()
        if self.pistas and not self._pygame.mixer.music.get_busy():
            return self.reproducir(self.actual if self.actual >= 0 else 0)
        return False

    def pausar(self):
        if not self.disponible:
            return
        if self._pygame.mixer.music.get_busy():
            self._pygame.mixer.music.pause()
            self.reproduciendo = False
            self.pausado = True

    def detener(self):
        if not self.disponible:
            return
        self._pygame.mixer.music.stop()
        self.reproduciendo = False
        self.pausado = False

    def set_volumen(self, valor):
        if not self.disponible:
            return
        try:
            self._pygame.mixer.music.set_volume(max(0.0, min(1.0, float(valor))))
        except Exception as e:
            print(f"[musica] Error de volumen: {e}")

    def terminada(self):
        """True si ya terminó la pista en reproducción."""
        if not self.disponible or not self.reproduciendo:
            return False
        try:
            return not self._pygame.mixer.music.get_busy()
        except Exception:
            return False