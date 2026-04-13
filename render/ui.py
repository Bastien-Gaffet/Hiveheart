from __future__ import annotations

import pygame

from config.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, UI_PANEL_HEIGHT,
    UI_PANEL_COLOR, UI_PANEL_BORDER_COLOR, UI_FONT_COLOR,
    UI_FONT_SIZE_LARGE, UI_FONT_SIZE_SMALL,
    UI_BEE_SLOTS_X, UI_BEE_SLOT_SIZE, UI_BEE_SLOT_GAP, UI_BEE_SLOT_COLOR,
    UI_SPAWN_BTN_WIDTH, UI_SPAWN_BTN_COLOR_ON, UI_SPAWN_BTN_COLOR_OFF,
    BEE_SPAWN_COST, BEE_BODY_COLOR, BEE_SCOUT_COLOR, BEE_RADIUS,
    SCOUT_SPAWN_COST, BEE_TYPE_WORKER, BEE_TYPE_SCOUT,
    MISSION_SCORE_BAR_WIDTH, MISSION_SCORE_BAR_HEIGHT,
    MISSION_SCORE_BAR_COLOR, MISSION_SCORE_BAR_BG_COLOR,
    MISSION_TIMER_WARN_THRESHOLD, MISSION_TIMER_WARN_COLOR,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.resources import Resources
    from game.entity_registry import EntityRegistry
    from game.game_state import GameState
    from game.mission import Mission


