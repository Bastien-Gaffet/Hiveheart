from config.constants import (
    TILE_SIZE,
    BEE_TYPE_WORKER,
    BEE_TYPE_SCOUT,
    BEE_FERTILITY_BOOST,
    FLOWER_GROWTH_RATE,
    POLLUTION_DAMAGE_RATE,
    POLLUTION_FERTILITY_DAMAGE,
    NECTAR_PER_FLOWER,
    BIOME_WATER,
    BIOME_FOREST,
    BIOME_MEADOW,
    BIOME_TOXIC,
    BIOME_WASTELAND,
    SCOUT_REVEAL_RADIUS,
)
from game.world import World
from game.resources import Resources
from game.entity_registry import EntityRegistry


class EcosystemSystem:
    def __init__(self, world: World, resources: Resources, registry: EntityRegistry) -> None:
        self._world     = world
        self._resources = resources
        self._registry  = registry

    def update(self, dt: float) -> None:
        self._apply_bee_effects(dt)
        self._tick_tiles(dt)

    # ------------------------------------------------------------------

    def _apply_bee_effects(self, dt: float) -> None:
        for bee in self._registry.bees:
            if bee.in_hive:
                continue
            if bee.bee_type == BEE_TYPE_WORKER and bee.target is not None:
                gx = int(bee.target[0] // TILE_SIZE)
                gy = int(bee.target[1] // TILE_SIZE)
                tile = self._world.get_tile(gx, gy)
                if tile is not None:
                    tile.fertility = min(1.0, tile.fertility + BEE_FERTILITY_BOOST * dt)
            elif bee.bee_type == BEE_TYPE_SCOUT:
                self._reveal_around(bee.x, bee.y)

    def _reveal_around(self, px: float, py: float) -> None:
        cx = int(px // TILE_SIZE)
        cy = int(py // TILE_SIZE)
        r2 = SCOUT_REVEAL_RADIUS * SCOUT_REVEAL_RADIUS
        for dy in range(-SCOUT_REVEAL_RADIUS, SCOUT_REVEAL_RADIUS + 1):
            for dx in range(-SCOUT_REVEAL_RADIUS, SCOUT_REVEAL_RADIUS + 1):
                if dx * dx + dy * dy <= r2:
                    tile = self._world.get_tile(cx + dx, cy + dy)
                    if tile is not None:
                        tile.revealed = True

    def _tick_tiles(self, dt: float) -> None:
        for tile in self._world.iter_loaded_tiles():
                # Flower growth
                if tile.fertility > 0.5:
                    tile.flowers += FLOWER_GROWTH_RATE * dt

                # Pollution suppression
                if tile.pollution > 0.4:
                    tile.flowers   -= POLLUTION_DAMAGE_RATE * dt
                    tile.fertility -= POLLUTION_FERTILITY_DAMAGE * dt

                tile.flowers   = max(0.0, tile.flowers)
                tile.fertility = max(0.0, tile.fertility)

                # Nectar accumulation
                self._resources.nectar += tile.flowers * NECTAR_PER_FLOWER * dt

                # Biome transitions — forest checked before meadow (stricter subset)
                if tile.biome == BIOME_WATER:
                    pass
                elif tile.fertility > 0.8 and tile.pollution < 0.1:
                    tile.biome = BIOME_FOREST
                elif tile.fertility > 0.6 and tile.pollution < 0.2:
                    tile.biome = BIOME_MEADOW
                elif tile.pollution > 0.7:
                    tile.biome = BIOME_TOXIC
                else:
                    tile.biome = BIOME_WASTELAND
