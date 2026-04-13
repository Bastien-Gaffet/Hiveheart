from __future__ import annotations
from game.tile import Tile
from config.constants import CHUNK_SIZE


class Chunk:
    """Grille locale CHUNK_SIZE×CHUNK_SIZE de Tiles.

    Le tile monde (tx, ty) appartient au chunk (tx // CHUNK_SIZE, ty // CHUNK_SIZE)
    à l'index local (tx % CHUNK_SIZE, ty % CHUNK_SIZE).
    """

    def __init__(self, cx: int, cy: int) -> None:
        self.cx: int = cx
        self.cy: int = cy
        self.grid: list[list[Tile]] = [
            [Tile() for _ in range(CHUNK_SIZE)]
            for _ in range(CHUNK_SIZE)
        ]
        self.dirty: bool = False  # True si une tile a été mutée depuis la génération

    def get_local(self, lx: int, ly: int) -> Tile:
        return self.grid[ly][lx]

    def iter_tiles(self):
        for row in self.grid:
            yield from row

    def iter_tiles_with_coords(self):
        ox = self.cx * CHUNK_SIZE
        oy = self.cy * CHUNK_SIZE
        for ly, row in enumerate(self.grid):
            for lx, tile in enumerate(row):
                yield ox + lx, oy + ly, tile
