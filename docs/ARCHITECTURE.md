# Architecture — Hiveheart

## Design philosophy

The architecture follows a lightweight ECS-inspired pattern:
- **Entities** hold data only (no logic)
- **Systems** hold logic only (no rendering)
- **Renderer** reads state, never writes it
- **Services** are swappable implementations behind interfaces

This means:
- `game/`, `entities/`, `systems/` never import `pygame`
- `render/` never modifies game state
- `services/` is the only layer that touches external storage

---

## Data flow

```
User input
    ↓
InputSystem (systems/input_system.py)
    ↓
Game state mutation (entities/, game/)
    ↓
Other systems update (MovementSystem, EcosystemSystem…)
    ↓
Renderer reads state (render/)
    ↓
Screen output
```

---

## Full file structure

```
hiveheart/
│
├── main.py                     # Entry point — assembles everything
├── requirements.txt
│
├── config/
│   └── constants.py            # TILE_SIZE, GRID_WIDTH, SCREEN dimensions, speeds
│
├── core/
│   ├── game.py                 # Game loop: holds systems list, calls update()
│   └── time.py                 # Delta time, game clock utilities
│
├── game/
│   ├── tile.py                 # Tile dataclass (fertility, pollution, flowers, biome)
│   ├── world.py                # 2D grid of Tiles, get_tile(x,y)
│   └── resources.py            # Global resource counters (nectar, pollen, hive energy)
│
├── entities/
│   ├── entity.py               # Base Entity (x, y, id)
│   └── bee.py                  # Bee entity (target, speed, bee_type, animation state)
│
├── systems/
│   ├── input_system.py         # Mouse events → bee selection + drag & drop
│   ├── movement_system.py      # Moves bees toward their target
│   ├── ecosystem_system.py     # Tile evolution, biome transitions, resource gain
│   └── threat_system.py        # Pollution spread, drought, fires (add later)
│
├── render/
│   ├── renderer.py             # Master draw() — calls sub-renderers
│   ├── world_renderer.py       # Tiles + biome colours
│   ├── bee_renderer.py         # Bee sprites + glow + bobbing animation
│   ├── particle_system.py      # Pollen particles, sparkles
│   ├── ui.py                   # HUD: nectar bar, bee panel, mission info
│   ├── camera.py               # Zoom + pan (apply offset to all draw calls)
│   └── effects.py              # Fake shaders: glow surfaces, bloom
│
├── services/
│   ├── storage_interface.py    # Abstract base: save_game(), load_game()
│   ├── local_storage.py        # JSON file implementation (use this first)
│   └── firebase_storage.py     # Firebase implementation (add later if needed)
│
├── assets/
│   ├── sprites/                # Bee frames, flower sprites, tile textures
│   ├── ui/                     # Panel backgrounds, icons
│   ├── sounds/                 # Buzz, bloom, nectar collect
│   └── music/                  # Ambient tracks per biome
│
├── data/
│   ├── saves/                  # Local save files
│   └── settings.json
│
└── docs/                       # All design documents (this folder)
```

---

## Module responsibilities (strict)

### `config/constants.py`
All magic numbers live here. No hardcoded values in other files.

```python
TILE_SIZE = 32
GRID_WIDTH = 20
GRID_HEIGHT = 15
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BEE_SPEED = 100  # px/sec
```

### `core/game.py`
Owns the list of active systems. Calls `system.update(dt)` on each every frame.
Does not know anything about pygame, rendering, or specific game rules.

### `game/world.py`
The 2D grid. Provides `get_tile(grid_x, grid_y)` and `get_tile_at_pixel(px, py)`.
Does not apply rules — that is the ecosystem system's job.

### `systems/ecosystem_system.py`
The most important system. Applies ecological rules each frame:
- Fertility drives flower growth
- Pollution suppresses flowers
- Bees on a tile boost fertility
- Biome transitions based on thresholds
- Nectar accumulates from flowers

### `systems/input_system.py`
Translates raw pygame mouse events into game actions:
- `MOUSEBUTTONDOWN` → find bee under cursor → begin drag
- `MOUSEBUTTONUP` → assign target tile to dragged bee
- `MOUSEWHEEL` → camera zoom

### `render/camera.py`
Holds `offset_x`, `offset_y`, `zoom`. Provides `world_to_screen(wx, wy)` and `screen_to_world(sx, sy)`.
All draw calls must pass through camera transform.

### `services/storage_interface.py`
Abstract base class. All save/load calls go through this interface.
Swap implementations without touching game code.

---

## Dependency rules (enforced)

```
main.py       → can import everything
core/         → imports nothing from the project
game/         → imports only config/
entities/     → imports only config/
systems/      → imports game/, entities/, config/
render/       → imports game/, entities/, config/, core/
services/     → imports game/ only (for serialisation shapes)
```

`pygame` is allowed only in `render/` and `main.py`.

---

## Adding a new bee type

1. Add a constant in `config/constants.py`: `BEE_TYPE_GUARDIAN = "guardian"`
2. Extend `entities/bee.py` with any new fields needed
3. Add handling in `systems/ecosystem_system.py` (what the bee does on its target)
4. Add visual in `render/bee_renderer.py`
5. Add to hive panel in `render/ui.py`

No other files need to change.

---

## Storage abstraction pattern

```python
# services/storage_interface.py
class StorageInterface:
    def save_game(self, data: dict) -> None:
        raise NotImplementedError

    def load_game(self) -> dict:
        raise NotImplementedError

# services/local_storage.py
import json, os

class LocalStorage(StorageInterface):
    PATH = "data/saves/save.json"

    def save_game(self, data):
        os.makedirs("data/saves", exist_ok=True)
        with open(self.PATH, "w") as f:
            json.dump(data, f)

    def load_game(self):
        with open(self.PATH) as f:
            return json.load(f)
```

To switch to Firebase or Supabase later: implement the same interface, pass a different instance in `main.py`. Zero game code changes.
