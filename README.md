# Loot Casino Generator 🎰

Une application de bureau Python permettant aux Maîtres du Jeu (JDR, D&D) de transformer la distribution de butin en une véritable expérience de Casino et de Gacha. Ce projet génère du loot de manière procédurale tout en intégrant des mécaniques psychologiques diaboliques : système de "Pitié", bannières d'invocation, emprunts usuraires et malédictions dynamiques.

## Fonctionnalités Principales

* **Génération Procédurale :** Création d'équipements avec des statistiques de base, des affixes aléatoires (préfixes/suffixes) et des effets uniques selon la rareté.
* **Mécaniques de Gacha :** * Système de "Pitié" (Pity) garantissant un objet Légendaire au bout de X tirages malchanceux.
    * Fragments d'Âme (Cashback) pour acheter des multi-tirages (x5, x10 avec rareté garantie).
    * Bannières ciblées payantes (Armurerie, Mystique, Éleveur) pour filtrer les types de butin.
* **Le Pacte Faustien :** Les joueurs peuvent contracter un prêt usuraire pour obtenir des tirages gratuits, en échange d'une dette colossale en pièces d'or et d'une malédiction active en jeu.
* **Forge & Jackpot :** Possibilité de transmuter un objet non désiré ou de tenter un "Quitte ou Double" pour l'améliorer jusqu'au rang Légendaire (au risque de tout perdre).
* **Suivi et Rétention :** Calcul automatique du "Bankroll" (Cagnotte de session), rang VIP évolutif et un "Gacha-Dex" pour traquer les objets uniques découverts.

## Installation et Lancement

1. Assurez-vous d'avoir Python 3.8 ou supérieur installé sur votre machine.
2. Installez les dépendances requises (gestion de l'audio) :
   ```bash
   pip install pygame
   ```
3. Lancez l'application depuis la racine du projet :
   ```bash
   python main.py
   ```

*(Note pour l'audio : Placez vos fichiers `spin.wav`, `win.wav`, `epic.wav`, `jackpot.wav` et `error.wav` dans le dossier `assets/`. Si le dossier est vide, le jeu fonctionnera silencieusement sans erreur).*

## Configuration des Données (Fichiers JSON) ⚙️

Toute l'intelligence du générateur repose sur les fichiers JSON situés dans le dossier `data/`. Vous pouvez créer une infinité d'objets sans jamais toucher au code Python.

### 1. L'Index `base_items.json`
Pour éviter d'avoir un fichier gigantesque, `base_items.json` agit comme un **sommaire**. Il liste les sous-fichiers que l'application doit lire et fusionner au démarrage.
```json
[
    "items_melee.json",
    "items_ranged.json",
    "items_armor.json",
    "items_pet.json"
]
```

### 2. Créer un objet (Exemple dans `items_melee.json`)
Chaque sous-fichier contient une liste d'objets de base.
```json
[
    {
        "id": "sword_01",
        "name": "Épée Longue en Acier",
        "type_id": "melee",
        "description": "Une lame standard mais bien équilibrée.",
        "base_stats": {
            "Dégâts": 8,
            "Poids": 3
        }
    }
]
```
*Le `type_id` est crucial : il doit correspondre aux catégories définies dans l'application pour que les Bannières d'invocation fonctionnent (ex: "pet_capsule" pour la bannière Éleveur).*

### 3. Les Malédictions (`curses.json`)
Ce fichier définit les punitions appliquées lorsqu'un joueur fait un échec critique ou contracte un prêt au marché noir.
```json
[
    {
        "name": "Poches Trouées",
        "description": "Vous perdez 10% de votre or à chaque repos long.",
        "duration": "3 Jours"
    }
]
```

### 4. Affixes, Tiers et Effets Uniques
Les autres fichiers (ex: `affixes.json`, `tiers.json`, `unique_effects.json`) contrôlent les modificateurs de statistiques et les probabilités. 
* **Tiers :** Définissent le nombre d'affixes qu'un objet peut recevoir (ex: Rare = 2 affixes, Légendaire = 4 affixes + 1 Effet Unique).
* **Affixes :** Ajoutent des statistiques dynamiques (`{"Dégâts": 2}`) et modifient le nom de l'objet (ex: "Épée Longue en Acier *du Sanglier*").

## Utilisation en Partie (JDR)

1. **Le Lancer de Dé :** Le joueur lance un véritable D20 physique à la table.
2. **La Saisie :** Le Maître du Jeu entre le résultat dans le champ "Résultat du D20".
3. **La Résolution :** L'application calcule les probabilités (Pitié, Mimic, Fake-out), fait tourner la roue visuelle et génère l'objet avec son prix marchand estimé.
4. **Sauvegarde :** En fin de session, cliquez sur "Terminer le tirage" pour enregistrer l'historique dans le dossier `log/` et sauvegarder la progression VIP du groupe.
