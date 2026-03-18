# Generateur de Loot - Type Gacha / Casino

## Contexte du Projet

En tant que Maître du Jeu (MJ) pour mes sessions de jeu de rôle (JDR), je cherchais un moyen de rendre la découverte de butin plus excitante pour mes joueurs. J'avais envie que chaque ouverture de coffre ressemble à un tirage de type "gacha" ou à une machine à sous de casino. 

Ce projet est donc un générateur de loot doté d'une interface graphique interactive. Le MJ entre le résultat d'un simple jet de dé (1 à 20) effectué par un joueur, et l'application s'occupe d'animer une roue et de générer un objet complet de manière procédurale, avec un système de "Jackpot" optionnel pour le quitte ou double.

## Fonctionnalités

* **Interface graphique native** : Utilisation de Python (Tkinter) avec animation fluide d'une roue de casino.
* **Génération procédurale** : Création d'armes de mêlée, armes à distance, armures, accessoires, artefacts et parchemins magiques.
* **100% Configurable** : Toute la logique (probabilités, types d'objets, affixes, effets uniques, panoplies/sets) repose sur des fichiers JSON facilement modifiables sans toucher au code.
* **Mécanique de Jackpot** : Les joueurs peuvent décider de remettre leur butin en jeu pour tenter de l'améliorer (changement de tier, double affixe, etc.), avec le risque permanent de tout perdre.
* **Économie intégrée** : Calcul automatique de la valeur marchande de l'objet généré en pièces d'or, d'argent et de cuivre (PO/PA/PC).
* **Sauvegarde automatique** : Historique des tirages conservé dans un dossier de logs au format JSON.

## Installation et Lancement

Le projet est conçu pour être léger et fonctionner sans aucune dépendance externe complexe (pas de `pip install` requis).

1. Assurez-vous d'avoir Python 3.x installé sur votre machine.
2. Téléchargez ou clonez le répertoire du projet.
3. Placez une image `croupier.png` dans le dossier `assets/` (taille recommandée : environ 200 à 250 pixels de large).
4. Exécutez le script principal depuis votre terminal :

```bash
python main.py
```

## Structure des Dossiers

* `main.py` : Le point d'entrée de l'application.
* `core/` : Contient la logique de génération (`generator.py`) et la structure des données de l'objet (`models.py`).
* `ui/` : Contient le contrôleur de l'interface graphique (`app.py`), la roue animée (`wheel.py`) et les panneaux d'affichage interactifs (`panels.py`).
* `data/` : Contient l'ensemble des fichiers de configuration JSON qui servent de base de données.
* `assets/` : Dossier réservé aux ressources visuelles de l'interface.
* `log/` : Dossier généré automatiquement pour stocker les sauvegardes de fin de tirage.
```
