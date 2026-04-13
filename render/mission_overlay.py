import pygame

from config.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    MOUSE_BUTTON_DOWN,
    MISSION_OVERLAY_BG_COLOR, MISSION_OVERLAY_BG_ALPHA,
    MISSION_WIN_COLOR, MISSION_LOSE_COLOR,
    MISSION_TITLE_FONT_SIZE, MISSION_BODY_FONT_SIZE,
    MISSION_BTN_WIDTH, MISSION_BTN_HEIGHT, MISSION_BTN_COLOR, MISSION_BTN_FONT_SIZE,
)


class MissionOverlay:
    """Draws win/lose screen on top of the world and handles restart button clicks.

    draw() is a no-op while game_state.phase == "playing".
    handle_events() sets game_state.restart_requested when the button is clicked.
    """

    def __init__(self, screen: pygame.Surface) -> None:
        self._screen      = screen
        self._font_title  = pygame.font.SysFont(None, MISSION_TITLE_FONT_SIZE)
        self._font_body   = pygame.font.SysFont(None, MISSION_BODY_FONT_SIZE)
        self._font_btn    = pygame.font.SysFont(None, MISSION_BTN_FONT_SIZE)
        self._bg          = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self._bg.fill((*MISSION_OVERLAY_BG_COLOR, MISSION_OVERLAY_BG_ALPHA))
        self._restart_btn_rect: pygame.Rect | None = None

    def draw(self, game_state) -> None:
        if game_state.phase == "playing":
            return

        self._screen.blit(self._bg, (0, 0))

        won        = game_state.phase == "won"
        title_text = "Victoire !" if won else "Défaite"
        title_color = MISSION_WIN_COLOR if won else MISSION_LOSE_COLOR

        cx = SCREEN_WIDTH  // 2
        cy = SCREEN_HEIGHT // 2

        title = self._font_title.render(title_text, True, title_color)
        self._screen.blit(title, (cx - title.get_width() // 2, cy - 100))

        score_pct = int(game_state.biodiversity_score * 100)
        body = self._font_body.render(f"Biodiversité : {score_pct}%", True, (200, 200, 200))
        self._screen.blit(body, (cx - body.get_width() // 2, cy - 40))

        if not won:
            tox = self._font_body.render(
                f"Pollution : {int(game_state.toxic_fraction * 100)}% du territoire",
                True, (200, 120, 100),
            )
            self._screen.blit(tox, (cx - tox.get_width() // 2, cy))

        btn_rect = pygame.Rect(cx - MISSION_BTN_WIDTH // 2, cy + 60,
                               MISSION_BTN_WIDTH, MISSION_BTN_HEIGHT)
        pygame.draw.rect(self._screen, MISSION_BTN_COLOR, btn_rect, border_radius=8)
        label = self._font_btn.render("Rejouer", True, (255, 255, 255))
        self._screen.blit(label, (
            btn_rect.x + (btn_rect.width  - label.get_width())  // 2,
            btn_rect.y + (btn_rect.height - label.get_height()) // 2,
        ))
        self._restart_btn_rect = btn_rect

    def handle_events(self, events: list, game_state) -> None:
        if game_state.phase == "playing" or self._restart_btn_rect is None:
            return
        for event in events:
            if event.type == MOUSE_BUTTON_DOWN and event.button == 1:
                if self._restart_btn_rect.collidepoint(event.pos):
                    game_state.restart_requested = True
