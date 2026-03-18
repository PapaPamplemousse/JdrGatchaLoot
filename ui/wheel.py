import tkinter as tk
import math
from core.generator import TIERS

class CasinoWheel(tk.Canvas):
    def __init__(self, parent, size=300, **kwargs):
        super().__init__(parent, width=size, height=size, bg="#2b2b2b", highlightthickness=0, **kwargs)
        self.size = size
        self.center = size / 2
        self.radius = size / 2 - 20
        self.segments = []
        self.current_rotation = 0
        
        self.colors = {
            "Common": "#A0A0A0",     # Gris
            "Uncommon": "#4CAF50",   # Vert
            "Rare": "#2196F3",       # Bleu
            "Very Rare": "#9C27B0",  # Violet
            "Legendary": "#FFC107"   # Or
        }
        self._build_wheel()

    def _build_wheel(self):
        total_weight = sum((t["max"] - t["min"] + 1) for t in TIERS)
        start_angle = 0
        
        for tier in TIERS:
            weight = tier["max"] - tier["min"] + 1
            extent = (weight / total_weight) * 360
            color = self.colors.get(tier["name"], "#FFF")
            
            # Création de l'arc
            arc_id = self.create_arc(
                20, 20, self.size-20, self.size-20,
                start=start_angle, extent=extent,
                fill=color, outline="#111", width=2
            )
            self.segments.append({
                "id": arc_id, "name": tier["name"],
                "base_start": start_angle, "extent": extent
            })
            start_angle += extent
            
        # Pointeur (triangle en haut)
        self.create_polygon(
            self.center - 15, 20,
            self.center + 15, 20,
            self.center, 50,  # Plus long
            fill="red", outline="white"
        )

    def spin_to_tier(self, target_tier_name, callback):
        """Anime la roue et s'arrête sur le tier ciblé de façon rapide."""
        target_segment = next((s for s in self.segments if s["name"] == target_tier_name), None)
        if not target_segment:
            callback()
            return

        target_angle_local = target_segment["base_start"] + (target_segment["extent"] / 2)
        target_rotation = (90 - target_angle_local) % 360
        
        # CHANGEMENT 1 : On passe de 1080 (3 tours) à 360 (1 seul tour bonus)
        #total_rotation_needed = 360 + target_rotation - self.current_rotation
        # Le compromis parfait : 2 tours complets (720 degrés)
        total_rotation_needed = 1080 + target_rotation - self.current_rotation

        # CHANGEMENT 2 : On augmente la vitesse initiale de 25 à 45
        self._animate_spin(total_rotation_needed, 45, callback)

    def _animate_spin(self, degrees_left, speed, callback):
        if degrees_left <= 0:
            callback() 
            return

        actual_step = min(speed, degrees_left)
        self.current_rotation = (self.current_rotation + actual_step) % 360
        
        for seg in self.segments:
            new_start = (seg["base_start"] + self.current_rotation) % 360
            self.itemconfig(seg["id"], start=new_start)

        # CHANGEMENT 3 : On freine plus fort (0.90 au lieu de 0.96)
        #new_speed = max(2, speed * 0.90) 
        new_speed = max(1.5, speed * 0.94) 
        # CHANGEMENT 4 : On réduit le délai de rafraîchissement (15ms au lieu de 20ms)
        self.after(15, self._animate_spin, degrees_left - actual_step, new_speed, callback)