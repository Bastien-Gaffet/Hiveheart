from entities.entity import Entity
from config.constants import BEE_SPEED, BEE_TYPE_WORKER


class Bee(Entity):
    def __init__(self, x: float, y: float, bee_type: str = BEE_TYPE_WORKER) -> None:
        super().__init__(x, y)
        self.bee_type: str = bee_type
        self.target: tuple[float, float] | None = None
        self.speed: float = BEE_SPEED
        self.energy: float = 1.0
        self.in_hive: bool = True
