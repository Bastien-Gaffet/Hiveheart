from config.constants import BIOME_TOXIC, SPREAD_RATE
from game.world import World

_NEIGHBORS = ((-1, 0), (1, 0), (0, -1), (0, 1))


class ThreatSystem:
    """Spreads pollution outward from toxic tiles each frame.

    Toxic tiles (biome == BIOME_TOXIC) add SPREAD_RATE * dt pollution per second
    to each of their four cardinal neighbors. Non-toxic neighbors accumulate
    pollution until they too become toxic, creating a spreading threat the player
    must counter with Worker bees.
    """

    def __init__(self, world: World) -> None:
        self._world = world

    def update(self, dt: float) -> None:
        amount = SPREAD_RATE * dt
        world = self._world
        for tx, ty, tile in world.iter_loaded_tiles_with_coords():
            if tile.biome != BIOME_TOXIC:
                continue
            for dx, dy in _NEIGHBORS:
                neighbor = world.get_tile(tx + dx, ty + dy)
                if neighbor is not None and neighbor.biome != BIOME_TOXIC:
                    neighbor.pollution = min(1.0, neighbor.pollution + amount)
