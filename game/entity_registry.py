from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entities.bee import Bee


class EntityRegistry:
    """Shared container for all game entities.
    Passed to main.py, Renderer, and all systems — all share the same reference.
    TYPE_CHECKING guard prevents a runtime circular import (game/ ← entities/).
    """

    def __init__(self) -> None:
        self.bees: list[Bee] = []           # type: ignore[type-arg]
        self.selected_bee: Bee | None = None        # written by InputSystem, read by Renderer
        self.hover_tile: tuple[int, int] | None = None  # written by InputSystem, read by Renderer

    def add_bee(self, bee: Bee) -> None:
        self.bees.append(bee)

    def remove_bee(self, bee: Bee) -> None:
        if self.selected_bee is bee:
            self.selected_bee = None
        self.bees.remove(bee)
