# Hiveheart

God game écologique : guider des abeilles pour ramener à la vie des écosystèmes mourants.

Le joueur n'est pas une abeille. Il est l'esprit de la ruche, une force invisible qui guide la vie. Le monde est malade, et il le soigne case par case en glissant ses abeilles vers les zones à restaurer.

## État

Prototype. La boucle de jeu de base fonctionne : monde en grille généré par bruit, abeilles déplaçables à la souris, caméra, et un système écologique où la fertilité fait pousser des fleurs, où la pollution abîme les cases et où les biomes évoluent. La suite est détaillée dans [docs/DEV_PLAN.md](docs/DEV_PLAN.md).

## Lancer

```bash
pip install -r requirements.txt
python main.py
```

Python 3.11 ou plus récent, avec [pygame-ce](https://pyga.me) et `opensimplex`.

## Architecture

Inspirée de l'ECS (entités, composants, systèmes), avec trois règles strictes :

- la logique du jeu (`game/`, `entities/`, `systems/`) n'importe jamais `pygame` ;
- le rendu (`render/`) ne modifie jamais l'état du jeu ;
- un système ne gère qu'une seule chose (mouvement, écosystème, entrées...).

La documentation de conception est dans [docs/](docs/) : game design, architecture, modèle de données et direction visuelle.
