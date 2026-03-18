# core/audio.py
import os
import sys
import pygame

class SoundManager:
    def __init__(self):
        self.enabled = False
        try:
            # Initialise le module audio
            pygame.mixer.init()
            self.enabled = True
        except Exception as e:
            print(f"Audio non disponible : {e}")

        # Détermination du chemin (Compatible PyInstaller)
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.assets_dir = os.path.join(base_dir, "assets")
        self.sounds = {}

        # On précharge les sons (ne plantera pas si les fichiers n'existent pas encore)
        self.load_sound("spin", "spin.mp3")       # Cléquetis de la roue
        self.load_sound("win", "win.wav")         # Petit butin
        self.load_sound("alarm", "alarm.wav")     # alarm erreur de roulette
        self.load_sound("jackpot", "jackpot.wav") # Alarme de Jackpot
        self.load_sound("loose", "loose.wav")     # Mimic ou Perte

    def load_sound(self, name, filename):
        """Charge un fichier son s'il existe dans le dossier assets."""
        if not self.enabled: return
        path = os.path.join(self.assets_dir, filename)
        if os.path.exists(path):
            try:
                self.sounds[name] = pygame.mixer.Sound(path)
            except Exception:
                pass

    def play(self, name):
        """Joue un son s'il a été chargé correctement."""
        if self.enabled and name in self.sounds:
            self.sounds[name].play()

# On crée une instance unique qui sera importée partout
audio_player = SoundManager()