import math
from game.entity_registry import EntityRegistry

_STOP_DISTANCE = 2.0  # px — bee snaps to target within this radius


class MovementSystem:
    def __init__(self, registry: EntityRegistry) -> None:
        self._registry = registry

    def update(self, dt: float) -> None:
        for bee in self._registry.bees:
            if bee.in_hive or bee.target is None:
                continue
            tx, ty = bee.target
            dx, dy = tx - bee.x, ty - bee.y
            dist = math.hypot(dx, dy)
            if dist <= _STOP_DISTANCE:
                bee.x, bee.y = tx, ty
                # target intentionnellement conservé : l'abeille "travaille" cette tile
                # EcosystemSystem boost la fertilité tant que bee.target is not None
            else:
                step = bee.speed * dt
                bee.x += dx / dist * step
                bee.y += dy / dist * step
