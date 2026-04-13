class Entity:
    _next_id: int = 0

    def __init__(self, x: float, y: float) -> None:
        self.id: int = Entity._next_id
        Entity._next_id += 1
        self.x: float = x
        self.y: float = y
