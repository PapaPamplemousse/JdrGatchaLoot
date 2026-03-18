# ui/app.py
import tkinter as tk
from tkinter import messagebox
import os
import json
import random  
from datetime import datetime
import sys
from .wheel import CasinoWheel
from .panels import InputPanel, ResultPanel
from core import generator
from core.models import LootItem

class LootCasinoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Générateur de Loot Casino $$$")
        # self.geometry("1000x700") # Fenêtre un peu plus grande pour accueillir la roue
        try:
            self.state('zoomed')
        except tk.TclError:
            self.attributes('-zoomed', True)
        
        self.configure(bg="#222")
        
        self.current_items = []
        self.jackpot_history = []

        # --- SYSTÈME DE PITY ---
        pity_cfg = generator.GACHA_DATA.get("pity", {})
        self.pity_counter = pity_cfg.get("current_pity", 0)
        self.pity_max = pity_cfg.get("max_pity", 5)
        self.pity_threshold = pity_cfg.get("max_roll_to_increment", 5)

        # --- SYSTÈME DE FRAGMENTS D'ÂME ---
        self.soul_fragments = generator.GACHA_DATA.get("soul_fragments", 0)
        self.frag_icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "soul_fragment.png")
        
        self.build_start_screen()

    def load_recent_history(self):
        """Récupère les objets des derniers tirages pour le bandeau défilant."""
        if getattr(sys, 'frozen', False):
            log_dir = os.path.join(os.path.dirname(sys.executable), "log")
        else:
            log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "log")
            
        if not os.path.exists(log_dir):
            return "♦ BIENVENUE A LA GRAND ROUE DU LOOT ! FAITES VOTRE PREMIER TIRAGE ! ♦"
            
        # Trie les fichiers du plus récent au plus ancien
        files = sorted([f for f in os.listdir(log_dir) if f.startswith("tirage_") and f.endswith(".json")], reverse=True)
        if not files:
            return "♦ BIENVENUE A LA GRAND ROUE DU LOOT ! FAITES VOTRE PREMIER TIRAGE ! ♦"
            
        recent_items = []
        for f in files[:5]: # On fouille dans les 5 derniers tirages
            try:
                with open(os.path.join(log_dir, f), "r", encoding="utf-8") as file:
                    data = json.load(file)
                    for item in data.get("items", []):
                        if item.get("tier") != "Vide" and item.get("name"):
                            recent_items.append(f"[{item.get('tier').upper()}] {item.get('name')}")
            except Exception:
                pass
                
        if not recent_items:
            return "♦ LA BANQUE EST PLEINE ! LANCEZ LES DÉS ! ♦"
            
        # On assemble tout avec des séparateurs et on le multiplie pour faire une très longue bande
        history_str = "   ✦   ".join(recent_items)
        return f"   ✦   {history_str}   ✦   " * 10

    # def build_start_screen(self):
    #     self.clear_window()
    #     frame = tk.Frame(self, bg="#222")
    #     frame.pack(expand=True)
        
    #     tk.Label(frame, text="♦ LOOT CASINO ♦", font=("Arial", 32, "bold"), fg="#FFC107", bg="#222").pack(pady=20)
    #     tk.Button(frame, text="NOUVEAU TIRAGE", font=("Arial", 16, "bold"), bg="#4CAF50", fg="white", 
    #               padx=20, pady=10, command=self.build_main_screen).pack()
    def build_start_screen(self):
        self.clear_window()
        
        # Un cadre principal très sombre pour faire ressortir les couleurs
        self.start_frame = tk.Frame(self, bg="#111")
        self.start_frame.pack(expand=True, fill=tk.BOTH)
        
        # --- 1. LE BANDEAU DÉFILANT (AÉROPORT / CASINO) ---
        # Fond vert sombre, bordure vert fluo
        self.marquee_canvas = tk.Canvas(self.start_frame, bg="#002200", height=60, highlightthickness=3, highlightbackground="#00FF00")
        self.marquee_canvas.pack(fill=tk.X, pady=(0, 40))
        
        history_text = self.load_recent_history()
        
        # Le texte écrit en Jaune fluo avec une police de type terminal
        self.marquee_text_id = self.marquee_canvas.create_text(
            1500, 32, text=history_text, 
            font=("Consolas", 18, "bold"), fill="#FFFF00", anchor="w"
        )
        self.marquee_x_pos = 1500 # Position de départ à l'extérieur de l'écran
        self._animate_marquee()

        # --- 2. TITRE CLIGNOTANT FAÇON NÉON ---
        self.title_label = tk.Label(self.start_frame, text="$$$ GRAND ROUE DU LOOT $$$", font=("Impact", 48, "bold"), bg="#111", fg="#FFD700")
        self.title_label.pack(pady=(40, 20))
        self._blink_title()

        # --- 3. GROS BOUTON D'ENTRÉE ---
        self.btn_play = tk.Button(self.start_frame, text=" ENTRER DANS LE CASINO ", font=("Arial", 22, "bold"), 
                                  bg="#E53935", fg="white", activebackground="#FFEB3B", activeforeground="red", 
                                  relief=tk.RAISED, bd=8, padx=40, pady=20, command=self.build_main_screen)
        self.btn_play.pack(pady=20)

    def build_main_screen(self):
        self.clear_window()
        self.current_items = []
        self.jackpot_history = []
        
        self.left_frame = tk.Frame(self, bg="#222")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.right_frame = tk.Frame(self, bg="#333", width=300)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # --- PARTIE GAUCHE ---
        self.wheel = CasinoWheel(self.left_frame, size=600)
        self.wheel.pack(pady=10)
        
        self.result_panel = ResultPanel(self.left_frame)
        self.result_panel.pack(fill=tk.BOTH, expand=True)

        # --- PARTIE DROITE ---
        self.btn_finish = tk.Button(self.right_frame, text="> TERMINER LE TIRAGE <", bg="#2196F3", fg="white", 
                                    font=("Arial", 12, "bold"), command=self.save_and_reset)
        self.btn_finish.pack(side=tk.BOTTOM, pady=20, padx=10, fill=tk.X)

        # --- NOUVEAU : LA JAUGE DE PITY ---
        self.pity_frame = tk.Frame(self.right_frame, bg="#333")
        self.pity_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 20))
        
        self.pity_label = tk.Label(self.pity_frame, text=f"PITIÉ : {self.pity_counter} / {self.pity_max}", bg="#333", fg="white", font=("Arial", 12, "bold"))
        self.pity_label.pack()
        
        # Jauge avec un fond gris sombre et une fine bordure pour bien la voir même vide
        self.pity_canvas = tk.Canvas(self.pity_frame, height=20, bg="#222", highlightthickness=1, highlightbackground="#555")
        self.pity_canvas.pack(fill=tk.X, pady=5)
        
        self.input_panel = InputPanel(self.right_frame, self.handle_launch, self.handle_jackpot_click, self.handle_multi_pull_soul, self.soul_fragments)
        self.input_panel.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.update() 
        self.update_pity_bar()

    def update_pity_bar(self):
        """Dessine et colorie la barre de Pity."""
        self.pity_canvas.delete("all")
        width = self.pity_canvas.winfo_width()
        if width <= 1: width = 600 # Sécurité si la fenêtre n'est pas encore dessinée
        
        fill_width = (self.pity_counter / self.pity_max) * width
        
        # Couleur : Blanc si < 5, Violet si = 5
        color = "#9C27B0" if self.pity_counter >= self.pity_max else "white"
        
        self.pity_canvas.create_rectangle(0, 0, fill_width, 25, fill=color, outline="")
        self.pity_label.config(text=f"PITIÉ (Légendaire Garanti) : {self.pity_counter} / {self.pity_max}")
    

    def handle_launch(self, rolls):
        tier_val = rolls["tier"]
        original_roll = rolls["tier"] # On garde le vrai jet en mémoire pour vérifier le seuil
        is_pity_pull = False

        # --- 1. VÉRIFICATION DE LA PITY ---
        if self.pity_counter >= self.pity_max:
            tier_val = 20 # On force le jet à 20 (Légendaire !)
            self.pity_counter = 0
            generator.save_gacha_pity(self.pity_counter) # Sauvegarde la remise à zéro
            is_pity_pull = True

        tier_data = generator.determine_tier(tier_val)
        if not tier_data:
            messagebox.showerror("Erreur", "Tier roll invalide.")
            self.input_panel.btn_lancer.config(state=tk.NORMAL)
            return

        # --- 2. MISE À JOUR DE LA PITY, DU CASHBACK ET SAUVEGARDE ---
        if not is_pity_pull:
            if tier_data["name"] == "Legendary":
                self.pity_counter = 0 # Reset organique
                generator.save_gacha_pity(self.pity_counter)
            
            # --- NOUVEAU : LOGIQUE DU CASHBACK D'ÂME ---
            elif tier_data["name"] == "Common":
                self.soul_fragments += 1 # Gagne 1 fragment !
                generator.save_gacha_fragments(self.soul_fragments)
                self.input_panel.update_soul_fragments(self.soul_fragments) # Met à jour l'UI

                # On vérifie aussi la Pity classique si le jet est faible
                if original_roll <= self.pity_threshold:
                    self.pity_counter += 1
                    generator.save_gacha_pity(self.pity_counter)
            
            elif original_roll <= self.pity_threshold and tier_data["name"] != "Vide":
                self.pity_counter += 1
                generator.save_gacha_pity(self.pity_counter)
                
        self.update_pity_bar()

        # --- 3. MÉCANIQUE DE FAKE-OUT (Ascenseur émotionnel) ---
        is_fake_out = False
        fake_out_target = None
        
        # 5% de chance de fake-out sur un jet non-légendaire, non-vide et non-pity
        if tier_data["name"] not in ["Legendary", "Vide"] and not is_pity_pull:
            if random.randint(1, 100) <= 5: 
                is_fake_out = True
                fake_out_target = generator.determine_tier(20) # Devient Légendaire !

        # --- LANCEMENT DE LA ROUE ---
        if is_fake_out:
            # On tourne vers le "faux" tier, puis on déclenche l'animation de rupture
            self.wheel.spin_to_tier(tier_data["name"], lambda: self.trigger_fake_out(fake_out_target))
        else:
            # Comportement normal
            self.wheel.spin_to_tier(tier_data["name"], lambda: self.generate_and_display(tier_data))

    def trigger_fake_out(self, real_tier_data):
        """Animation textuelle de rupture pour l'effet Fake-Out."""
        self.result_panel.clear()
        self.result_panel.text_area.config(state=tk.NORMAL, bg="white", fg="black")
        self.result_panel.text_area.insert(tk.END, "\n\n... Attente de la matière ...\n")
        self.update()
        
        # Effet visuel : l'écran devient noir et le texte rouge sang
        self.after(400, lambda: self._fake_out_step_2(real_tier_data))

    def _fake_out_step_2(self, real_tier_data):
        self.result_panel.text_area.config(bg="#1E1E1E", fg="#FF0000")
        self.result_panel.text_area.insert(tk.END, "\n⚠ ANOMALIE DÉTECTÉE ⚠\nLA MATIÈRE SE FRAGMENTE !!\n")
        self.update()
        
        # Puisque le fake-out donne un légendaire, on remet la Pity à 0
        self.pity_counter = 0
        generator.save_gacha_pity(self.pity_counter)
        self.update_pity_bar()

        # On affiche le vrai loot après 1 seconde de suspense
        self.after(1200, lambda: self._finish_fake_out(real_tier_data))

    def _finish_fake_out(self, real_tier_data):
        self.result_panel.text_area.config(bg="#1E1E1E", fg="#00FF00") # Retour au vert Matrix
        self.generate_and_display(real_tier_data)


    def _build_single_item(self, tier_data):
        """Génère mécaniquement un objet complet basé sur un tier, sans affichage."""
        if tier_data["name"] == "Vide":
            return None
            
        item = LootItem()
        item.tier = tier_data["name"]
        
        min_type, max_type = generator.get_bounds(generator.ITEM_TYPES)
        type_roll = random.randint(min_type, max_type)
        type_data = generator.determine_item_type(type_roll)
        item.item_type = type_data["name"]
        
        if type_data["id"] == "scroll":
            min_scroll, max_scroll = generator.get_bounds(generator.SCROLLS.get("rarities", []))
            scroll_roll = random.randint(min_scroll, max_scroll)
            rar_data = generator.determine_scroll_rarity(scroll_roll)
            if rar_data:
                valid_spells = [s for s in generator.SCROLLS.get("spells", []) if s.get("rarity_id") == rar_data["id"]]
                if valid_spells:
                    spell_data = generator.determine_scroll_spell(rar_data["id"], random.randint(1, len(valid_spells)))
                    if spell_data:
                        item.base_name = f"Parchemin de {spell_data['name']} ({rar_data['name']})"
                        item.description = spell_data["description"]
        else:
            valid_bases = [b for b in generator.BASE_ITEMS if b.get("type_id") == type_data["id"]]
            if not valid_bases: # Sécurité anti-crash si le JSON est vide pour ce type
                return None
                
            min_base, max_base = generator.get_bounds(valid_bases)
            base_data = generator.determine_base_item(type_data["id"], random.randint(min_base, max_base))
            
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
                if item.tier == "Common": num_affixes = random.choice([0, 1])
                
                min_affix, max_affix = generator.get_bounds(generator.AFFIXES)
                for _ in range(num_affixes):
                    affix = generator.determine_affix(random.randint(min_affix, max_affix))
                    if affix:
                        item.affixes.append(affix)
                        item.merge_stats(affix.get("stats_modifier", {}))
                        if "effect" in affix: item.effects.append(affix["effect"])
                        if not item.prefix and "prefix" in affix: item.prefix = affix["prefix"]
                        elif not item.suffix and "suffix" in affix: item.suffix = affix["suffix"]

                if tier_data.get("has_unique_effect", False):
                    min_u, max_u = generator.get_bounds(generator.UNIQUE_EFFECTS)
                    unique_data = generator.get_unique_effect(random.randint(min_u, max_u))
                    if unique_data:
                        item.effects.append(f"*** UNIQUE : {unique_data['name']} ***\n      {unique_data['description']}")
                        item.prefix = "Mythique"

        base_value_pc = {
            "Common": random.randint(50, 5000), "Uncommon": random.randint(5000, 20000),
            "Rare": random.randint(20000, 150000), "Very Rare": random.randint(150000, 450000),
            "Legendary": random.randint(450000, 1000000)
        }
        total_pc = int(base_value_pc.get(item.tier, 0) * (1.0 + (0.15 * len(item.affixes))))
        item.set_price_from_copper(total_pc)
        
        return item


    def generate_and_display(self, tier_data):
        if tier_data["name"] == "Vide":
            self.result_panel.clear()
            if random.randint(1, 100) <= 68:
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
            else:
                self.result_panel.append_text("¯\_(oo))_/¯ LE COFFRE EST VIDE...\n\n")
                self.result_panel.append_text("Il n'y a absolument rien ici à part de la poussière.")
            self.input_panel.btn_lancer.config(state=tk.NORMAL)
            return
            
        item = self._build_single_item(tier_data)
        if item:
            self.current_items.append(item)
            self.result_panel.display_item(item)
            self.after(500, self.ask_jackpot)

    def ask_jackpot(self):
        # --- NOUVEAU : On affiche le gros bouton au lieu du pop-up ---
        self.result_panel.append_text("\n $$$ [?] VOULEZ-VOUS TENTER LE le JACKPOT ??? $$$ ")
        self.input_panel.show_jackpot() 
        self.input_panel.btn_lancer.config(state=tk.NORMAL)

    def handle_jackpot_click(self):
        # --- NOUVEAU : Action quand le bouton est cliqué ---
        self.input_panel.btn_lancer.config(state=tk.DISABLED) # On rebloque le lancer normal
        jackpot_roll = random.randint(1, 100)
        self.process_jackpot(jackpot_roll)

    def process_jackpot(self, roll):
        self.jackpot_history.append(roll)
        self.result_panel.append_text(f"[?] Lancement du Jackpot... ")
        # On fait tourner la roue pour le suspense, puis on applique
        self.wheel.spin_to_tier("Common", lambda: self._apply_jackpot_logic(roll)) 

    def _apply_jackpot_logic(self, roll):
        if not self.current_items:
            self.input_panel.btn_lancer.config(state=tk.NORMAL)
            return
            
        # On travaille toujours sur le dernier item généré
        item = self.current_items[-1]

        if 1 <= roll <= 50:
            self.current_items.clear()
            self.result_panel.append_text("X_X PERTE TOTALE : Le coffre se referme... tout a disparu.")
            self.input_panel.btn_lancer.config(state=tk.NORMAL)
            
        elif 51 <= roll <= 70:
            self.result_panel.append_text("--- RIEN : Le vent souffle, rien ne se passe.")
            self.result_panel.append_text("\n> Fin du Jackpot. Vous conservez votre butin actuel.")
            self.input_panel.btn_lancer.config(state=tk.NORMAL)

            
        elif 71 <= roll <= 85:
            self.result_panel.append_text("[+] SECOND ITEM : Gagné ! (Remplissez les champs et relancez pour générer le 2nd item)")
            self.input_panel.btn_lancer.config(state=tk.NORMAL)
            
        elif 86 <= roll <= 95:
            self._upgrade_item(item, to_legendary=False)
            self.result_panel.display_item(item)
            self.result_panel.append_text("\n^^^ UPGRADE : L'objet s'illumine et devient plus puissant !")
            self.after(1000, self.ask_jackpot)
            
        elif roll >= 96:
            self._upgrade_item(item, to_legendary=True)
            self.result_panel.append_text("*** JACKPOT ABSOLU ! L'item devient Légendaire !")
            self.after(1000, self.ask_jackpot) 

    def _upgrade_item(self, item, to_legendary=False):
        """Améliore mécaniquement l'objet (Stats, Affixes, Prix, Effet Unique)."""
        tiers_order = ["Common", "Uncommon", "Rare", "Very Rare", "Legendary"]
        if item.tier not in tiers_order:
            return # Ne s'applique pas aux parchemins par exemple

        current_idx = tiers_order.index(item.tier)
        
        # Détermine le nouveau palier
        if to_legendary:
            new_idx = len(tiers_order) - 1
        else:
            new_idx = min(current_idx + 1, len(tiers_order) - 1)

        # S'il y a bien une montée de niveau
        if new_idx > current_idx:
            new_tier_name = tiers_order[new_idx]
            item.tier = new_tier_name
            
            # 1. On récupère les règles du nouveau Tier
            tier_data = next((t for t in generator.TIERS if t["name"] == new_tier_name), None)
            if not tier_data: return

            # 2. Ajout des affixes manquants si le nouveau tier permet d'en avoir plus
            target_affixes = tier_data.get("base_affixes", 0)
            current_affixes = len(item.affixes)
            
            if target_affixes > current_affixes:
                min_affix, max_affix = generator.get_bounds(generator.AFFIXES)
                for _ in range(target_affixes - current_affixes):
                    r = random.randint(min_affix, max_affix)
                    affix = generator.determine_affix(r)
                    if affix:
                        item.affixes.append(affix)
                        item.merge_stats(affix.get("stats_modifier", {}))
                        if "effect" in affix: item.effects.append(affix["effect"])
                        
                        # Met à jour le nom si possible
                        if not item.prefix and "prefix" in affix:
                            item.prefix = affix["prefix"]
                        elif not item.suffix and "suffix" in affix:
                            item.suffix = affix["suffix"]

            # 3. Ajout d'un effet unique si le nouveau tier le permet (et qu'on n'en a pas déjà un)
            has_unique = any("UNIQUE" in e for e in item.effects)
            if tier_data.get("has_unique_effect", False) and not has_unique:
                min_unique, max_unique = generator.get_bounds(generator.UNIQUE_EFFECTS)
                unique_roll = random.randint(min_unique, max_unique)
                unique_data = generator.get_unique_effect(unique_roll)
                if unique_data:
                    item.effects.append(f"*** UNIQUE : {unique_data['name']} ***\n      {unique_data['description']}")
                    item.prefix = "Mythique" # Force un nom épique

            # 4. On triple la valeur marchande de l'objet !
            total_copper = (item.price_po * 10000) + (item.price_pa * 100) + item.price_pc
            item.set_price_from_copper(int(total_copper * 3.0))

    def handle_multi_pull_soul(self, count, tier_garanti=None):
        """Déduit les fragments et génère les items d'un coup."""
        # 1. CONSOMMATION ET SAUVEGARDE DES ÂMES
        self.soul_fragments -= count
        generator.save_gacha_fragments(self.soul_fragments)
        self.input_panel.update_soul_fragments(self.soul_fragments)
        
        self.input_panel.btn_lancer.config(state=tk.DISABLED)
        self.input_panel.hide_jackpot()
        self.result_panel.clear()
        
        # 2. GÉNÉRATION DE LA LISTE
        multi_items = []
        for i in range(count):
            # Application de la garantie sur le TOUT DERNIER jet (ex: le 10ème)
            if i == count - 1 and tier_garanti:
                t_data = tier_garanti
            else:
                t_data = generator.determine_tier(random.randint(1, 20))
                
            item = self._build_single_item(t_data)
            
            if item:
                multi_items.append(item)
                self.current_items.append(item)
            else:
                # Création d'un "Faux" objet vide pour l'affichage de la liste
                empty_item = LootItem()
                empty_item.tier = "Vide"
                multi_items.append(empty_item)
                self.current_items.append(empty_item)
                
        # 3. AFFICHAGE GROUPÉ
        self.result_panel.display_multi_items(multi_items)
        self.input_panel.btn_lancer.config(state=tk.NORMAL)
        self.update_pity_bar()

    def _animate_marquee(self):
        """Fait défiler le texte de droite à gauche sur le Canvas."""
        # Sécurité : si on a changé d'écran, on arrête l'animation
        if not hasattr(self, 'marquee_canvas') or not self.marquee_canvas.winfo_exists():
            return
            
        # Vitesse de défilement (-4 pixels vers la gauche)
        self.marquee_canvas.move(self.marquee_text_id, -4, 0)
        
        coords = self.marquee_canvas.coords(self.marquee_text_id)
        if coords:
            # Si le texte est parti beaucoup trop loin à gauche, on le relance à droite
            if coords[0] < -8000: 
                self.marquee_canvas.coords(self.marquee_text_id, self.winfo_width(), 32)
                
        # On boucle l'animation toutes les 30 millisecondes (environ 30 FPS)
        self.after(30, self._animate_marquee)

    def _blink_title(self):
        """Fait clignoter le titre principal entre Or et Rouge vif."""
        if not hasattr(self, 'title_label') or not self.title_label.winfo_exists():
            return
            
        current_fg = self.title_label.cget("fg")
        new_fg = "#FF0000" if current_fg == "#FFD700" else "#FFD700"
        self.title_label.config(fg=new_fg)
        
        # On boucle le clignotement toutes les 600 ms
        self.after(600, self._blink_title)

    def save_and_reset(self):
        # log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "log")
        if getattr(sys, 'frozen', False):
            # Le dossier où se trouve le fichier .exe
            exe_dir = os.path.dirname(sys.executable)
            log_dir = os.path.join(exe_dir, "log")
        else:
            # Le dossier racine du script Python
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            log_dir = os.path.join(script_dir, "log")
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

