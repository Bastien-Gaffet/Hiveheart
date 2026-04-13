# Hiveheart — Claude Code Context

This is the primary context file for Claude Code working on Hiveheart, a god game about bees restoring ecosystems.

## Quick orientation

- **Language**: Python 3.11+
- **Renderer**: Pygame
- **Architecture**: ECS-inspired (Systems, Entities, World) — NOT monolithic
- **Storage**: abstracted behind `services/storage_interface.py` (no direct Firebase calls in game code)
- **Entry point**: `main.py`

## Project files

| File | Purpose |
|------|---------|
| [GAME_DESIGN.md](docs/GAME_DESIGN.md) | Full GDD — mechanics, bee types, threats, objectives |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | File structure, module roles, dependency rules |
| [DATA_MODEL.md](docs/DATA_MODEL.md) | Tile, Bee, World, Resources data structures and rules |
| [DEV_PLAN.md](docs/DEV_PLAN.md) | Ordered implementation steps, what is done vs. todo |
| [VISUAL.md](docs/VISUAL.md) | Rendering approach, fake shaders, camera, UI style |

## Hard rules (never break these)

1. Game logic (`game/`, `entities/`, `systems/`) must never import `pygame`
2. Renderer must never modify game state
3. Storage calls go through `services/storage_interface.py` only — never call Firebase/SQLite directly from game code
4. Keep systems single-responsibility: one system = one concern

## Current status

Proto phase — validating core gameplay loop before adding polish.
See [DEV_PLAN.md](docs/DEV_PLAN.md) for what is built and what is next.
