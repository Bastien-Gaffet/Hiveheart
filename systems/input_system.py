from __future__ import annotations
import math
from typing import TYPE_CHECKING

from config.constants import (
    MOUSE_BUTTON_DOWN,
    MOUSE_BUTTON_UP,
    MOUSE_MOTION,
    MOUSE_WHEEL,
    BEE_RADIUS,
    TILE_SIZE,
    CAMERA_ZOOM_STEP,
    CAMERA_ZOOM_MIN,
    CAMERA_ZOOM_MAX,
    SCREEN_HEIGHT,
    UI_PANEL_HEIGHT,
    BEE_SPAWN_COST,
    SCOUT_SPAWN_COST,
    BEE_TYPE_SCOUT,
)

if TYPE_CHECKING:
    from render.camera import Camera
    from render.ui import HUD
    from game.entity_registry import EntityRegistry
    from game.resources import Resources
    from entities.bee import Bee


class InputSystem:
    """Handles player mouse input: bee selection, target assignment, and HUD interaction.

    Satisfies the System Protocol via update(dt).
    main.py calls handle_events(events) each frame BEFORE game.update(dt).

    No pygame import: event type constants come from config/constants.py;
    event attributes (.type, .button, .pos) are read via duck typing.
    """

    def __init__(
        self,
        registry: EntityRegistry,
        camera: Camera,
        resources: Resources,
        hud: HUD,
    ) -> None:
        self._registry  = registry
        self._camera    = camera
        self._resources = resources
        self._hud       = hud

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def handle_events(self, events: list) -> None:
        for event in events:
            if event.type == MOUSE_BUTTON_DOWN and event.button == 1:
                self._on_mouse_down(event.pos)
            elif event.type == MOUSE_BUTTON_UP and event.button == 1:
                self._on_mouse_up(event.pos)
            elif event.type == MOUSE_MOTION:
                self._on_mouse_motion(event.pos)
            elif event.type == MOUSE_WHEEL:
                self._camera.zoom = max(
                    CAMERA_ZOOM_MIN,
                    min(CAMERA_ZOOM_MAX, self._camera.zoom + event.y * CAMERA_ZOOM_STEP),
                )

    def update(self, dt: float) -> None:
        pass

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _on_mouse_down(self, screen_pos: tuple[int, int]) -> None:
        _, sy = screen_pos
        if sy >= SCREEN_HEIGHT - UI_PANEL_HEIGHT:
            self._on_panel_down(screen_pos)
        else:
            wx, wy = self._camera.screen_to_world(screen_pos[0], screen_pos[1])
            self._registry.selected_bee = self._bee_at(wx, wy)

    def _on_panel_down(self, screen_pos: tuple[int, int]) -> None:
        if self._hud.spawn_button_rect().collidepoint(screen_pos):
            if self._resources.nectar >= BEE_SPAWN_COST:
                from entities.bee import Bee
                self._resources.nectar -= BEE_SPAWN_COST
                self._registry.add_bee(Bee(x=0.0, y=0.0))
            return
        if self._hud.scout_button_rect().collidepoint(screen_pos):
            if self._resources.nectar >= SCOUT_SPAWN_COST:
                from entities.bee import Bee
                self._resources.nectar -= SCOUT_SPAWN_COST
                self._registry.add_bee(Bee(x=0.0, y=0.0, bee_type=BEE_TYPE_SCOUT))
            return
        idx = self._hud.bee_slot_index_at(screen_pos)
        if idx >= 0:
            hive_bees = [b for b in self._registry.bees if b.in_hive]
            self._registry.selected_bee = hive_bees[idx]

    def _on_mouse_up(self, screen_pos: tuple[int, int]) -> None:
        bee = self._registry.selected_bee
        if bee is None:
            return

        if bee.in_hive:
            _, sy = screen_pos
            if sy < SCREEN_HEIGHT - UI_PANEL_HEIGHT:
                # Deploy bee onto map
                wx, wy = self._camera.screen_to_world(screen_pos[0], screen_pos[1])
                tx = int(wx // TILE_SIZE)
                ty = int(wy // TILE_SIZE)
                bee.in_hive = False
                bee.x = tx * TILE_SIZE + TILE_SIZE / 2
                bee.y = ty * TILE_SIZE + TILE_SIZE / 2
                bee.target = (bee.x, bee.y)
            # else: dropped back on panel — deselect without deploying
            self._registry.selected_bee = None
            self._registry.hover_tile   = None
            return

        # Deployed bee: reassign target
        wx, wy = self._camera.screen_to_world(screen_pos[0], screen_pos[1])
        tx = int(wx // TILE_SIZE)
        ty = int(wy // TILE_SIZE)
        bee.target = (tx * TILE_SIZE + TILE_SIZE / 2, ty * TILE_SIZE + TILE_SIZE / 2)
        self._registry.hover_tile = None

    def _on_mouse_motion(self, screen_pos: tuple[int, int]) -> None:
        if self._registry.selected_bee is None:
            self._registry.hover_tile = None
            return
        _, sy = screen_pos
        if sy >= SCREEN_HEIGHT - UI_PANEL_HEIGHT:
            self._registry.hover_tile = None
            return
        wx, wy = self._camera.screen_to_world(screen_pos[0], screen_pos[1])
        tx, ty = int(wx // TILE_SIZE), int(wy // TILE_SIZE)
        self._registry.hover_tile = (tx, ty)

    def _bee_at(self, wx: float, wy: float) -> Bee | None:
        """Return the first deployed bee whose body circle contains (wx, wy)."""
        for bee in self._registry.bees:
            if bee.in_hive:
                continue
            if math.hypot(bee.x - wx, bee.y - wy) <= BEE_RADIUS:
                return bee
        return None
