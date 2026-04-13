import pygame


def draw_glow(
    screen: pygame.Surface,
    x: int,
    y: int,
    radius: int,
    color: tuple[int, int, int],
) -> None:
    """Fake radial glow via an SRCALPHA surface blitted with BLEND_ADD.
    Creates a soft quadratic falloff from the centre outward.
    """
    surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    for i in range(radius, 0, -1):
        alpha = int(255 * (i / radius) ** 2)
        pygame.draw.circle(surf, (*color, alpha), (radius, radius), i)
    screen.blit(surf, (x - radius, y - radius), special_flags=pygame.BLEND_ADD)
