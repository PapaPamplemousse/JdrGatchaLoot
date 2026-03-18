# ui/panels.py
import tkinter as tk
from tkinter import messagebox
from tkinter import PhotoImage
import os 
import sys

class InputPanel(tk.Frame):
    def __init__(self, parent, on_launch_cb, on_jackpot_cb, on_multi_soul_cb, initial_fragments): 
        super().__init__(parent, bg="#333", padx=10, pady=10)
        self.on_launch = on_launch_cb
        self.on_jackpot = on_jackpot_cb
        self.on_multi_soul = on_multi_soul_cb
        self.entries = {}
        self.blink_job = None
        
        # --- L'ESPACE DU CROUPIER ---
        self.croupier_space = tk.Frame(self, bg="#333", height=200) 
        self.croupier_space.pack(fill=tk.X, pady=(0, 20)) 

        # Chemins des images
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        self.img_path = os.path.join(base_dir, "assets", "croupier.png")
        self.frag_path = os.path.join(base_dir, "assets", "soul_fragment.png")

        # Chargement du croupier
        try:
            self.croupier_img = tk.PhotoImage(file=self.img_path)
            self.lbl_croupier = tk.Label(self.croupier_space, image=self.croupier_img, bg="#333", bd=0)
            self.lbl_croupier.pack(expand=True)
        except tk.TclError:
            self.lbl_croupier = tk.Label(self.croupier_space, text="[ Croupier ]", bg="#222", fg="#777")
            self.lbl_croupier.pack(expand=True, fill=tk.BOTH)

        # --- NOUVEAU : SUPERPOSITION DES FRAGMENTS D'ÂME ---
        # On crée un petit cadre transparent qui va "flotter" sur le Croupier
        self.soul_overlay = tk.Frame(self.croupier_space, bg="#333")
        # On le place en haut à droite (relx=0.98 signifie 98% de la largeur)
        self.soul_overlay.place(relx=0.98, rely=0.05, anchor="ne")

        self.lbl_frag_value = tk.Label(self.soul_overlay, text=f"x{initial_fragments} ", fg="#9C27B0", bg="#333", font=("Arial", 16, "bold"))
        self.lbl_frag_value.pack(side=tk.LEFT)

        try:
            # .subsample(2, 2) divise la taille de l'image par 2. Met (3, 3) si encore trop gros !
            self.frag_img = tk.PhotoImage(file=self.frag_path).subsample(2, 2)
            self.lbl_frag_icon = tk.Label(self.soul_overlay, image=self.frag_img, bg="#333", bd=0)
            self.lbl_frag_icon.pack(side=tk.RIGHT)
        except tk.TclError:
            tk.Label(self.soul_overlay, text="[ÂME]", fg="#9C27B0", bg="#333").pack(side=tk.RIGHT)

        # --- LE RESTE DE L'INTERFACE ---
        tk.Label(self, text="♦ RÉSULTATS DU DÉ ♦", fg="white", bg="#333", font=("Arial", 14, "bold")).pack(pady=10)

        self.add_input("Résultat du D20:", "tier")

        self.btn_lancer = tk.Button(self, text="LANCER LE TIRAGE", bg="#FF5722", fg="white", font=("Arial", 12, "bold"), command=self.submit)
        self.btn_lancer.pack(pady=10, fill=tk.X)

        # --- CADRES SÉPARÉS POUR SÉCURISER L'AFFICHAGE ---
        self.jackpot_container = tk.Frame(self, bg="#333")
        self.jackpot_container.pack(fill=tk.X)
        
        self.multi_container = tk.Frame(self, bg="#333")
        self.multi_container.pack(fill=tk.X)

        # BOUTON JACKPOT (Toujours affiché, mais grisé par défaut)
        self.btn_jackpot = tk.Button(self.jackpot_container, text="★★★ JACKPOT ★★★", font=("Impact", 16, "bold"), relief=tk.RAISED, borderwidth=5, command=self.trigger_jackpot)
        self.btn_jackpot.pack(pady=5, fill=tk.X)
        self.btn_jackpot.config(state=tk.DISABLED, bg="#555", fg="#888") 
        
        # BOUTONS MULTI (Toujours affichés, couleurs gérées dynamiquement)
        self.btn_multi_x5 = tk.Button(self.multi_container, text="♦ TIRAGE MULTI x5 ♦", font=("Arial", 12, "bold"), command=lambda: self.trigger_multi_soul(5))
        self.btn_multi_x5.pack(pady=5, fill=tk.X)

        self.btn_multi_x10 = tk.Button(self.multi_container, text="♦ TIRAGE x10 (Rare Garanti) ♦", font=("Arial", 12, "bold"), borderwidth=3, relief=tk.RIDGE, command=lambda: self.trigger_multi_soul(10))
        self.btn_multi_x10.pack(pady=5, fill=tk.X)

        # Initialisation
        self.update_soul_fragments(initial_fragments)
        self.entries["tier"].bind("<Return>", lambda event: self.submit())
        self.entries["tier"].focus()

    def add_input(self, label_text, key):
        frame = tk.Frame(self, bg="#333")
        frame.pack(fill=tk.X, pady=5)
        tk.Label(frame, text=label_text, fg="#CCC", bg="#333", width=18, anchor="w").pack(side=tk.LEFT)
        entry = tk.Entry(frame, bg="#222", fg="white", insertbackground="white")
        entry.pack(side=tk.RIGHT, expand=True, fill=tk.X)
        self.entries[key] = entry

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

        self.btn_lancer.config(state=tk.DISABLED)
        self.on_launch({"tier": tier_val})

    def reset_inputs(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.btn_lancer.config(state=tk.NORMAL)
        if "tier" in self.entries:
            self.entries["tier"].focus()

    # --- LOGIQUE DU JACKPOT ---
    def show_jackpot(self):
        # On l'active et on lui donne ses vraies couleurs
        self.btn_jackpot.config(state=tk.NORMAL, bg="gold", fg="red")
        self._blink_jackpot()

    def hide_jackpot(self):
        if self.blink_job is not None:
            self.after_cancel(self.blink_job)
            self.blink_job = None
        # On le grise et on le désactive au lieu de le cacher
        self.btn_jackpot.config(state=tk.DISABLED, bg="#555", fg="#888")

    def trigger_jackpot(self):
        self.hide_jackpot()
        self.on_jackpot()

    def _blink_jackpot(self):
        # Sécurité : si le bouton a été grisé entre temps, on arrête le clignotement
        if self.btn_jackpot['state'] == tk.DISABLED:
            return 
            
        current_bg = self.btn_jackpot.cget("background")
        new_bg = "white" if current_bg == "gold" else "gold"
        self.btn_jackpot.config(background=new_bg)
        self.blink_job = self.after(300, self._blink_jackpot)

    # --- LOGIQUE DES FRAGMENTS ET MULTI ---
    def update_soul_fragments(self, fragment_count):
        self.lbl_frag_value.config(text=f"x{fragment_count} ")
        
        # Gestion du Tirage x5
        if fragment_count >= 5:
            self.btn_multi_x5.config(state=tk.NORMAL, bg="#9C27B0", fg="white")
        else:
            self.btn_multi_x5.config(state=tk.DISABLED, bg="#555", fg="#888")

        # Gestion du Tirage x10
        if fragment_count >= 10:
            self.btn_multi_x10.config(state=tk.NORMAL, bg="#6A1B9A", fg="gold")
        else:
            self.btn_multi_x10.config(state=tk.DISABLED, bg="#555", fg="#888")

    def trigger_multi_soul(self, count):
        self.on_multi_soul(count)

class ResultPanel(tk.Frame):
    # Reste exactement comme avant
    def __init__(self, parent):
        super().__init__(parent, bg="#1E1E1E", padx=10, pady=10)
        self.text_area = tk.Text(self, bg="#1E1E1E", fg="#00FF00", font=("Consolas", 11), state=tk.DISABLED, wrap=tk.WORD)
        self.text_area.pack(expand=True, fill=tk.BOTH)

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
        """Affichage condensé spécialement conçu pour les multi-tirages (façon Gacha)."""
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
            
            # Condense les stats sur une ligne
            stats_str = ", ".join([f"{k}: {v}" for k, v in item.stats.items()])
            if not stats_str: stats_str = "Aucune stat"
            
            output += f"    -> {item.item_type} | Val: ¤ {item.get_price_string()} | Stats: {stats_str}\n"
            
            # Affiche juste le premier effet s'il y en a un pour ne pas surcharger
            if item.effects:
                first_effect = item.effects[0].split('\n')[0] # Prend juste le titre de l'effet
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