# core/models.py
class LootItem:
    def __init__(self):
        self.tier = ""
        self.item_type = ""
        self.base_name = ""
        self.prefix = ""
        self.suffix = ""
        self.stats = {}
        self.effects = []
        self.description = ""
        self.affixes = []
        self.set_id = None
        self.set_name = ""
        self.set_bonuses = {}
        
        # Nouvelles variables pour l'économie
        self.price_po = 0
        self.price_pa = 0
        self.price_pc = 0

    def get_full_name(self):
        parts = []
        if self.prefix: parts.append(self.prefix)
        parts.append(self.base_name)
        if self.suffix: parts.append(self.suffix)
        return " ".join(parts)

    def merge_stats(self, new_stats):
        for stat, value in new_stats.items():
            if stat in self.stats:
                self.stats[stat] += value
            else:
                self.stats[stat] = value

    def set_price_from_copper(self, total_pc):
        """Convertit un total de pièces de cuivre en PO, PA, PC"""
        self.price_po = total_pc // 10000
        remaining = total_pc % 10000
        self.price_pa = remaining // 100
        self.price_pc = remaining % 100

    def get_price_string(self):
        """Formate le prix pour l'affichage"""
        parts = []
        if self.price_po > 0: parts.append(f"{self.price_po} PO")
        if self.price_pa > 0: parts.append(f"{self.price_pa} PA")
        if self.price_pc > 0: parts.append(f"{self.price_pc} PC")
        return " ".join(parts) if parts else "0 PC"

    def to_dict(self):
        data = {
            "name": self.get_full_name(),
            "tier": self.tier,
            "type": self.item_type,
            "value": self.get_price_string(),
            "stats": self.stats,
            "effects": self.effects,
            "description": self.description,
            "affixes": [a["name"] for a in self.affixes]
        }
        if self.set_id:
            data["set"] = {"name": self.set_name, "bonuses": self.set_bonuses}
        return data