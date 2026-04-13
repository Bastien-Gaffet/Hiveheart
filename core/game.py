from typing import Protocol


class System(Protocol):
    def update(self, dt: float) -> None: ...


class Game:
    """Owns the active systems list. Calls system.update(dt) every frame.
    Knows nothing about pygame, rendering, or specific game rules.
    """

    def __init__(self) -> None:
        self.systems: list[System] = []

    def add_system(self, system: System) -> None:
        self.systems.append(system)

    def update(self, dt: float) -> None:
        for system in self.systems:
            system.update(dt)
