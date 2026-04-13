# Visual & Rendering — Hiveheart

## Art direction

The visual contrast is the core emotional hook:
- **Dead world**: muted greys, dark browns, flat colours, no animation
- **Alive world**: saturated greens and yellows, particle effects, subtle motion, warmth

The player must see the transformation at a glance. No numbers needed — colour tells the story.

Style reference: semi-cartoon, slightly organic. Not pixel art. Not photorealistic.
Think: a hand-painted illustration that moves.

---

## Colour palette per biome

| Biome | Base colour | Accent |
|-------|------------|--------|
| wasteland | `(80, 70, 60)` | — |
| meadow | `(90, 170, 80)` | `(255, 220, 80)` flowers |
| forest | `(40, 120, 50)` | `(100, 220, 90)` canopy |
| toxic | `(100, 40, 110)` | `(180, 60, 200)` glow |
| water | `(40, 80, 160)` | `(120, 180, 255)` shimmer |

Tile colour must interpolate smoothly toward its biome target, not snap instantly.

### Dynamic colour formula (renderer)
```python
r = int(80 + tile.pollution * 120)
g = int(60 + tile.fertility * 180)
b = int(40 + tile.flowers * 80)
color = (clamp(r, 0, 255), clamp(g, 0, 255), clamp(b, 0, 255))
```

---

## Tile rendering

- Draw filled rect per tile with dynamic colour
- Draw thin dark border (`(0,0,0)` at alpha 30) to separate tiles
- Draw flower sprites (or circles in proto) on top when `tile.flowers > 0.2`

### Flower proto rendering
```python
if tile.flowers > 0.2:
    count = min(int(tile.flowers * 3), 5)
    for i in range(count):
        fx = tile_x + seeded_random_x(x, y, i)  # deterministic offset
        fy = tile_y + seeded_random_y(x, y, i)
        pygame.draw.circle(screen, (255, 200, 50), (fx, fy), 2)
```

Use a seeded RNG per tile so flowers don't jump every frame.

---

## Bee rendering

### Base shape (proto)
```python
offset_y = math.sin(time * 5 + bee.x * 0.05) * 3   # gentle bobbing
x, y = int(bee.x), int(bee.y + offset_y)

pygame.draw.circle(screen, (0, 0, 0), (x, y + 5), 6)          # drop shadow
pygame.draw.circle(screen, (255, 220, 50), (x, y), 6)          # body
pygame.draw.circle(screen, (255, 255, 150), (x, y), 10, 1)     # rim glow
```

### Glow (fake shader)
Renders a radial alpha gradient on a `SRCALPHA` surface, blitted with `BLEND_ADD`:

```python
def draw_glow(screen, x, y, radius, color):
    surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    for i in range(radius, 0, -1):
        alpha = int(255 * (i / radius) ** 2)
        pygame.draw.circle(surf, (*color, alpha), (radius, radius), i)
    screen.blit(surf, (x - radius, y - radius), special_flags=pygame.BLEND_ADD)
```

Call with: `draw_glow(screen, x, y, 20, (255, 200, 80))`

---

## Particle system (pollen)

Each particle: `{x, y, vx, vy, life}` — life goes from 1.0 to 0.0.

### Spawn
```python
def spawn_particle(particles, x, y):
    particles.append({
        "x": x, "y": y,
        "vx": random.uniform(-20, 20),
        "vy": random.uniform(-30, -10),
        "life": 1.0
    })
```

### Update & draw
```python
def update_particles(particles, dt):
    for p in particles:
        p["x"] += p["vx"] * dt
        p["y"] += p["vy"] * dt
        p["life"] -= dt
    particles[:] = [p for p in particles if p["life"] > 0]

def draw_particles(screen, particles):
    for p in particles:
        r = max(1, int(p["life"] * 3))
        pygame.draw.circle(screen, (255, 220, 100), (int(p["x"]), int(p["y"])), r)
```

Spawn particles when a bee is actively boosting a tile.

---

## Camera

```python
class Camera:
    x:    float = 0.0   # world-space offset
    y:    float = 0.0
    zoom: float = 1.0   # clamp to [0.5, 2.5]

    def world_to_screen(self, wx, wy) -> tuple:
        return (
            int((wx - self.x) * self.zoom),
            int((wy - self.y) * self.zoom)
        )

    def screen_to_world(self, sx, sy) -> tuple:
        return (
            sx / self.zoom + self.x,
            sy / self.zoom + self.y
        )
```

### Controls
- Arrow keys or WASD → pan (`camera.x += speed * dt`)
- Mouse wheel → zoom (`camera.zoom += event.y * 0.1`)

All `pygame.draw` calls must use `camera.world_to_screen()` for position.
Tile size on screen = `TILE_SIZE * camera.zoom`.

---

## HUD (UI)

### Nectar bar
```
[ Hive icon ]  Nectar: 42  [ Pollen: 10 ]
```
Drawn as a rounded rect panel at top-left, always in screen space (not affected by camera).

### Bee panel
Bottom panel: shows available bees in the hive. Player drags from here.
Each slot: small bee icon + count badge.

### Mission hint
Top-right: current objective in one line. Fades in on level start.

### Style rules
- Panel background: `(20, 20, 30)` with `border_radius=10`
- Text: white, `Arial 18–20px`
- Icons: simple circles/shapes in proto, sprites later
- No drop shadows on UI — keep it clean

---

## Animations (future)

Use `Animation` class with a list of pygame Surfaces (sprite frames):

```python
class Animation:
    def __init__(self, frames, fps=10):
        self.frames = frames
        self.fps = fps
        self.time = 0.0

    def update(self, dt):
        self.time += dt

    def current_frame(self) -> pygame.Surface:
        idx = int(self.time * self.fps) % len(self.frames)
        return self.frames[idx]
```

Attach an `Animation` to each `Bee` entity. Renderer calls `bee.animation.current_frame()`.

---

## Draw order (painter's algorithm)

1. Background fill (`(15, 15, 20)`)
2. Tiles (world layer)
3. Flowers on tiles
4. Pollen particles
5. Bee shadows
6. Bees + glow
7. UI (always on top, in screen space)
