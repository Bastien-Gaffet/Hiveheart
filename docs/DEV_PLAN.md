# Development Plan — Hiveheart

## Guiding principle

Build the smallest thing that proves the game is fun, then layer on top.
Never add rendering before the mechanic it visualises is working.
Never add a mechanic before the architecture supports it cleanly.

## Structural decisions (locked)

- **World**: infini, basé sur un système de chunks (`CHUNK_SIZE = 16`)
- **Génération**: bruit Simplex multi-couches (fertilité, pollution, humidité) avec seed globale
- **Sauvegarde**: cloud (Supabase ou équivalent) — uniquement les chunks modifiés (deltas)
- **Proto**: grille fixe 20×15 jusqu'à Phase 10. Migration chunk en Phase 10.5.
- **Règle**: ne jamais hardcoder `GRID_WIDTH × GRID_HEIGHT` dans la logique jeu (seulement dans la génération initiale du proto)

---

## Phase 1 — Skeleton (get something on screen)

- [x] `config/constants.py` with all constants
- [x] `game/tile.py` — Tile dataclass
- [x] `game/world.py` — World with 2D grid, `get_tile(x, y)`
- [x] `game/resources.py` — Resources counters
- [x] `core/game.py` — Systems list + `update(dt)` loop
- [x] `main.py` — pygame init, window, clock, basic loop
- [x] `render/renderer.py` — draw grid as coloured rects (fertility → colour)

**Checkpoint**: grey-to-green grid visible on screen. No interaction yet.

---

## Phase 2 — First entity

- [x] `entities/entity.py` — base Entity
- [x] `entities/bee.py` — Bee with position, target, speed, bee_type
- [x] `render/renderer.py` — draw bees as yellow circles with bobbing
- [x] One Worker bee hardcoded at (100, 100) in `main.py`

**Checkpoint**: one bee visible, gently bobbing.

---

## Phase 3 — Drag & drop

- [x] `systems/input_system.py` — click bee to select, release to assign target
- [x] `render/camera.py` — basic camera, screen↔world coordinate conversion
- [x] Camera passed to input system so mouse clicks map to world coords correctly

**Checkpoint**: can drag bee to a tile. Bee stays put (no movement yet).

---

## Phase 4 — Movement

- [x] `systems/movement_system.py` — bee moves toward target at `bee.speed`
- [x] Bee stops when within 2px of target

**Checkpoint**: drag a bee, it flies to the tile.

---

## Phase 5 — Ecological loop

- [x] `systems/ecosystem_system.py` — fertility → flowers, pollution → damage, biome transitions
- [x] Worker bee on a tile boosts `fertility`
- [x] `resources.nectar` accumulates from flowers
- [x] `render/renderer.py` — biome colour changes visible in real time (formula already uses fertility/flowers)

**Checkpoint**: drop bee on dead tile → tile turns green → flowers appear → nectar goes up. This is the core loop working.

---

## Phase 6 — Visual polish (first pass)

- [x] `render/effects.py` — `draw_glow()` fake shader
- [x] `render/particle_system.py` — pollen particles spawn when bee works a tile
- [x] Camera pan (WASD/arrows) and zoom (scroll wheel)
- [x] Tile colour interpolation (smooth transition)
- [x] Flower dots drawn on fertile tiles (seeded random position per tile)

**Checkpoint**: game looks and feels alive. Showable to others.

---

## Phase 7 — HUD

- [x] `render/ui.py` — nectar counter, bee panel (hive)
- [x] Bee panel: drag bees from UI onto map
- [x] Multiple Worker bees spawnable (costs nectar)

**Checkpoint**: full core loop: earn nectar → spend nectar → more bees → more nectar.

---

## Phase 8 — Scout bee

- [ ] Scout bee type: reveals fog of war (tiles start hidden)
- [ ] `render/renderer.py` — fog of war layer (dark overlay on unrevealed tiles)
- [ ] Scout assigned to a tile removes fog in radius

**Checkpoint**: exploration mechanic works.

---

## Phase 9 — First threat

- [ ] `systems/threat_system.py` — pollution spreads from toxic tiles each second
- [ ] Visible feedback when pollution is spreading (tile flickers or pulses)
- [ ] Player must act before ecosystem collapses

**Checkpoint**: game has tension. Not just zen management anymore.

---

## Phase 10 — Mission structure (proto)

- [ ] Win condition: `biodiversity_score` above threshold
- [ ] Lose condition: all tiles reach `biome = "toxic"` within time limit
- [ ] Mission 1 : jardin abandonné (rythme tutoriel)
- [ ] Écran win/lose state

**Checkpoint**: Hiveheart est jouable avec un début, un milieu, une fin.

---

## Phase 10.5 — Monde infini (migration chunk)

> Pivot architectural avant le save system. Le proto grille fixe est remplacé.

- [ ] `config/constants.py` — ajouter `CHUNK_SIZE = 16`
- [ ] `game/chunk.py` — Chunk : grille locale `CHUNK_SIZE × CHUNK_SIZE` de Tiles
- [ ] `game/world_generator.py` — génération procédurale via bruit Simplex multi-couches :
  - Couche 1 (grande échelle) → fertilité de base
  - Couche 2 (échelle moyenne) → pollution (taches industrielles)
  - Couche 3 (petite échelle) → humidité + rivières
  - Biomes émergent de la combinaison des 3 valeurs
- [ ] `game/world.py` — refacto : `chunks: dict[tuple[int,int], Chunk]`, génération à la demande
- [ ] `render/renderer.py` — tiles visibles calculées depuis position caméra (plus de boucle fixe)
- [ ] `services/storage_interface.py` — interface par chunk : `save_chunk()`, `load_chunk()`, `save_meta()`

**Checkpoint**: monde infini scrollable, chunks générés à la volée, cohérent visuellement aux frontières.

---

## Phase 11 — Save system (local d'abord)

- [ ] `services/local_storage.py` — JSON par chunk, uniquement les chunks modifiés (deltas vs génération)
- [ ] Déclenché manuellement (touche S) ou à la fermeture
- [ ] Format : `seed` + `tile_deltas` par chunk + `bees` + `resources`

---

## Phase 12 — Save system cloud

- [ ] `services/supabase_storage.py` (ou provider équivalent) — implémente la même interface
- [ ] Schéma DB : `saves`, `chunks`, `tile_deltas`, `bees`, `resources`
- [ ] Swap dans `main.py` : zéro changement dans le code jeu
- [ ] Sync au save manuel + chargement au démarrage

---

## Future phases (post-proto)

- Pathfinding (A*) pour les abeilles autour des obstacles
- Types d'abeilles supplémentaires (Architect, Chemist, Guardian, Queen, Traveler)
- Musiques ambiantes par biome
- Animations sprite sheet pour abeilles et fleurs
- Cycles saisonniers (hiver/printemps affectent fertilité et nectar)
- Entités passives (papillons, oiseaux) apparaissant selon seuils de biodiversité
- Menaces supplémentaires (feu, sécheresse, monoculture)
- Système d'évolution des abeilles (dépense de pollen)
- Écran de sélection de mission
- Paramètres (volume, résolution)

---

## What NOT to build yet

- Multijoueur
- Classements
- Système de compte / auth
- IA complexe
- 3D ou shaders au-delà du fake glow
- Input mobile

Ces éléments viennent après que la boucle solo soit fun et stable.
