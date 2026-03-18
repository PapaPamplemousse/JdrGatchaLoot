import tkinter as tk
import math
from core.generator import TIERS

class CasinoWheel(tk.Canvas):
    def __init__(self, parent, size=300, **kwargs):
        # Le fond #222 et highlightthickness=0 fusionnent la roue avec le fond !
        super().__init__(parent, width=size, height=size, bg="#222", highlightthickness=0, **kwargs)
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
        # --- 1. LA JANTE DORÉE (Contour extérieur) ---
        # On dessine un cercle légèrement plus grand que les parts de la roue
        self.create_oval(
            14, 14, self.size-14, self.size-14,
            fill="#111", outline="#FFD700", width=6
        )

        # --- 2. L'OMBRE DE LA ROUE ---
        self.create_oval(
            19, 19, self.size-19, self.size-19,
            fill="#000", outline="", width=0
        )

        total_weight = sum((t["max"] - t["min"] + 1) for t in TIERS)
        start_angle = 0
        
        for tier in TIERS:
            weight = tier["max"] - tier["min"] + 1
            extent = (weight / total_weight) * 360
            color = self.colors.get(tier["name"], "#FFF")
            
            # Création de l'arc (les parts)
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
            
        # --- 3. LE MOYEU CENTRAL (Le clou au milieu de la roue) ---
        self.create_oval(
            self.center - 15, self.center - 15,
            self.center + 15, self.center + 15,
            fill="#FFD700", outline="#111", width=2
        )
        self.create_oval(
            self.center - 5, self.center - 5,
            self.center + 5, self.center + 5,
            fill="#333", outline="", width=0
        )
            
        # --- 4. LE POINTEUR AMÉLIORÉ (Avec effet de relief) ---
        # A. L'ombre du pointeur (décalée de 2 pixels en bas à droite)
        self.create_polygon(
            self.center - 13, 17,
            self.center + 17, 17,
            self.center + 2, 52,
            fill="#000"
        )
        # B. Le vrai pointeur (Rouge avec contour Or)
        self.create_polygon(
            self.center - 15, 15,
            self.center + 15, 15,
            self.center, 50, 
            fill="#E53935", outline="#FFD700", width=2
        )
        # C. Le petit clou argenté sur le pointeur
        self.create_oval(
            self.center - 4, 18,
            self.center + 4, 26,
            fill="#E0E0E0", outline="#111", width=1
        )

    def spin_to_tier(self, target_tier_name, callback):
        """Anime la roue et s'arrête sur le tier ciblé de façon rapide."""
        target_segment = next((s for s in self.segments if s["name"] == target_tier_name), None)
        if not target_segment:
            callback()
            return

        target_angle_local = target_segment["base_start"] + (target_segment["extent"] / 2)
        target_rotation = (90 - target_angle_local) % 360
        
        # Le compromis parfait : 2 tours complets (720 degrés) + la rotation cible
        total_rotation_needed = 720 + target_rotation - self.current_rotation

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

        new_speed = max(1.5, speed * 0.94) 
        self.after(15, self._animate_spin, degrees_left - actual_step, new_speed, callback)