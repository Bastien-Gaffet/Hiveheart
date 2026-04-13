import math
import random
import pygame

from render.camera import Camera
from render.effects import draw_glow
from render.particle_system import spawn_particle, update_particles, draw_particles
from core.settings import Settings
from game.world import World
from game.entity_registry import EntityRegistry
from config.constants import (
    TILE_SIZE,
    CHUNK_SIZE, CHUNK_LOAD_RADIUS,
    SCREEN_WIDTH, SCREEN_HEIGHT, UI_PANEL_HEIGHT,
    BEE_TYPE_WORKER,
    BEE_BODY_COLOR, BEE_SCOUT_COLOR, BEE_GLOW_COLOR, BEE_SHADOW_COLOR,
    FOG_COLOR,
    BIOME_TOXIC,
    TOXIC_PULSE_COLOR, TOXIC_PULSE_ALPHA_BASE, TOXIC_PULSE_ALPHA_AMP, TOXIC_PULSE_SPEED,
    BEE_RADIUS, BEE_GLOW_RADIUS, BEE_SHADOW_DROP,
    BEE_BOB_SPEED, BEE_BOB_AMP, BEE_BOB_PHASE,
    BEE_SELECT_COLOR, BEE_SELECT_RADIUS, BEE_SELECT_WIDTH,
    BEE_GLOW_EFFECT_RADIUS, BEE_GLOW_EFFECT_COLOR,
    HOVER_BORDER_COLOR, HOVER_BORDER_ALPHA, HOVER_BORDER_WIDTH,
    TARGET_MARKER_COLOR, TARGET_MARKER_BASE_RADIUS,
    TARGET_MARKER_PULSE_AMP, TARGET_MARKER_PULSE_SPEED, TARGET_MARKER_WIDTH,
    FLOWER_DOT_COLOR, FLOWER_DOT_RADIUS, FLOWER_MAX_COUNT,
    POLLEN_SPAWN_RATE,
    TILE_COLOR_LERP_SPEED,
    TILE_R_BASE, TILE_R_POLL,
    TILE_G_BASE, TILE_G_FERT,
    TILE_B_BASE, TILE_B_FLOW,
)

_BORDER_COLOR = (0, 0, 0)
_GAME_HEIGHT  = SCREEN_HEIGHT - UI_PANEL_HEIGHT


def _tile_color(tile) -> tuple[int, int, int]:
    r = int(TILE_R_BASE + tile.pollution * TILE_R_POLL)
    g = int(TILE_G_BASE + tile.fertility * TILE_G_FERT)
    b = int(TILE_B_BASE + tile.flowers   * TILE_B_FLOW)
    return (
        max(0, min(255, r)),
        max(0, min(255, g)),
        max(0, min(255, b)),
    )