class HUD:
    def __init__(
        self,
        screen: pygame.Surface,
        resources: Resources,
        registry: EntityRegistry,
        game_state: GameState,
        mission: Mission,
    ) -> None:
        self._screen      = screen
        self._resources   = resources
        self._registry    = registry
        self._game_state  = game_state
        self._mission     = mission
        self._panel_y     = SCREEN_HEIGHT - UI_PANEL_HEIGHT
        self._font_lg     = pygame.font.SysFont(None, UI_FONT_SIZE_LARGE)
        self._font_sm     = pygame.font.SysFont(None, UI_FONT_SIZE_SMALL)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def draw(self, mouse_pos: tuple[int, int]) -> None:
        self._draw_panel_bg()
        self._draw_nectar()
        self._draw_timer()
        self._draw_score_bar()
        self._draw_bee_slots(mouse_pos)
        self._draw_spawn_button()
        self._draw_scout_button()

    def bee_slot_index_at(self, pos: tuple[int, int]) -> int:
        """Return index into hive_bees list at screen pos, or -1."""
        x, y = pos
        hive_bees = [b for b in self._registry.bees if b.in_hive]
        cy = self._panel_y + UI_PANEL_HEIGHT // 2
        for i in range(len(hive_bees)):
            cx = UI_BEE_SLOTS_X + i * (UI_BEE_SLOT_SIZE + UI_BEE_SLOT_GAP)
            if abs(x - cx) <= UI_BEE_SLOT_SIZE // 2 and abs(y - cy) <= UI_BEE_SLOT_SIZE // 2:
                return i
        return -1

    def spawn_button_rect(self) -> pygame.Rect:
        return pygame.Rect(
            SCREEN_WIDTH - UI_SPAWN_BTN_WIDTH - 16,
            self._panel_y + 16,
            UI_SPAWN_BTN_WIDTH,
            UI_PANEL_HEIGHT - 32,
        )

    def scout_button_rect(self) -> pygame.Rect:
        return pygame.Rect(
            SCREEN_WIDTH - UI_SPAWN_BTN_WIDTH * 2 - 24,
            self._panel_y + 16,
            UI_SPAWN_BTN_WIDTH,
            UI_PANEL_HEIGHT - 32,
        )

    # ------------------------------------------------------------------
    # Private draw passes
    # ------------------------------------------------------------------

    def _draw_panel_bg(self) -> None:
        pygame.draw.rect(
            self._screen, UI_PANEL_COLOR,
            pygame.Rect(0, self._panel_y, SCREEN_WIDTH, UI_PANEL_HEIGHT),
        )
        pygame.draw.line(
            self._screen, UI_PANEL_BORDER_COLOR,
            (0, self._panel_y), (SCREEN_WIDTH, self._panel_y), 1,
        )

    def _draw_timer(self) -> None:
        secs = int(self._game_state.time_remaining)
        text = f"{secs // 60:02d}:{secs % 60:02d}"
        color = MISSION_TIMER_WARN_COLOR if self._game_state.time_remaining < MISSION_TIMER_WARN_THRESHOLD else UI_FONT_COLOR
        surf = self._font_lg.render(text, True, color)
        self._screen.blit(surf, (180, self._panel_y + (UI_PANEL_HEIGHT - surf.get_height()) // 2))

    def _draw_score_bar(self) -> None:
        bx = (SCREEN_WIDTH - MISSION_SCORE_BAR_WIDTH) // 2
        by = self._panel_y + (UI_PANEL_HEIGHT - MISSION_SCORE_BAR_HEIGHT) // 2
        pygame.draw.rect(self._screen, MISSION_SCORE_BAR_BG_COLOR,
                         (bx, by, MISSION_SCORE_BAR_WIDTH, MISSION_SCORE_BAR_HEIGHT))
        fill_w = int(self._game_state.biodiversity_score * MISSION_SCORE_BAR_WIDTH)
        if fill_w > 0:
            pygame.draw.rect(self._screen, MISSION_SCORE_BAR_COLOR,
                             (bx, by, fill_w, MISSION_SCORE_BAR_HEIGHT))
        target_x = bx + int(self._mission.win_target * MISSION_SCORE_BAR_WIDTH)
        pygame.draw.line(self._screen, (255, 255, 255),
                         (target_x, by), (target_x, by + MISSION_SCORE_BAR_HEIGHT), 1)

    def _draw_nectar(self) -> None:
        text = self._font_lg.render(
            f"Nectar  {self._resources.nectar:.1f}", True, UI_FONT_COLOR
        )
        self._screen.blit(
            text, (16, self._panel_y + (UI_PANEL_HEIGHT - text.get_height()) // 2)
        )

    def _draw_bee_slots(self, mouse_pos: tuple[int, int]) -> None:
        selected  = self._registry.selected_bee
        hive_bees = [b for b in self._registry.bees if b.in_hive]
        cy = self._panel_y + UI_PANEL_HEIGHT // 2
        for i, bee in enumerate(hive_bees):
            cx = UI_BEE_SLOTS_X + i * (UI_BEE_SLOT_SIZE + UI_BEE_SLOT_GAP)
            pygame.draw.circle(self._screen, UI_BEE_SLOT_COLOR, (cx, cy), UI_BEE_SLOT_SIZE // 2, 2)
            if bee is not selected:
                color = BEE_SCOUT_COLOR if bee.bee_type == BEE_TYPE_SCOUT else BEE_BODY_COLOR
                pygame.draw.circle(self._screen, color, (cx, cy), BEE_RADIUS)

    def _draw_spawn_button(self) -> None:
        can_afford = self._resources.nectar >= BEE_SPAWN_COST
        color = UI_SPAWN_BTN_COLOR_ON if can_afford else UI_SPAWN_BTN_COLOR_OFF
        rect  = self.spawn_button_rect()
        pygame.draw.rect(self._screen, color, rect, border_radius=6)
        label = self._font_sm.render(f"+ Worker ({int(BEE_SPAWN_COST)})", True, (255, 255, 255))
        lx = rect.x + (rect.width  - label.get_width())  // 2
        ly = rect.y + (rect.height - label.get_height()) // 2
        self._screen.blit(label, (lx, ly))

    def _draw_scout_button(self) -> None:
        can_afford = self._resources.nectar >= SCOUT_SPAWN_COST
        color = UI_SPAWN_BTN_COLOR_ON if can_afford else UI_SPAWN_BTN_COLOR_OFF
        rect  = self.scout_button_rect()
        pygame.draw.rect(self._screen, color, rect, border_radius=6)
        label = self._font_sm.render(f"+ Scout ({int(SCOUT_SPAWN_COST)})", True, (255, 255, 255))
        lx = rect.x + (rect.width  - label.get_width())  // 2
        ly = rect.y + (rect.height - label.get_height()) // 2
        self._screen.blit(label, (lx, ly))