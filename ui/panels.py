# ui/panels.py
import tkinter as tk
from tkinter import messagebox
import os 

class InputPanel(tk.Frame):
    def __init__(self, parent, on_launch_cb, on_jackpot_cb): # Ajout du callback jackpot
        super().__init__(parent, bg="#333", padx=10, pady=10)
        self.on_launch = on_launch_cb
        self.on_jackpot = on_jackpot_cb
        self.entries = {}
        self.blink_job = None # Pour gérer l'animation de clignotement
        
        self.croupier_space = tk.Frame(self, bg="#333", height=200) 
        self.croupier_space.pack(fill=tk.X, pady=(0, 20)) 

        # --- CHARGEMENT DE L'IMAGE FIXE (PNG) ---
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.img_path = os.path.join(base_dir, "assets", "croupier.png")

        try:
            self.croupier_img = tk.PhotoImage(file=self.img_path)
            self.lbl_croupier = tk.Label(self.croupier_space, image=self.croupier_img, bg="#333")
            self.lbl_croupier.pack(expand=True)
        except tk.TclError:
            self.lbl_croupier = tk.Label(self.croupier_space, text="[ Placez 'croupier.png'\ndans le dossier 'assets' ]", bg="#222", fg="#777")
            self.lbl_croupier.pack(expand=True, fill=tk.BOTH)

        # --- LE RESTE DE L'INTERFACE ---
        tk.Label(self, text="♦ RÉSULTATS DU DÉ ♦", fg="white", bg="#333", font=("Arial", 14, "bold")).pack(pady=10)

        self.add_input("Résultat du D20:", "tier")

        self.btn_lancer = tk.Button(self, text="LANCER LE TIRAGE", bg="#FF5722", fg="white", font=("Arial", 12, "bold"), command=self.submit)
        self.btn_lancer.pack(pady=10, fill=tk.X)

        # --- NOUVEAU : BOUTON JACKPOT ---
        # Il est masqué par défaut (pack_forget)
        self.btn_jackpot = tk.Button(self, text="★★★ JACKPOT ★★★", bg="gold", fg="red", font=("Impact", 18, "bold"), relief=tk.RAISED, borderwidth=5, command=self.trigger_jackpot)
        # On ne le pack pas tout de suite.

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
        self.hide_jackpot() # Cache le jackpot au nouveau lancer
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
        """Affiche le bouton Jackpot et commence le clignotement."""
        self.btn_jackpot.pack(pady=10, fill=tk.X)
        self._blink_jackpot()

    def hide_jackpot(self):
        """Cache le bouton Jackpot et arrête le clignotement."""
        if self.blink_job is not None:
            self.after_cancel(self.blink_job)
            self.blink_job = None
        self.btn_jackpot.pack_forget()

    def trigger_jackpot(self):
        """Action quand on clique sur le bouton Jackpot."""
        self.hide_jackpot()
        self.on_jackpot() # Appelle la fonction dans app.py

    def _blink_jackpot(self):
        """Alterne les couleurs du bouton."""
        current_bg = self.btn_jackpot.cget("background")
        new_bg = "white" if current_bg == "gold" else "gold"
        self.btn_jackpot.config(background=new_bg)
        # Re-planifie le clignotement toutes les 300ms
        self.blink_job = self.after(300, self._blink_jackpot)

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
                sign = "+" if val > 0 else ""
                output += f"  {stat}: {sign}{val}\n"
        
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

    def append_text(self, text):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, text + "\n")
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)
        
    def clear(self):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.text_area.config(state=tk.DISABLED)