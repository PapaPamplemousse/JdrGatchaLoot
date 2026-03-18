import json
import os
from .models import LootItem

# Chemin relatif vers le dossier data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

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