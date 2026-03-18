# ui/app.py
import tkinter as tk
from tkinter import messagebox
import os
import json
import random  
from datetime import datetime

from .wheel import CasinoWheel
from .panels import InputPanel, ResultPanel
from core import generator
from core.models import LootItem

class LootCasinoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Générateur de Loot Casino $$$")
        self.geometry("1000x700") # Fenêtre un peu plus grande pour accueillir la roue
        self.configure(bg="#222")
        
        self.current_items = []
        self.jackpot_history = []
        
        self.build_start_screen()

    def build_start_screen(self):
        self.clear_window()
        frame = tk.Frame(self, bg="#222")
        frame.pack(expand=True)
        
        tk.Label(frame, text="♦ LOOT CASINO ♦", font=("Arial", 32, "bold"), fg="#FFC107", bg="#222").pack(pady=20)
        tk.Button(frame, text="NOUVEAU TIRAGE", font=("Arial", 16, "bold"), bg="#4CAF50", fg="white", 
                  padx=20, pady=10, command=self.build_main_screen).pack()

    def build_main_screen(self):
        self.clear_window()
        self.current_items = []
        self.jackpot_history = []
        
        self.left_frame = tk.Frame(self, bg="#222")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.right_frame = tk.Frame(self, bg="#333", width=300)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # CHANGEMENT ICI : Roue plus grande (400 au lieu de 250)
        self.wheel = CasinoWheel(self.left_frame, size=400)
        self.wheel.pack(pady=10)
        
        self.result_panel = ResultPanel(self.left_frame)
        self.result_panel.pack(fill=tk.BOTH, expand=True)
        
        self.btn_finish = tk.Button(self.left_frame, text="$$$ TERMINER LE TIRAGE $$$", bg="#2196F3", fg="white", 
                                    font=("Arial", 10, "bold"), command=self.save_and_reset)
        self.btn_finish.pack(pady=5, fill=tk.X)

        self.input_panel = InputPanel(self.right_frame, self.handle_launch)
        self.input_panel.pack(fill=tk.BOTH, expand=True)

    def handle_launch(self, rolls):
        tier_data = generator.determine_tier(rolls["tier"])
        if not tier_data:
            messagebox.showerror("Erreur", "Tier roll invalide.")
            self.input_panel.btn_lancer.config(state=tk.NORMAL)
            return

        # On lance l'animation de la roue, puis on exécute la suite
        self.wheel.spin_to_tier(tier_data["name"], lambda: self.generate_and_display(tier_data))

    def generate_and_display(self, tier_data):
        # 1. GESTION DU COFFRE VIDE
        if tier_data["name"] == "Vide":
            self.result_panel.clear()
            
            # Tirage au sort : 70% de chance (1 à 70)
            if random.randint(1, 100) <= 70:
                # CAS DU MIMIC
                mimic_art = (
                    "      _____\n"
                    "     /     \\ \n"
                    "    | () () |\n"
                    "     \\  ^  /\n"
                    "      |||||\n\n"
                )
                self.result_panel.append_text("⚠ ATTENTION ! Ce n'est pas de la poussière... ⚠\n\n")
                self.result_panel.append_text(mimic_art)
                self.result_panel.append_text("Le coffre révèle des dents acérées et une langue violacée !\n")
                self.result_panel.append_text("C'EST UN MIMIC ! Il vous attaque ! ")
                # Ici, tu pourrais ajouter un appel à une fonction de combat : self.lancer_combat_mimic()
            else:
                # CAS VRAIMENT VIDE
                self.result_panel.append_text("\_(oo))_/¯ LE COFFRE EST VIDE...\n\n")
                self.result_panel.append_text("Il n'y a absolument rien ici à part de la poussière.")

            self.input_panel.btn_lancer.config(state=tk.NORMAL)
            return
            
        item = LootItem()
        item.tier = tier_data["name"]
        
        # # 2. AUTOMATISATION DES JETS GLOBAUX
        # type_roll = random.randint(1, 100)
        # base_roll = random.randint(1, 100)

        # 2. JETS DYNAMIQUES POUR LE TYPE D'OBJET
        min_type, max_type = generator.get_bounds(generator.ITEM_TYPES)
        type_roll = random.randint(min_type, max_type)


        type_data = generator.determine_item_type(type_roll)
        item.item_type = type_data["name"]
        
        if type_data["id"] == "scroll":
            min_scroll, max_scroll = generator.get_bounds(generator.SCROLLS.get("rarities", []))
            scroll_roll = random.randint(min_scroll, max_scroll)
            #scroll_roll = random.randint(1, 100)
            rar_data = generator.determine_scroll_rarity(scroll_roll)
            if rar_data:
                valid_spells = [s for s in generator.SCROLLS.get("spells", []) if s.get("rarity_id") == rar_data["id"]]
                if valid_spells:
                    spell_roll = random.randint(1, len(valid_spells))
                    spell_data = generator.determine_scroll_spell(rar_data["id"], spell_roll)
                    if spell_data:
                        item.base_name = f"Parchemin de {spell_data['name']} ({rar_data['name']})"
                        item.description = spell_data["description"]
        else :
            # Jet dynamique pour l'objet de base (en filtrant par type d'arme/armure d'abord)
            valid_bases = [b for b in generator.BASE_ITEMS if b.get("type_id") == type_data["id"]]
            min_base, max_base = generator.get_bounds(valid_bases)
            base_roll = random.randint(min_base, max_base)

            base_data = generator.determine_base_item(type_data["id"], base_roll)
            if base_data:
                item.base_name = base_data["name"]
                item.stats = base_data.get("base_stats", {}).copy()
                item.description = base_data.get("description", "")
                if "set_id" in base_data:
                    set_info = generator.get_set_info(base_data["set_id"])
                    if set_info:
                        item.set_id = base_data["set_id"]
                        item.set_name = set_info["name"]
                        item.set_bonuses = set_info["bonuses"]
                        
                num_affixes = tier_data.get("base_affixes", 0)
                if item.tier == "Common":
                    num_affixes = random.choice([0, 1])
                
                # Jets dynamiques pour les affixes
                min_affix, max_affix = generator.get_bounds(generator.AFFIXES)
                for _ in range(num_affixes):
                    #r = random.randint(1, 100)
                    r = random.randint(min_affix, max_affix)
                    affix = generator.determine_affix(r)
                    if affix:
                        item.affixes.append(affix)
                        item.merge_stats(affix.get("stats_modifier", {}))
                        if "effect" in affix: item.effects.append(affix["effect"])
                        if not item.prefix and "prefix" in affix:
                            item.prefix = affix["prefix"]
                        elif not item.suffix and "suffix" in affix:
                            item.suffix = affix["suffix"]

                if tier_data.get("has_unique_effect", False):
                    min_unique, max_unique = generator.get_bounds(generator.UNIQUE_EFFECTS)
                    unique_roll = random.randint(min_unique, max_unique)
                    unique_data = generator.get_unique_effect(unique_roll)
                    if unique_data:
                        item.effects.append(f"*** UNIQUE : {unique_data['name']} ***\n      {unique_data['description']}")
                        # On force un préfixe stylé pour que le nom de l'arme en jette
                        item.prefix = "Mythique"

        # 3. CALCUL DU PRIX (En pièces de cuivre : PC)
        # J'ai équilibré pour que ça fasse entre 0 et 100 PO environ selon la rareté
        base_value_pc = {
            "Common": random.randint(50, 5000),      # De 50 PC à 50 PA
            "Uncommon": random.randint(5000, 20000), # De 50 PA à 2 PO
            "Rare": random.randint(20000, 150000),   # De 2 PO à 15 PO
            "Very Rare": random.randint(150000, 450000), # De 15 PO à 45 PO
            "Legendary": random.randint(450000, 1000000) # De 45 PO à 100 PO
        }
        
        total_pc = base_value_pc.get(item.tier, 0)
        
        # Bonus de valeur : +15% par affixe présent sur l'arme
        bonus_multiplier = 1.0 + (0.15 * len(item.affixes))
        total_pc = int(total_pc * bonus_multiplier)
        
        item.set_price_from_copper(total_pc)

        # 4. AFFICHAGE ET JACKPOT
        self.current_items.append(item)
        self.result_panel.display_item(item)
        
        self.after(500, self.ask_jackpot)

    def ask_jackpot(self):
        # --- NOUVEAU : POPUP JACKPOT ---
        if messagebox.askyesno("Jackpot $$$", "VOULEZ-VOUS UTILISER LE JACKPOT ?\n\nAttention : Quitte ou double !"):
            jackpot_roll = random.randint(1, 100)
            self.process_jackpot(jackpot_roll)
        else:
            self.result_panel.append_text("\nTirage terminé. Terminez pour sauvegarder, ou modifiez vos jets pour un autre tirage.")
            self.input_panel.btn_lancer.config(state=tk.NORMAL)

    def process_jackpot(self, roll):
        self.jackpot_history.append(roll)
        self.result_panel.append_text(f"\[?] Lancement du Jackpot... ")
        # On fait tourner la roue pour le suspense, puis on applique
        self.wheel.spin_to_tier("Common", lambda: self._apply_jackpot_logic(roll)) 

    def _apply_jackpot_logic(self, roll):
        if 1 <= roll <= 50:
            self.current_items.clear()
            self.result_panel.append_text("X_X PERTE TOTALE : Le coffre se referme... tout a disparu.")
            self.input_panel.btn_lancer.config(state=tk.NORMAL)
            
        elif 51 <= roll <= 70:
            self.result_panel.append_text("--- RIEN : Le vent souffle, rien ne se passe.")
            self.after(1000, self.ask_jackpot) # On repropose le jackpot
            
        elif 71 <= roll <= 85:
            self.result_panel.append_text("[+] SECOND ITEM : Gagné ! (Remplissez les champs et relancez pour générer le 2nd item)")
            self.input_panel.btn_lancer.config(state=tk.NORMAL)
            
        elif 86 <= roll <= 95:
            self.result_panel.append_text("^^^ UPGRADE : L'item monte d'un Tier !")
            self.after(1000, self.ask_jackpot) # On repropose le jackpot
            
        elif roll >= 96:
            self.result_panel.append_text("*** JACKPOT ABSOLU ! L'item devient Légendaire !")
            self.after(1000, self.ask_jackpot) # On repropose le jackpot

    def save_and_reset(self):
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "log")
        os.makedirs(log_dir, exist_ok=True)
        
        files = [f for f in os.listdir(log_dir) if f.startswith("tirage_") and f.endswith(".json")]
        idx = len(files) + 1
        filename = f"tirage_{idx:03d}.json"
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "items": [i.to_dict() for i in self.current_items],
            "jackpot_history": self.jackpot_history
        }
        
        with open(os.path.join(log_dir, filename), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        messagebox.showinfo("Sauvegarde", f"Tirage sauvegardé dans {filename}")
        self.build_start_screen()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()