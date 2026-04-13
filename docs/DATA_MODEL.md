# Data Model & Ecological Rules — Hiveheart

## Tile

The atomic unit of the world. Every cell in the grid is a Tile.

```python
class Tile:
    fertility:  float = 0.2   # 0.0–1.0. High = flowers grow. Low = nothing lives.
    pollution:  float = 0.5   # 0.0–1.0. High = suppresses fertility and flowers.
    humidity:   float = 0.3   # 0.0–1.0. Low = drought risk. High = moisture bonus.
    flowers:    float = 0.0   # 0.0–N.   Count of flowers on this tile.
    biome:      str   = "wasteland"
    # biomes: "wasteland" | "meadow" | "forest" | "toxic" | "water"
```

---

## World

```python
class World:
    grid: list[list[Tile]]   # grid[y][x]
    width:  int
    height: int
```

Access pattern: `world.grid[y][x]` — row-major, y first.
Helper: `world.get_tile(x, y)` returns `None` if out of bounds.

---

## Bee (Entity)

```python
class Bee:
    x:        float           # pixel position
    y:        float           # pixel position
    target:   tuple | None    # (pixel_x, pixel_y) destination
    bee_type: str             # "worker" | "scout" | "guardian" | ...
    speed:    float = 100     # px/sec
    energy:   float = 1.0     # 0.0–1.0. Depletes with work, recharges at hive.
```

---

## Resources (global)

```python
class Resources:
    nectar:      float = 0.0   # Spent to spawn new bees
    pollen:      float = 0.0   # Spent to evolve bees
    hive_energy: float = 1.0   # Spent for special actions
```

---

## Ecological rules (EcosystemSystem)

These rules run every frame on every tile.

### Flower growth
```python
if tile.fertility > 0.5:
    tile.flowers += FLOWER_GROWTH_RATE * dt
```

### Pollution suppression
```python
if tile.pollution > 0.4:
    tile.flowers -= POLLUTION_DAMAGE_RATE * dt
    tile.fertility -= POLLUTION_FERTILITY_DAMAGE * dt

tile.flowers = max(0.0, tile.flowers)
tile.fertility = max(0.0, tile.fertility)
```

### Nectar production
```python
resources.nectar += tile.flowers * NECTAR_PER_FLOWER * dt
```

### Bee effect on tile (Worker)
While a Worker bee is targeting a tile:
```python
tile.fertility = min(1.0, tile.fertility + BEE_FERTILITY_BOOST * dt)
```

### Biome transition thresholds
```python
if tile.fertility > 0.6 and tile.pollution < 0.2:
    tile.biome = "meadow"
elif tile.fertility > 0.8 and tile.pollution < 0.1:
    tile.biome = "forest"
elif tile.pollution > 0.7:
    tile.biome = "toxic"
elif tile.biome not in ("water",):
    tile.biome = "wasteland"
```

### Pollution spread (ThreatSystem — add later)
```python
# Each toxic tile slowly corrupts its neighbours
for neighbour in get_neighbours(world, x, y):
    if tile.biome == "toxic":
        neighbour.pollution += SPREAD_RATE * dt
```

---

## Constants (config/constants.py)

```python
TILE_SIZE = 32
GRID_WIDTH = 20
GRID_HEIGHT = 15
SCREEN_WIDTH = GRID_WIDTH * TILE_SIZE    # 640
SCREEN_HEIGHT = GRID_HEIGHT * TILE_SIZE  # 480

BEE_SPEED = 100           # px/sec
BEE_FERTILITY_BOOST = 0.05
FLOWER_GROWTH_RATE = 0.01
POLLUTION_DAMAGE_RATE = 0.02
POLLUTION_FERTILITY_DAMAGE = 0.005
NECTAR_PER_FLOWER = 0.001
BEE_ENERGY_DRAIN = 0.05   # per second while active
BEE_ENERGY_RECHARGE = 0.2 # per second at hive

SPREAD_RATE = 0.001       # pollution spread per second
```

---

## Serialisation shape (for save files)

```json
{
  "resources": {
    "nectar": 42.0,
    "pollen": 10.0,
    "hive_energy": 0.8
  },
  "bees": [
    {"x": 100, "y": 120, "bee_type": "worker", "energy": 0.9}
  ],
  "world": {
    "width": 20,
    "height": 15,
    "tiles": [
      {"x": 0, "y": 0, "fertility": 0.4, "pollution": 0.3, "flowers": 1.2, "biome": "meadow"}
    ]
  }
}
```

Only save tiles that differ from default state to keep file size small.