class Renderer:
    def __init__(
        self,
        screen: pygame.Surface,
        world: World,
        entity_registry: EntityRegistry,
        camera: Camera,
        settings: Settings | None = None,
    ) -> None:
        self.screen = screen
        self.world = world
        self.entity_registry = entity_registry
        self.camera = camera
        self.settings: Settings = settings or Settings()
        self.time: float = 0.0

        # Particle state — owned by renderer, all visual
        self.particles: list[dict] = []
        self._particle_timers: dict[int, float] = {}  # bee.id → time accumulator

        # Per-tile display colour — lazy dict, grows as tiles are first drawn
        self._display_colors: dict[tuple[int, int], list[float]] = {}

    # ------------------------------------------------------------------
    # Main draw entry point
    # ------------------------------------------------------------------

    def draw(self, dt: float) -> None:
        self.time += dt

        # Preload chunks around camera centre before any tile access
        cam = self.camera
        cam_cx = int(cam.offset_x + SCREEN_WIDTH  / cam.zoom / 2) // (CHUNK_SIZE * TILE_SIZE)
        cam_cy = int(cam.offset_y + _GAME_HEIGHT   / cam.zoom / 2) // (CHUNK_SIZE * TILE_SIZE)
        self.world.ensure_chunks_around(cam_cx, cam_cy, CHUNK_LOAD_RADIUS)

        self.screen.fill((15, 15, 20))
        self._draw_world(dt)
        self._draw_toxic_pulse()
        self._draw_hover_highlight()
        self._draw_flowers()
        if self.settings.show_pollen_particles:
            self._update_and_draw_particles(dt)
        if self.settings.show_target_marker:
            self._draw_target_markers()
        self._draw_bees()

    # ------------------------------------------------------------------
    # Viewport helper
    # ------------------------------------------------------------------

    def _visible_tile_range(self) -> tuple[int, int, int, int]:
        """Retourne (tx_min, ty_min, tx_max, ty_max) des tiles visibles + marge 1."""
        cam = self.camera
        m   = 1
        tx_min = int(cam.offset_x // TILE_SIZE) - m
        ty_min = int(cam.offset_y // TILE_SIZE) - m
        tx_max = int((cam.offset_x + SCREEN_WIDTH  / cam.zoom) // TILE_SIZE) + m + 1
        ty_max = int((cam.offset_y + _GAME_HEIGHT   / cam.zoom) // TILE_SIZE) + m + 1
        return tx_min, ty_min, tx_max, ty_max

    # ------------------------------------------------------------------
    # Draw passes
    # ------------------------------------------------------------------

    def _draw_world(self, dt: float) -> None:
        tw       = max(1, int(TILE_SIZE * self.camera.zoom))
        lerp_spd = TILE_COLOR_LERP_SPEED * dt
        tx_min, ty_min, tx_max, ty_max = self._visible_tile_range()

        for ty in range(ty_min, ty_max):
            for tx in range(tx_min, tx_max):
                tile   = self.world.get_tile(tx, ty)
                target = _tile_color(tile)
                key    = (tx, ty)

                if key not in self._display_colors:
                    self._display_colors[key] = [float(target[0]),
                                                  float(target[1]),
                                                  float(target[2])]
                dc = self._display_colors[key]

                if self.settings.show_tile_transitions:
                    dc[0] += (target[0] - dc[0]) * lerp_spd
                    dc[1] += (target[1] - dc[1]) * lerp_spd
                    dc[2] += (target[2] - dc[2]) * lerp_spd
                    color = (int(dc[0]), int(dc[1]), int(dc[2]))
                else:
                    color = target

                sx, sy = self.camera.world_to_screen(tx * TILE_SIZE, ty * TILE_SIZE)
                rect   = pygame.Rect(int(sx), int(sy), tw, tw)
                if not tile.revealed:
                    pygame.draw.rect(self.screen, FOG_COLOR, rect)
                    continue
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, _BORDER_COLOR, rect, 1)

    def _draw_toxic_pulse(self) -> None:
        alpha = int(TOXIC_PULSE_ALPHA_BASE + TOXIC_PULSE_ALPHA_AMP * math.sin(self.time * TOXIC_PULSE_SPEED))
        tw    = max(1, int(TILE_SIZE * self.camera.zoom))
        surf  = pygame.Surface((tw, tw), pygame.SRCALPHA)
        pygame.draw.rect(surf, (*TOXIC_PULSE_COLOR, alpha), surf.get_rect())
        tx_min, ty_min, tx_max, ty_max = self._visible_tile_range()
        for ty in range(ty_min, ty_max):
            for tx in range(tx_min, tx_max):
                tile = self.world.get_tile(tx, ty)
                if tile.revealed and tile.biome == BIOME_TOXIC:
                    sx, sy = self.camera.world_to_screen(tx * TILE_SIZE, ty * TILE_SIZE)
                    self.screen.blit(surf, (int(sx), int(sy)))

    def _draw_hover_highlight(self) -> None:
        hover = self.entity_registry.hover_tile
        if hover is None:
            return
        tx, ty = hover
        if not self.world.get_tile(tx, ty).revealed:
            return
        tw = max(1, int(TILE_SIZE * self.camera.zoom))
        sx, sy = self.camera.world_to_screen(tx * TILE_SIZE, ty * TILE_SIZE)
        surf = pygame.Surface((tw, tw), pygame.SRCALPHA)
        pygame.draw.rect(
            surf,
            (*HOVER_BORDER_COLOR, HOVER_BORDER_ALPHA),
            surf.get_rect(),
            HOVER_BORDER_WIDTH,
        )
        self.screen.blit(surf, (int(sx), int(sy)))

    def _draw_flowers(self) -> None:
        tw = max(1, int(TILE_SIZE * self.camera.zoom))
        tx_min, ty_min, tx_max, ty_max = self._visible_tile_range()
        for ty in range(ty_min, ty_max):
            for tx in range(tx_min, tx_max):
                tile = self.world.get_tile(tx, ty)
                if not tile.revealed or tile.flowers <= 0.2:
                    continue
                count = min(int(tile.flowers * 3), FLOWER_MAX_COUNT)
                sx, sy = self.camera.world_to_screen(tx * TILE_SIZE, ty * TILE_SIZE)
                rng = random.Random(tx * 10000 + ty * 100)
                for _ in range(count):
                    fx = int(sx) + int(rng.random() * tw)
                    fy = int(sy) + int(rng.random() * tw)
                    pygame.draw.circle(self.screen, FLOWER_DOT_COLOR, (fx, fy), FLOWER_DOT_RADIUS)

    def _update_and_draw_particles(self, dt: float) -> None:
        interval = 1.0 / POLLEN_SPAWN_RATE
        for bee in self.entity_registry.bees:
            if bee.bee_type != BEE_TYPE_WORKER or bee.target is None:
                continue
            timer = self._particle_timers.get(bee.id, 0.0) + dt
            while timer >= interval:
                sx, sy = self.camera.world_to_screen(bee.x, bee.y)
                spawn_particle(self.particles, sx, sy)
                timer -= interval
            self._particle_timers[bee.id] = timer

        update_particles(self.particles, dt)
        draw_particles(self.screen, self.particles)

    def _draw_target_markers(self) -> None:
        pulse  = math.sin(self.time * TARGET_MARKER_PULSE_SPEED) * TARGET_MARKER_PULSE_AMP
        radius = max(1, int(TARGET_MARKER_BASE_RADIUS + pulse))
        for bee in self.entity_registry.bees:
            if bee.target is None:
                continue
            sx, sy = self.camera.world_to_screen(bee.target[0], bee.target[1])
            pygame.draw.circle(
                self.screen, TARGET_MARKER_COLOR, (int(sx), int(sy)), radius, TARGET_MARKER_WIDTH,
            )

    def _draw_bees(self) -> None:
        mouse_pos = pygame.mouse.get_pos()
        for bee in self.entity_registry.bees:
            body_color = BEE_SCOUT_COLOR if bee.bee_type != BEE_TYPE_WORKER else BEE_BODY_COLOR
            if bee.in_hive:
                if bee is self.entity_registry.selected_bee:
                    bx, by = mouse_pos
                    draw_glow(self.screen, bx, by, BEE_GLOW_EFFECT_RADIUS, BEE_GLOW_EFFECT_COLOR)
                    pygame.draw.circle(self.screen, body_color, (bx, by), BEE_RADIUS)
                continue

            offset_y = math.sin(self.time * BEE_BOB_SPEED + bee.x * BEE_BOB_PHASE) * BEE_BOB_AMP
            sx, sy   = self.camera.world_to_screen(bee.x, bee.y + offset_y)
            bx, by   = int(sx), int(sy)

            pygame.draw.circle(self.screen, BEE_SHADOW_COLOR, (bx, by + BEE_SHADOW_DROP), BEE_RADIUS)
            draw_glow(self.screen, bx, by, BEE_GLOW_EFFECT_RADIUS, BEE_GLOW_EFFECT_COLOR)
            pygame.draw.circle(self.screen, body_color, (bx, by), BEE_RADIUS)
            pygame.draw.circle(self.screen, BEE_GLOW_COLOR, (bx, by), BEE_GLOW_RADIUS, 1)

            if bee is self.entity_registry.selected_bee:
                pygame.draw.circle(self.screen, BEE_SELECT_COLOR, (bx, by), BEE_SELECT_RADIUS, BEE_SELECT_WIDTH)
