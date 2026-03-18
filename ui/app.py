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
from core.audio import audio_player

class LootCasinoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Générateur de Loot Casino $$$")
        try:
            self.state('zoomed')
        except tk.TclError:
            self.attributes('-zoomed', True)
        
        self.configure(bg="#222")
        
        self.current_items = []
        self.jackpot_history = []
        self.session_total_pc = 0

        self.is_cursed_mode = False

        pity_cfg = generator.GACHA_DATA.get("pity", {})
        self.pity_counter = pity_cfg.get("current_pity", 0)
        self.pity_max = pity_cfg.get("max_pity", 10)
        self.pity_threshold = pity_cfg.get("max_roll_to_increment", 3)

        self.soul_fragments = generator.GACHA_DATA.get("soul_fragments", 0)
        self.frag_icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "soul_fragment.png")
        
        self.build_start_screen()

    def launch_game(self, cursed):
        self.is_cursed_mode = cursed
        self.build_main_screen()

    def load_recent_history(self):
        if getattr(sys, 'frozen', False):
            log_dir = os.path.join(os.path.dirname(sys.executable), "log")
        else:
            log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "log")
            
        if not os.path.exists(log_dir): return "♦ BIENVENUE A LA GRAND ROUE DU LOOT ! FAITES VOTRE PREMIER TIRAGE ! ♦"
        files = sorted([f for f in os.listdir(log_dir) if f.startswith("tirage_") and f.endswith(".json")], reverse=True)
        if not files: return "♦ BIENVENUE A LA GRAND ROUE DU LOOT ! FAITES VOTRE PREMIER TIRAGE ! ♦"
            
        recent_items = []
        for f in files[:5]:
            try:
                with open(os.path.join(log_dir, f), "r", encoding="utf-8") as file:
                    data = json.load(file)
                    for item in data.get("items", []):
                        if item.get("tier") != "Vide" and item.get("name"):
                            recent_items.append(f"[{item.get('tier').upper()}] {item.get('name')}")
            except Exception: pass
        if not recent_items: return "♦ LA BANQUE EST PLEINE ! LANCEZ LES DÉS ! ♦"
        history_str = "   ✦   ".join(recent_items)
        return f"   ✦   {history_str}   ✦   " * 10

    def get_combinations_count(self):
        """Calcule mathématiquement le nombre de combinaisons uniques possibles."""
        try:
            nb_bases = len(generator.BASE_ITEMS)
            nb_affixes = len(generator.AFFIXES)
            nb_uniques = len(generator.UNIQUE_EFFECTS)
            
            # Calcul combinatoire : 
            # Objets sans affixe + avec 1 affixe + avec 2 affixes + avec 3 affixes
            combos_affixes = (
                1 + 
                nb_affixes + 
                (nb_affixes * (nb_affixes - 1) // 2) + 
                (nb_affixes * (nb_affixes - 1) * (nb_affixes - 2) // 6)
            )
            
            # Base * Combinaisons d'affixes * (Avec ou sans effet unique)
            total_equip = nb_bases * combos_affixes * (1 + nb_uniques)
            
            # On ajoute les parchemins
            nb_scrolls = len(generator.SCROLLS.get("spells", [])) * len(generator.SCROLLS.get("rarities", []))
            
            total = total_equip + nb_scrolls
            
            # Formate le nombre avec des espaces pour la lisibilité (ex: 1 250 430)
            return f"{total:,}".replace(",", " ")
        except Exception:
            return "des millions de"

    def get_vip_level(self):
        """Calcule le statut VIP du groupe en fonction du nombre de tirages totaux."""
        rolls = generator.GACHA_DATA.get("total_rolls", 0)
        if rolls >= 160: return 5, "BALEINE LÉGENDAIRE", "#FFD700" # Or
        if rolls >= 80: return 4, "FLAMBEUR MAÎTRE", "#E040FB"     # Violet
        if rolls >= 40: return 3, "HABITUÉ DU CASINO", "#00FFFF"   # Cyan
        if rolls >= 20: return 2, "CLIENT RÉGULIER", "#00FF00"      # Vert
        if rolls >= 10: return 1, "AMATEUR", "#FFFFFF"              # Blanc
        return 0, "NOUVEAU JOUEUR", "#888888"                       # Gris

    def open_gachadex(self):
        """Ouvre une fenêtre pop-up affichant la collection des objets découverts."""
        dex_window = tk.Toplevel(self)
        dex_window.title("⌘ Gacha-Dex - La Collection")
        dex_window.geometry("600x700")
        dex_window.configure(bg="#111")
        
        tk.Label(dex_window, text="COMPLEXE DU COLLECTIONNEUR", font=("Impact", 24), bg="#111", fg="#FFD700").pack(pady=20)
        
        # Statistiques
        total_bases = len(generator.BASE_ITEMS)
        discovered = len(generator.GACHA_DATA.get("discovered_bases", []))
        pct = int((discovered / total_bases) * 100) if total_bases > 0 else 0
        
        tk.Label(dex_window, text=f"Objets Uniques Découverts : {discovered} / {total_bases} ({pct}%)", font=("Arial", 16, "bold"), bg="#111", fg="#00FFFF").pack(pady=10)
        
        # Liste déroulante
        list_frame = tk.Frame(dex_window, bg="#222")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(list_frame, bg="#222", fg="#FFF", font=("Consolas", 12), yscrollcommand=scrollbar.set)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Peupler la liste avec de la frustration
        for base in generator.BASE_ITEMS:
            name = base["name"]
            if name in generator.GACHA_DATA.get("discovered_bases", []):
                listbox.insert(tk.END, f"✓ {name}")
                listbox.itemconfig(tk.END, {'fg': '#00FF00'})
            else:
                listbox.insert(tk.END, f"▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒")
                listbox.itemconfig(tk.END, {'fg': '#444444'})
                
        tk.Button(dex_window, text="FERMER LE REGISTRE", bg="#E53935", fg="white", font=("Arial", 12, "bold"), command=dex_window.destroy).pack(pady=10)

    def open_pay_debt(self):
        """Ouvre une boîte de dialogue pour rembourser une partie ou toute la dette."""
        from tkinter import simpledialog # Importation locale pour éviter les bugs
        
        current_debt = generator.GACHA_DATA.get("debt_po", 0)
        if current_debt <= 0:
            return
            
        # Ouvre une fenêtre demandant un chiffre
        amount = simpledialog.askinteger(
            "Guichet du Casino", 
            f"La mafia vous regarde avec insistance.\nVotre dette est de {current_debt} PO.\n\nCombien de PO souhaitez-vous rembourser ?", 
            minvalue=1, maxvalue=current_debt, parent=self
        )
        
        if amount: # Si le joueur a cliqué sur "OK" avec un montant valide
            # On déduit la somme
            generator.GACHA_DATA["debt_po"] -= amount
            generator._save_all_data() # Sauvegarde forcée dans le JSON
            
            new_debt = generator.GACHA_DATA["debt_po"]
            
            if new_debt <= 0:
                messagebox.showinfo("Contrat Terminé", "☆★ DETTE SOLDÉE ! ★☆ \n\nLe Casino vous remercie de votre honnêteté. Vos malédictions sont levées... pour le moment.")
            else:
                messagebox.showinfo("Paiement Accepté", f"Paiement de {amount} PO reçu.\nIl vous reste encore {new_debt} PO à rembourser. Ne traînez pas.")
            
            # On rafraîchit l'écran d'accueil pour mettre à jour le montant sur le bouton (ou le cacher)
            self.build_start_screen()

    def build_start_screen(self):
        self.clear_window()
        self.start_frame = tk.Frame(self, bg="#111")
        self.start_frame.pack(expand=True, fill=tk.BOTH)
        
        self.marquee_canvas = tk.Canvas(self.start_frame, bg="#002200", height=60, highlightthickness=3, highlightbackground="#00FF00")
        self.marquee_canvas.pack(fill=tk.X, pady=(0, 40))
        history_text = self.load_recent_history()
        self.marquee_text_id = self.marquee_canvas.create_text(1500, 32, text=history_text, font=("Consolas", 18, "bold"), fill="#FFFF00", anchor="w")
        self.marquee_x_pos = 1500 
        self._animate_marquee()

        vip_level, vip_title, vip_color = self.get_vip_level()
        
        tk.Label(self.start_frame, text=f"♚ STATUT : VIP {vip_level} - {vip_title} ♚", font=("Arial", 14, "bold"), bg="#111", fg=vip_color).pack(pady=(0, 10))

        self.title_label = tk.Label(self.start_frame, text="$$$ GRAND ROUE DU LOOT $$$", font=("Impact", 48, "bold"), bg="#111", fg="#FFD700")
        self.title_label.pack(pady=(40, 10))
        self._blink_title()

        combo_count = self.get_combinations_count()
        self.combo_label = tk.Label(self.start_frame, text=f"♠♡♢♣ Plus de {combo_count} combinaisons d'objets uniques ! ♣♢♡♠", 
                                    font=("Arial", 18, "bold"), bg="#111", fg="#00FFFF")
        self.combo_label.pack(pady=(0, 30))
        
        tk.Label(self.start_frame, text="Seul le hasard décide de votre destin...", font=("Arial", 16, "italic"), bg="#111", fg="#888").pack(pady=(0, 30))

        # --- NOUVEAUX BOUTONS D'ENTRÉE ---
        self.btn_play = tk.Button(self.start_frame, text=" ENTRER DANS LE CASINO (Classique) ", font=("Arial", 22, "bold"), 
                                  bg="#E53935", fg="white", activebackground="#FFEB3B", activeforeground="red", 
                                  relief=tk.RAISED, bd=8, padx=40, pady=10, command=lambda: self.launch_game(False))
        self.btn_play.pack(pady=10)

        self.btn_blood = tk.Button(self.start_frame, text="☙ MARCHÉ NOIR (-1 PV MAX) ☙", font=("Arial", 18, "bold"), 
                                  bg="#4a0000", fg="#ff4444", activebackground="#ff0000", activeforeground="black", 
                                  relief=tk.RAISED, bd=5, padx=40, pady=10, command=lambda: self.launch_game(True))
        self.btn_blood.pack(pady=10)

       
        self.btn_dex = tk.Button(self.start_frame, text="⌘ VOIR LA COLLECTION (GACHA-DEX)", font=("Arial", 14, "bold"), 
                                  bg="#1E88E5", fg="white", relief=tk.RAISED, bd=4, padx=20, pady=5, command=self.open_gachadex)
        self.btn_dex.pack(pady=20)

        current_debt = generator.GACHA_DATA.get("debt_po", 0)
        if current_debt > 0:
            formatted_debt = f"{current_debt:,}".replace(",", " ")
            self.btn_pay_debt = tk.Button(self.start_frame, text=f"$ REMBOURSER LA DETTE ({formatted_debt} PO) $", 
                                          font=("Arial", 14, "bold"), bg="#FF9800", fg="black", 
                                          relief=tk.RAISED, bd=4, padx=20, pady=5, command=self.open_pay_debt)
            self.btn_pay_debt.pack(pady=10)

    def build_main_screen(self):
        self.clear_window()
        self.current_items = []
        self.jackpot_history = []
        
        self.left_frame = tk.Frame(self, bg="#222")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Le fond change selon le mode !
        bg_color = "#4a0000" if self.is_cursed_mode else "#004d00"
        
        self.right_frame = tk.Frame(self, bg=bg_color, width=300)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.wheel = CasinoWheel(self.left_frame, size=600)
        self.wheel.pack(pady=10)
        
        self.result_panel = ResultPanel(self.left_frame)
        self.result_panel.pack(fill=tk.BOTH, expand=True)

        self.bankroll_frame = tk.Frame(self.right_frame, bg="#000", bd=5, relief=tk.SUNKEN)
        self.bankroll_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(10, 0))
        tk.Label(self.bankroll_frame, text="TOTAL DES GAINS", fg="#888", bg="#000", font=("Arial", 10, "bold")).pack(pady=(5,0))
        
        self.lbl_bankroll = tk.Label(self.bankroll_frame, text="0 PO", fg="#FF0000", bg="#000", font=("Courier", 24, "bold"))
        self.lbl_bankroll.pack(pady=(0, 5))

        self.debt_po = generator.GACHA_DATA.get("debt_po", 0)
        self.lbl_debt = tk.Label(self.bankroll_frame, text="", fg="#ff4444", bg="#000", font=("Arial", 10, "bold"))
        self.lbl_debt.pack(pady=(0, 5))

        self._update_bankroll_display(0)
        self._update_debt_display()

        self.btn_finish = tk.Button(self.right_frame, text="> TERMINER LE TIRAGE <", bg="#2196F3", fg="white", 
                                    font=("Arial", 12, "bold"), command=self.save_and_reset)
        self.btn_finish.pack(side=tk.BOTTOM, pady=20, padx=10, fill=tk.X)

        vip_level, _, _ = self.get_vip_level()
        self.current_pity_max = 4 if vip_level >= 2 else self.pity_max # VIP 2
        discounted_x10_cost = 8 if vip_level >= 4 else 10 # VIP 4

        self.pity_frame = tk.Frame(self.right_frame, bg=bg_color)
        self.pity_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 20))
        
        self.pity_label = tk.Label(self.pity_frame, text=f"PITIÉ : {self.pity_counter} / {self.current_pity_max}", bg=bg_color, fg="white", font=("Arial", 12, "bold"))
        self.pity_label.pack()
        
        self.pity_canvas = tk.Canvas(self.pity_frame, height=20, bg="#222", highlightthickness=1, highlightbackground="#555")
        self.pity_canvas.pack(fill=tk.X, pady=5)
        
        
        self.input_panel = InputPanel(
            self.right_frame, self.handle_launch, self.handle_jackpot_click, 
            self.handle_multi_pull_soul, self.handle_loan, self.handle_forge, 
            self.soul_fragments, x10_cost=discounted_x10_cost, is_cursed=self.is_cursed_mode
        )

        self.input_panel.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.update() 
        self.update_pity_bar()

    def _update_bankroll_display(self, additional_pc):
        """Met à jour le compteur de gains de la session."""
        self.session_total_pc += additional_pc
        
        # Le fun du jackpot : si on perd tout, ça peut baisser en dessous de zéro !
        display_pc = max(0, self.session_total_pc)
        
        po = display_pc // 10000
        pa = (display_pc % 10000) // 100
        pc = display_pc % 100
        
        if po > 0: display = f"{po} PO {pa} PA"
        elif pa > 0: display = f"{pa} PA {pc} PC"
        else: display = f"{pc} PC"
            
        self.lbl_bankroll.config(text=display)
    def _update_debt_display(self):
        """Met à jour le texte de la dette usuraire."""
        if self.debt_po > 0:
            self.lbl_debt.config(text=f"☠ DETTE EN COURS : {self.debt_po:,} PO ☠".replace(",", " "))
        else:
            self.lbl_debt.config(text="")

    def handle_loan(self):
        """Le Pacte Faustien : des fragments contre une dette colossale et un malus."""
        msg = (" PACTE D'USURE\n\n"
               "Vous êtes sur le point d'emprunter 5 Fragments d'Âme.\n\n"
               "EN ÉCHANGE :\n"
               "1. Vous contractez une dette immédiate de 1000 PO.\n"
               "2. Vous subirez une MALÉDICTION aléatoire en jeu tant que la dette ne sera pas payée.\n\n"
               "Signer avec votre sang ?")
               
        if messagebox.askyesno("L'Entité vous écoute", msg):
            # Application de la dette et des âmes
            self.debt_po += 1000
            generator.GACHA_DATA["debt_po"] = self.debt_po
            
            self.soul_fragments += 5
            generator.save_gacha_fragments(self.soul_fragments) # Ceci sauvegarde aussi la dette !
            
            self.input_panel.update_soul_fragments(self.soul_fragments)
            self._update_debt_display()
            
            curses = [
                "Vulnérabilité au Feu et à l'Acide.", 
                "Malchance : Désavantage sur vos jets de sauvegarde.", 
                "Paranoïa : Impossible de faire un repos long réparateur.", 
                "Poches trouées : Vous perdez 10% de votre or par jour.",
                "Cécité nocturne : Vous êtes aveugle dans la pénombre."
            ]
            chosen_curse = random.choice(curses)
            
            self.result_panel.clear()
            self.result_panel.set_banner("Vide")
            self.result_panel.append_text(f"☠ CONTRAT SIGNÉ ☠ \n\n+5 Fragments d'Âme reçus.\n-1000 PO de Dette ajoutés au registre.\n\nMALÉDICTION ACTIVE : {chosen_curse}\n")
            self.result_panel.append_text("Le Casino vous remercie de votre fidélité éternelle.")

    def handle_forge(self):
        """Détruit le dernier objet généré pour en recréer un nouveau du même Tier."""
        if not self.current_items or self.current_items[-1].tier == "Vide":
            messagebox.showwarning("Transmutation", "Il n'y a aucun objet valide à transmuter ! Lancez d'abord les dés.")
            return
            
        cost = 3
        if self.soul_fragments < cost:
            return # Sécurité
            
        old_item = self.current_items[-1]
        
        if messagebox.askyesno("Forge des Âmes", f"Dépenser {cost} Âmes pour détruire [{old_item.base_name}] et générer un NOUVEL objet garanti de Tier {old_item.tier} ?"):
            # Déduction des âmes
            self.soul_fragments -= cost
            generator.save_gacha_fragments(self.soul_fragments)
            self.input_panel.update_soul_fragments(self.soul_fragments)
            
            # Retrait de l'argent de l'ancien objet de la Bankroll
            old_pc = (old_item.price_po * 10000) + (old_item.price_pa * 100) + old_item.price_pc
            self._update_bankroll_display(-old_pc)
            
            # Recherche des données du Tier actuel pour forger le nouveau
            tier_dict = next((t for t in generator.TIERS if t["name"] == old_item.tier), None)
            if not tier_dict: return
            
            # Création du nouvel objet
            new_item = self._build_single_item(tier_dict)
            self.current_items[-1] = new_item # Remplace l'ancien objet dans l'historique
            
            # Ajout de l'argent du nouvel objet
            new_pc = (new_item.price_po * 10000) + (new_item.price_pa * 100) + new_item.price_pc
            self._update_bankroll_display(new_pc)
            
            self.result_panel.clear()
            self.result_panel.set_banner(new_item.tier)
            self.result_panel.append_text("⚒ LA MATIÈRE SE MÉTAMORPHOSE ! ⚒\n")
            self.result_panel.display_item(new_item)

    def update_pity_bar(self):
        self.pity_canvas.delete("all")
        width = self.pity_canvas.winfo_width()
        if width <= 1: width = 600
        fill_width = (self.pity_counter / self.pity_max) * width
        color = "#9C27B0" if self.pity_counter >= self.pity_max else "white"
        self.pity_canvas.create_rectangle(0, 0, fill_width, 25, fill=color, outline="")
        self.pity_label.config(text=f"PITIÉ (Légendaire Garanti) : {self.pity_counter} / {self.pity_max}")

    def handle_launch(self, rolls):
        tier_val = rolls["tier"]
        original_roll = rolls["tier"]
        is_pity_pull = False

        selected_banner = self.input_panel.banner_var.get()
        banner_cost = 0
        if "Armurerie" in selected_banner: banner_cost = 1
        elif "Mystique" in selected_banner: banner_cost = 2

        if banner_cost > 0:
            if self.soul_fragments < banner_cost:
                messagebox.showerror("Fonds Insuffisants", f"Cette bannière coûte {banner_cost} Fragment(s) d'Âme.\nFaites des tirages Standard pour en obtenir !")
                self.input_panel.btn_lancer.config(state=tk.NORMAL)
                return
            # On déduit le coût
            self.soul_fragments -= banner_cost
            generator.save_gacha_fragments(self.soul_fragments)
            self.input_panel.update_soul_fragments(self.soul_fragments)
        # -----------------------------------------

        generator.increment_rolls(1)

        if self.pity_counter >= self.pity_max:
            tier_val = 20
            self.pity_counter = 0
            generator.save_gacha_pity(self.pity_counter)
            is_pity_pull = True

        tier_data = generator.determine_tier(tier_val)
        if not tier_data:
            messagebox.showerror("Erreur", "Tier roll invalide.")
            self.input_panel.btn_lancer.config(state=tk.NORMAL)
            return

        if not is_pity_pull:
            if tier_data["name"] == "Legendary":
                self.pity_counter = 0 
                generator.save_gacha_pity(self.pity_counter)
            
            elif tier_data["name"] == "Common":
                self.soul_fragments += 1
                generator.save_gacha_fragments(self.soul_fragments)
                self.input_panel.update_soul_fragments(self.soul_fragments)

                if original_roll <= self.pity_threshold:
                    self.pity_counter += 1
                    generator.save_gacha_pity(self.pity_counter)
            
            elif original_roll <= self.pity_threshold and tier_data["name"] != "Vide":
                self.pity_counter += 1
                generator.save_gacha_pity(self.pity_counter)
                
        self.update_pity_bar()

        is_fake_out = False
        fake_out_target = None
        
        if tier_data["name"] not in ["Legendary", "Vide"] and not is_pity_pull:
            if random.randint(1, 100) <= 5: 
                is_fake_out = True
                fake_out_target = generator.determine_tier(20)

        
        if is_fake_out:
            self.wheel.spin_to_tier(tier_data["name"], lambda: self.trigger_fake_out(fake_out_target))
        else:
            self.wheel.spin_to_tier(tier_data["name"], lambda: self.generate_and_display(tier_data))

    def trigger_fake_out(self, real_tier_data):
        self.result_panel.clear()
        self.result_panel.set_banner("Vide") # On éteint le bandeau pour le suspense
        self.result_panel.text_area.config(state=tk.NORMAL, bg="white", fg="black")
        self.result_panel.text_area.insert(tk.END, "\n\n... Attente de la matière ...\n")
        self.update()
        self.after(400, lambda: self._fake_out_step_2(real_tier_data))

    def _fake_out_step_2(self, real_tier_data):
        self.result_panel.text_area.config(bg="#1E1E1E", fg="#FF0000")
        audio_player.play("alarm")
        self.result_panel.text_area.insert(tk.END, "\n⚠ ANOMALIE DÉTECTÉE ⚠\nLA MATIÈRE SE FRAGMENTE !!\n")
        self.update()
        self.pity_counter = 0
        generator.save_gacha_pity(self.pity_counter)
        self.update_pity_bar()
        self.after(1200, lambda: self._finish_fake_out(real_tier_data))

    def _finish_fake_out(self, real_tier_data):
        self.result_panel.text_area.config(bg="#1E1E1E", fg="#00FF00")
        self.generate_and_display(real_tier_data)

    def _build_single_item(self, tier_data):
        if tier_data["name"] == "Vide": return None
        item = LootItem()
        item.tier = tier_data["name"]
        
        selected_banner = self.input_panel.banner_var.get()
        
        if "Armurerie" in selected_banner:
            # Filtre uniquement les armes et armures
            allowed = ["melee", "ranged", "armor"]
            filtered_types = [t for t in generator.ITEM_TYPES if t["id"] in allowed]
            type_data = random.choice(filtered_types)
            
        elif "Mystique" in selected_banner:
            # Filtre uniquement la magie, les familiers et les reliques
            allowed = ["scroll", "artifact", "pet_capsule"]
            filtered_types = [t for t in generator.ITEM_TYPES if t["id"] in allowed]
            type_data = random.choice(filtered_types)
            
        else:
            # Bannière Standard (Comportement normal)
            min_type, max_type = generator.get_bounds(generator.ITEM_TYPES)
            type_data = generator.determine_item_type(random.randint(min_type, max_type))
        # ------------------------------------------
        
        item.item_type = type_data["name"]
        
        if type_data["id"] == "scroll":
            min_scroll, max_scroll = generator.get_bounds(generator.SCROLLS.get("rarities", []))
            rar_data = generator.determine_scroll_rarity(random.randint(min_scroll, max_scroll))
            if rar_data:
                valid_spells = [s for s in generator.SCROLLS.get("spells", []) if s.get("rarity_id") == rar_data["id"]]
                if valid_spells:
                    spell_data = generator.determine_scroll_spell(rar_data["id"], random.randint(1, len(valid_spells)))
                    if spell_data:
                        item.base_name = f"Parchemin de {spell_data['name']} ({rar_data['name']})"
                        item.description = spell_data["description"]
        else:
            valid_bases = [b for b in generator.BASE_ITEMS if b.get("type_id") == type_data["id"]]
            if not valid_bases: return None
                
            min_base, max_base = generator.get_bounds(valid_bases)
            base_data = generator.determine_base_item(type_data["id"], random.randint(min_base, max_base))
            
            if base_data:
                item.base_name = base_data["name"]
                generator.add_discovery(item.base_name)
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
            self.result_panel.set_banner("Vide")
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
        # --- NOUVEAU : LA PROPOSITION MAUDITE ---
            if self.is_cursed_mode:
                if messagebox.askyesno("Pacte de Sang", "Votre tirage est perdu...\n\nL'entité vous propose un marché :\nSacrifiez ENCORE 1 PV MAX pour relancer le dé immédiatement. Acceptez-vous ?"):
                    self.result_panel.append_text("\n\n☙ [PACTE] Vous sacrifiez une partie de votre âme (-1 PV MAX).")
                    self.result_panel.append_text("Le coffre se referme dans un bruit visqueux... Relancez le dé ! ☙")
                    # On laisse le bouton de lancer actif pour qu'il rejoue !
            return
            
        item = self._build_single_item(tier_data)
        if item:
            item_pc = (item.price_po * 10000) + (item.price_pa * 100) + item.price_pc
            self._update_bankroll_display(item_pc)
            self.result_panel.set_banner(item.tier)
            self.current_items.append(item)
            self.result_panel.display_item(item)
            self.after(500, self.ask_jackpot)

    def ask_jackpot(self):
        # --- NOUVEAU : On affiche le gros bouton au lieu du pop-up ---
        self.result_panel.append_text("\n $$$ [?] VOULEZ-VOUS TENTER LE le JACKPOT ??? $$$ ")
        self.input_panel.show_jackpot() 
        self.input_panel.btn_lancer.config(state=tk.NORMAL)

    def handle_jackpot_click(self):
        self.input_panel.btn_lancer.config(state=tk.DISABLED) 
        audio_player.play("spin")
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
            
        item = self.current_items[-1]

        if 1 <= roll <= 50:
            self.current_items.clear()
            self.result_panel.set_banner("Vide") 
            self.result_panel.append_text("X_X PERTE TOTALE : Le coffre se referme... tout a disparu.")
            self._update_bankroll_display(-self.session_total_pc) 
            
            self.input_panel.btn_lancer.config(state=tk.NORMAL)
            
        elif 51 <= roll <= 70:
            self.result_panel.append_text("--- RIEN : Le vent souffle, rien ne se passe.")
            self.result_panel.append_text("\n> Fin du Jackpot. Vous conservez votre butin actuel.")
            self.input_panel.btn_lancer.config(state=tk.NORMAL)
            
        elif 71 <= roll <= 85:
            self.result_panel.append_text("\n[+] SECOND ITEM : Gagné ! (Remplissez les champs et relancez pour générer le 2nd item)")
            self.input_panel.btn_lancer.config(state=tk.NORMAL)
            
        elif 86 <= roll <= 95:
            self._upgrade_item(item, to_legendary=False)
            self.result_panel.display_item(item)
            self.result_panel.append_text("\n^^^ UPGRADE : L'objet s'illumine et devient plus puissant !")
            self.after(1000, self.ask_jackpot)
            
        elif roll >= 96:
            self._upgrade_item(item, to_legendary=True)
            self.result_panel.set_banner("Legendary") # Force l'affichage légendaire
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
        """Déduit les fragments, génère les items, calcule la cagnotte et trouve le meilleur loot."""
        generator.increment_rolls(count)
        self.soul_fragments -= count
        generator.save_gacha_fragments(self.soul_fragments)
        self.input_panel.update_soul_fragments(self.soul_fragments)
        
        self.input_panel.btn_lancer.config(state=tk.DISABLED)
        self.input_panel.hide_jackpot()
        self.result_panel.clear()
        
        multi_items = []
        
        # --- NOUVEAU : Variables pour la Bankroll et le Bandeau ---
        total_multi_pc = 0
        tiers_order = ["Vide", "Common", "Uncommon", "Rare", "Very Rare", "Legendary"]
        best_tier_idx = -1
        best_tier_name = "Vide"
        # ----------------------------------------------------------

        for i in range(count):
            if i == count - 1 and tier_garanti:
                t_data = tier_garanti
            else:
                t_data = generator.determine_tier(random.randint(1, 20))
                
            item = self._build_single_item(t_data)
            
            if item:
                multi_items.append(item)
                self.current_items.append(item)
                
                # Ajout de l'argent de cet objet au total de la multi
                item_pc = (item.price_po * 10000) + (item.price_pa * 100) + item.price_pc
                total_multi_pc += item_pc
                
                # Vérification du meilleur tier pour le bandeau
                current_idx = tiers_order.index(item.tier) if item.tier in tiers_order else 0
                if current_idx > best_tier_idx:
                    best_tier_idx = current_idx
                    best_tier_name = item.tier

            else:
                empty_item = LootItem()
                empty_item.tier = "Vide"
                multi_items.append(empty_item)
                self.current_items.append(empty_item)
                
                # Si le meilleur tier est toujours indéfini, on met Vide
                if best_tier_idx == -1:
                    best_tier_idx = 0
                    best_tier_name = "Vide"
                
        # --- NOUVEAU : Mise à jour de l'UI avec les calculs ---
        if total_multi_pc > 0:
            self._update_bankroll_display(total_multi_pc) # Monte la cagnotte d'un coup !
            
        self.result_panel.set_banner(best_tier_name, is_multi=True) # Affiche le meilleur loot
        # ------------------------------------------------------
        
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
            
        self.build_start_screen()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

