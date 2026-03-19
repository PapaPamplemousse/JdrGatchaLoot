import json
import os
import random
from .models import LootItem
import sys


def get_resource_path():
    """Obtient le dossier absolu, compatible avec PyInstaller."""
    if getattr(sys, 'frozen', False):
        # Si on est dans un exécutable compilé
        return sys._MEIPASS
    # Si on est en script normal
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(get_resource_path(), "data")


def load_json(filename):
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        return [] # Retourne liste vide si le fichier n'existe pas encore
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

TIERS = load_json("tiers.json")
ITEM_TYPES = load_json("item_types.json")
BASE_ITEMS = load_json("base_items.json")
AFFIXES = load_json("affixes.json")
SCROLLS = load_json("scrolls.json")
UNIQUE_EFFECTS = load_json("unique_effects.json")
SETS = load_json("sets.json")

def get_from_table(table, roll):
    for entry in table:
        if entry["min"] <= roll <= entry["max"]:
            return entry
    return None

def determine_tier(roll): return get_from_table(TIERS, roll)
def determine_item_type(roll): return get_from_table(ITEM_TYPES, roll)
def determine_base_item(type_id, roll):
    valid_items = [item for item in BASE_ITEMS if item.get("type_id") == type_id]
    return get_from_table(valid_items, roll)
def determine_scroll_rarity(roll): return get_from_table(SCROLLS.get("rarities", []), roll)
def determine_scroll_spell(rarity_id, roll):
    valid_spells = [spell for spell in SCROLLS.get("spells", []) if spell.get("rarity_id") == rarity_id]
    if not valid_spells: return None
    idx = max(0, min(roll - 1, len(valid_spells) - 1))
    return valid_spells[idx]
def determine_affix(roll): return get_from_table(AFFIXES, roll)
def get_unique_effect(roll): return get_from_table(UNIQUE_EFFECTS, roll)
def get_set_info(set_id):
    if isinstance(SETS, dict): return SETS.get(set_id, None)
    return None
def get_bounds(table):
    """Scan un tableau JSON pour trouver le min global et le max global."""
    if not table:
        return 1, 1
    min_val = min(entry.get("min", 1) for entry in table)
    max_val = max(entry.get("max", 1) for entry in table)
    return min_val, max_val

# --- CHARGEMENT DU FICHIER DE DONNÉES GACHA ---
GACHA_FILE = os.path.join(DATA_DIR, "gacha_data.json")

def load_gacha_data():
    """Charge les données de Pity, de Fragments, le VIP et le Gacha-Dex."""
    try:
        with open(GACHA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Rétrocompatibilité : on ajoute les nouvelles clés si elles manquent
            if "total_rolls" not in data: data["total_rolls"] = 0
            if "debt_po" not in data: data["debt_po"] = 0
            if "discovered_bases" not in data: data["discovered_bases"] = []
            return data
    except FileNotFoundError:
        return {
            "pity": {"max_pity": 10, "max_roll_to_increment": 3, "current_pity": 0},
            "soul_fragments": 0,
            "total_rolls": 0,
            "debt_po": 0,
            "discovered_bases": []
        }

# Initialisation des données locales
GACHA_DATA = load_gacha_data()

def save_gacha_pity(current_pity):
    GACHA_DATA["pity"]["current_pity"] = current_pity
    _save_all_data()

def save_gacha_fragments(fragment_count):
    GACHA_DATA["soul_fragments"] = fragment_count
    _save_all_data()

# --- NOUVELLES FONCTIONS DE SUIVI (VIP & DEX) ---
def increment_rolls(count=1):
    """Augmente le nombre total de tirages pour le niveau VIP."""
    GACHA_DATA["total_rolls"] += count
    _save_all_data()

def add_discovery(base_name):
    """Ajoute un objet au Gacha-Dex s'il n'a jamais été vu."""
    if base_name and base_name not in GACHA_DATA["discovered_bases"]:
        GACHA_DATA["discovered_bases"].append(base_name)
        _save_all_data()
        return True # C'est une nouvelle découverte !
    return False

def _save_all_data():
    """Sauvegarde tout le JSON sur le disque."""
    try:
        with open(GACHA_FILE, "w", encoding="utf-8") as f:
            json.dump(GACHA_DATA, f, indent=4)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde Gacha : {e}")

def save_gacha_pity(current_pity):
    """Met à jour et sauvegarde la pitié."""
    GACHA_DATA["pity"]["current_pity"] = current_pity
    _save_all_data()

def save_gacha_fragments(fragment_count):
    """Met à jour et sauvegarde le nombre de fragments."""
    GACHA_DATA["soul_fragments"] = fragment_count
    _save_all_data()

def _save_all_data():
    """Sauvegarde tout le JSON sur le disque."""
    try:
        with open(GACHA_FILE, "w", encoding="utf-8") as f:
            json.dump(GACHA_DATA, f, indent=4)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde Gacha : {e}")

CURSES_FILE = os.path.join(DATA_DIR, "curses.json")

def load_curses():
    try:
        with open(CURSES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # Malédiction de secours si le fichier manque
        return [{"name": "Malchance Gacha", "description": "Désavantage sur tout.", "duration": "1 Jour"}]

CURSES = load_curses()

def get_random_curse():
    """Tire une malédiction aléatoire depuis le JSON."""
    if not CURSES:
        return {"name": "Malchance Gacha", "description": "Désavantage sur tout.", "duration": "1 Jour"}
    return random.choice(CURSES)