# ui/panels.py
import tkinter as tk
from tkinter import messagebox
import os
import sys
from core.audio import audio_player

# --- COULEUR DU TAPIS DE CASINO ---
CASINO_DARK = "#003300"


class InputPanel(tk.Frame):
    def __init__(self, parent, on_launch_cb, on_jackpot_cb, on_multi_soul_cb, initial_fragments, is_cursed=False): 
        self.bg_color = "#4a0000" if is_cursed else "#004d00" 
        self.dark_color = "#2a0000" if is_cursed else "#003300"
        
        super().__init__(parent, bg=self.bg_color, padx=10, pady=10)
        self.on_launch = on_launch_cb
        self.on_jackpot = on_jackpot_cb
        self.on_multi_soul = on_multi_soul_cb
        self.entries = {}
        self.blink_job = None
        
        # --- L'ESPACE DU CROUPIER ---
        self.multi_container = tk.Frame(self, bg=self.bg_color)
        self.multi_container.pack(side=tk.BOTTOM, fill=tk.X)

        self.jackpot_container = tk.Frame(self, bg=self.bg_color)
        self.jackpot_container.pack(side=tk.BOTTOM, fill=tk.X)

        self.btn_lancer = tk.Button(self, text="LANCER LE TIRAGE", bg="#FF5722", fg="white", font=("Arial", 12, "bold"), command=self.submit)
        self.btn_lancer.pack(side=tk.BOTTOM, pady=10, fill=tk.X)

        self.input_frame = tk.Frame(self, bg=self.bg_color)
        self.input_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        tk.Label(self.input_frame, text="Résultat du D20:", fg="#CCC", bg=self.bg_color, width=18, anchor="w").pack(side=tk.LEFT)
        self.entries["tier"] = tk.Entry(self.input_frame, bg=self.dark_color, fg="white", insertbackground="white")
        self.entries["tier"].pack(side=tk.RIGHT, expand=True, fill=tk.X)

        tk.Label(self, text="♦ RÉSULTATS DU DÉ ♦", fg="white", bg=self.bg_color, font=("Arial", 14, "bold")).pack(side=tk.BOTTOM, pady=10)

        self.croupier_space = tk.Frame(self, bg=self.bg_color) 
        self.croupier_space.pack(side=tk.TOP, fill=tk.BOTH, expand=True) 

        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        self.img_path = os.path.join(base_dir, "assets", "croupier.png")
        self.frag_path = os.path.join(base_dir, "assets", "soul_fragment.png")

        try:
            self.croupier_img = tk.PhotoImage(file=self.img_path).subsample(2, 2)
            self.lbl_croupier = tk.Label(self.croupier_space, image=self.croupier_img, bg=self.bg_color, bd=0)
            self.lbl_croupier.pack(expand=True)
        except tk.TclError:
            self.lbl_croupier = tk.Label(self.croupier_space, text="[ Croupier ]", bg=self.dark_color, fg="#777")
            self.lbl_croupier.pack(expand=True, fill=tk.BOTH)

        self.soul_overlay = tk.Frame(self.croupier_space, bg=self.bg_color)
        self.soul_overlay.place(relx=0.98, rely=0.05, anchor="ne")

        self.lbl_frag_value = tk.Label(self.soul_overlay, text=f"x{initial_fragments} ", fg="#E040FB", bg=self.bg_color, font=("Arial", 16, "bold"))
        self.lbl_frag_value.pack(side=tk.LEFT)

        try:
            self.frag_img = tk.PhotoImage(file=self.frag_path).subsample(3, 3) 
            self.lbl_frag_icon = tk.Label(self.soul_overlay, image=self.frag_img, bg=self.bg_color, bd=0)
            self.lbl_frag_icon.pack(side=tk.RIGHT)
        except tk.TclError:
            tk.Label(self.soul_overlay, text="[ÂME]", fg="#E040FB", bg=self.bg_color).pack(side=tk.RIGHT)

        self.btn_jackpot = tk.Button(self.jackpot_container, text="★★★ JACKPOT ★★★", font=("Impact", 16, "bold"), relief=tk.RAISED, borderwidth=5, command=self.trigger_jackpot)
        self.btn_jackpot.pack(pady=5, fill=tk.X)
        self.btn_jackpot.config(state=tk.DISABLED, bg=self.dark_color, fg="#666") 
        
        self.btn_multi_x5 = tk.Button(self.multi_container, text="♦ TIRAGE MULTI x5 ♦", font=("Arial", 12, "bold"), command=lambda: self.trigger_multi_soul(5))
        self.btn_multi_x5.pack(side=tk.TOP, pady=5, fill=tk.X)

        self.btn_multi_x10 = tk.Button(self.multi_container, text="♦ TIRAGE x10 (Rare Garanti) ♦", font=("Arial", 12, "bold"), borderwidth=3, relief=tk.RIDGE, command=lambda: self.trigger_multi_soul(10))
        self.btn_multi_x10.pack(side=tk.TOP, pady=5, fill=tk.X)

        self.update_soul_fragments(initial_fragments)
        self.entries["tier"].bind("<Return>", lambda event: self.submit())
        self.entries["tier"].focus()

    def submit(self):
        self.hide_jackpot()
        try:
            tier_val = int(self.entries["tier"].get() or 0)
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer un nombre valide.")
            return

        if not (1 <= tier_val <= 20):
            messagebox.showerror("Erreur", "Le jet doit être compris entre 1 et 20.")
            return
        audio_player.play("spin")
        self.btn_lancer.config(state=tk.DISABLED)
        self.on_launch({"tier": tier_val})

    def reset_inputs(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.btn_lancer.config(state=tk.NORMAL)
        if "tier" in self.entries:
            self.entries["tier"].focus()

    def show_jackpot(self):
        self.btn_jackpot.config(state=tk.NORMAL, bg="gold", fg="red")
        self._blink_jackpot()

    def hide_jackpot(self):
        if self.blink_job is not None:
            self.after_cancel(self.blink_job)
            self.blink_job = None
        self.btn_jackpot.config(state=tk.DISABLED, bg=CASINO_DARK, fg="#666")

    def trigger_jackpot(self):
        self.hide_jackpot()
        self.on_jackpot()

    def _blink_jackpot(self):
        if self.btn_jackpot['state'] == tk.DISABLED: return 
        current_bg = self.btn_jackpot.cget("background")
        new_bg = "white" if current_bg == "gold" else "gold"
        self.btn_jackpot.config(background=new_bg)
        self.blink_job = self.after(300, self._blink_jackpot)

    def update_soul_fragments(self, fragment_count):
        self.lbl_frag_value.config(text=f"x{fragment_count} ")
        if fragment_count >= 5:
            self.btn_multi_x5.config(state=tk.NORMAL, bg="#9C27B0", fg="white")
        else:
            self.btn_multi_x5.config(state=tk.DISABLED, bg=CASINO_DARK, fg="#666")

        if fragment_count >= 10:
            self.btn_multi_x10.config(state=tk.NORMAL, bg="#6A1B9A", fg="gold")
        else:
            self.btn_multi_x10.config(state=tk.DISABLED, bg=CASINO_DARK, fg="#666")

    def trigger_multi_soul(self, count):
        self.on_multi_soul(count)


class ResultPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#1E1E1E", padx=10, pady=10)
        
        # --- NOUVEAU : LE BANDEAU DE RARETÉ (BIG WIN) ---
        self.banner_lbl = tk.Label(self, text="♦ FAITES VOS JEUX... ♦", bg="#111", fg="#FFF", font=("Impact", 20, "bold"), pady=5)
        self.banner_lbl.pack(fill=tk.X, pady=(0, 10))
        self.banner_blink_job = None

        self.text_area = tk.Text(self, bg="#1E1E1E", fg="#00FF00", font=("Consolas", 11), state=tk.DISABLED, wrap=tk.WORD)
        self.text_area.pack(expand=True, fill=tk.BOTH)


    def set_banner(self, tier_name, is_multi=False):
        """Met à jour le bandeau supérieur. Adapte le texte si c'est un multi-tirage."""
        if self.banner_blink_job:
            self.after_cancel(self.banner_blink_job)
            self.banner_blink_job = None

        colors = {
            "Vide": {"bg": "#000000", "fg": "#FF0000", "text": "☠ PERDU ☠"},
            "Common": {"bg": "#555555", "fg": "#FFFFFF", "text": "BUTIN COMMUN"},
            "Uncommon": {"bg": "#1B5E20", "fg": "#FFFFFF", "text": "BUTIN PEU COMMUN"},
            "Rare": {"bg": "#0D47A1", "fg": "#FFFFFF", "text": "★ RARE ★"},
            "Very Rare": {"bg": "#4A148C", "fg": "#FFFFFF", "text": "★★ TRÈS RARE ★★"},
            "Legendary": {"bg": "#FFD700", "fg": "#FF0000", "text": "★★★ LÉGENDAIRE !!! ★★★"}
        }

        cfg = colors.get(tier_name, {"bg": "#111", "fg": "#FFF", "text": "♦ FAITES VOS JEUX... ♦"})
        
        final_text = cfg["text"]
        if is_multi:
            if tier_name == "Vide":
                final_text = "☠ MULTI-POUSSIÈRE (TRAGÉDIE)... ☠"
            else:
                final_text = f"♦ MULTI-TIRAGE : TOP {final_text} ♦"

        self.banner_lbl.config(bg=cfg["bg"], fg=cfg["fg"], text=final_text)

        if tier_name == "Legendary":
            self._blink_banner_legendary()

        if tier_name in ["Very Rare", "Legendary"]:
            audio_player.play("jackpot")
        elif tier_name == "Vide":
            audio_player.play("loose")
        else:
            audio_player.play("win")

    def _blink_banner_legendary(self):
        """Fait clignoter le bandeau légendaire frénétiquement."""
        current_bg = self.banner_lbl.cget("bg")
        new_bg = "#FF0000" if current_bg == "#FFD700" else "#FFD700"
        new_fg = "#FFD700" if current_bg == "#FFD700" else "#FFFFFF"
        self.banner_lbl.config(bg=new_bg, fg=new_fg)
        self.banner_blink_job = self.after(150, self._blink_banner_legendary)

    # --- (Le reste des méthodes ResultPanel : display_item, display_multi_items, etc.) ---
    def display_item(self, item):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        output = f"===== LOOT GÉNÉRÉ =====\n"
        output += f"Nom    : {item.get_full_name()}\n"
        output += f"Tier   : {item.tier}\n"
        output += f"Type   : {item.item_type}\n"
        output += f"Valeur : ¤ {item.get_price_string()}\n\n"
        
        if item.stats:
            output += "Stats :\n"
            for stat, val in item.stats.items():
                if isinstance(val, (int, float)):
                    sign = "+" if val > 0 else ""
                    output += f"  {stat}: {sign}{val}\n"
                else:
                    output += f"  {stat}: {val}\n"
        
        if getattr(item, 'set_id', None):
            output += f"\n[+] Set : {item.set_name}\n"
            for pieces, bonus in item.set_bonuses.items():
                output += f"  [{pieces} pièces] -> {bonus}\n"

        if item.effects:
            output += "\nEffets :\n"
            for eff in item.effects:
                output += f"  - {eff}\n"
                
        output += f"\nDescription :\n{item.description}\n"
        output += "=======================\n"
        self.text_area.insert(tk.END, output)
        self.text_area.config(state=tk.DISABLED)

    def display_multi_items(self, items):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        output = f"===== RÉSULTAT DU MULTI-TIRAGE x{len(items)} =====\n\n"
        for i, item in enumerate(items, 1):
            if item.tier == "Vide":
                output += f"[{i}] ~ LE NÉANT ~\n    -> Rien que de la poussière.\n\n"
                continue
            tier_str = item.tier.upper()
            name_str = item.get_full_name()
            output += f"[{i}] [{tier_str}] {name_str}\n"
            stats_str = ", ".join([f"{k}: {v}" for k, v in item.stats.items()])
            if not stats_str: stats_str = "Aucune stat"
            output += f"    -> {item.item_type} | Val: ¤ {item.get_price_string()} | Stats: {stats_str}\n"
            if item.effects:
                first_effect = item.effects[0].split('\n')[0] 
                output += f"    -> Effet: {first_effect}\n"
            output += "\n"
        output += "========================================\n"
        self.text_area.insert(tk.END, output)
        self.text_area.config(state=tk.DISABLED)
        
    def append_text(self, text):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, text + "\n")
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)
        
    def clear(self):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.text_area.config(state=tk.DISABLED)
        self.set_banner("None") # Reset du bandeau