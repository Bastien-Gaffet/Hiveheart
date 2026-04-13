from config.constants import (
    CAMERA_DEFAULT_OFFSET_X,
    CAMERA_DEFAULT_OFFSET_Y,
    CAMERA_DEFAULT_ZOOM,
)


class Camera:
    """Converts between world coordinates and screen coordinates.

    Phase 3: identity transform (offset 0, zoom 1).
    Phase 6 will add pan (arrow keys) and zoom (scroll wheel) by mutating
    offset_x/y and zoom — the formulas here stay unchanged.
    """

    def __init__(self) -> None:
        self.offset_x: float = CAMERA_DEFAULT_OFFSET_X
        self.offset_y: float = CAMERA_DEFAULT_OFFSET_Y
        self.zoom:     float = CAMERA_DEFAULT_ZOOM

    def world_to_screen(self, wx: float, wy: float) -> tuple[float, float]:
        return (wx - self.offset_x) * self.zoom, (wy - self.offset_y) * self.zoom

    def screen_to_world(self, sx: float, sy: float) -> tuple[float, float]:
        return sx / self.zoom + self.offset_x, sy / self.zoom + self.offset_y
