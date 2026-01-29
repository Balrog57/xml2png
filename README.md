# 🖼️ XML2PNG (Python Edition)

Un fork dédié au visuel. Il génère automatiquement des assets (Wheels, cartouches) à partir de fichiers XML pour habiller vos interfaces.

## Fonctionnalités

- **Traitement par lot** : Génération de milliers d'images basées sur les bases de données XML Hyperspin/EmulationStation.
- **Système de calques avancé** : 
  - **Calque d'arrière-plan** : Adapte automatiquement la taille du canevas à l'image de fond. Supporte la transparence.
  - **10 Calques configurables** : Combinez Texte, Images Statiques, et Images Variables basées sur des dossiers.
- **Personnalisation de texte riche** :
  - **Styles** : Gras, Italique, Souligné.
  - **Formatage** : Sélecteur de couleur (Hex/Palette), Alignement (Gauche/Centre/Droite).
  - **Contrôles** : Limite de caractères max, support Préfixe & Suffixe.
  - **Contenu dynamique** : Utilisez Description du jeu, Année, Genre, Fabricant, ou Nom du jeu (Nom de fichier ou balise XML `<name>`).
  - **Polices** : Scanne et utilise les polices système installées avec fonctionnalité de recherche.
- **Aperçu en temps réel** : 
  - Éditeur visuel avec gestion précise du ratio d'aspect.
  - Mise en évidence de la boîte englobante du calque sélectionné.
  - Mode texte de démonstration quand aucun XML n'est chargé (montre l'exemple : Sonic The Hedgehog 2).
- **Bascules de visibilité des calques** : Icône œil pour afficher/masquer les calques individuels sans perdre les réglages.
- **Transformations d'image** : Miroir (flip horizontal), Étirement (ignorer le ratio), Rotation (0°, 90°, 180°, 270°).
- **Expérience Utilisateur** :
  - Arrêt/Pause de la génération.
  - Détection automatique de `assets/backgrounds` pour une sélection facile du fond.
- **Haute Performance** : Construit avec Python et Pillow pour un traitement d'image rapide.

## Prérequis

- Python 3.10+
- PyQt6
- Pillow

## Installation

1. Clonez le dépôt.
2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
3. Lancez l'application :
   ```bash
   python src/main.py
   ```

## Utilisation

1. **Sélectionner XML** : Chargez votre fichier XML Hyperspin ou EmulationStation.
2. **Sélectionner Destination** : Choisissez où les images générées seront sauvegardées.
3. **Configurer l'arrière-plan** :
   - Placez vos images de fond dans `assets/backgrounds`.
   - Sélectionnez le calque "Background" et choisissez votre image dans le menu déroulant.
   - La taille de l'image de sortie correspondra à la résolution de votre fond.
4. **Configurer les calques** :
   - Activez jusqu'à 10 calques.
   - Choisissez **Texte**, **Image Statique**, ou **Image Dossier** (correspond au nom de fichier ROM).
   - Personnalisez la position, la taille et les styles.
5. **Générer** : Cliquez sur "GENERATE ALL IMAGES". Vous pouvez arrêter le processus à tout moment.

## Création de l'exécutable

Pour construire l'exécutable `.exe` autonome :
```bash
pyinstaller xml2png.spec
```
L'exécutable se trouvera dans le dossier `dist/XML2PNG_Build/`.

## Modules Clés

- **src/model** : Analyse XML (`xml_parser.py`) et logique de Composition d'Image (`compositor.py`).
- **src/view** : Interface Utilisateur PyQt6 (`main_window.py`, `layer_controls.py`, `preview_widget.py`).
- **src/controller** : Logique de l'application et threading (`app_controller.py`).

## Credits

Ce projet est un fork modernisé et réécrit en Python de l'application originale **Xml2Png** créée par **r0man0 (Romain Langlois)**.

**Remerciements originaux :**
* Merci à : https://www.autohotkey.com/
* Plus d'applications et de contenus pour votre frontend à : http://r0man0.free.fr

[Voir le projet original sur le site de r0man0](http://r0man0.free.fr/index.php/fr/a-propos-de-xml2png/)

