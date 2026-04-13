from __future__ import annotations
from typing import TYPE_CHECKING
from game.tile import Tile
from game.chunk import Chunk
from game.world_generator import WorldGenerator
from config.constants import TILE_SIZE, CHUNK_SIZE

if TYPE_CHECKING:
    from services.storage_interface import StorageInterface


class World:
    """Monde infini basé sur des chunks de CHUNK_SIZE×CHUNK_SIZE tiles.

    API publique (signature inchangée) :
        get_tile(tx, ty)                → Tile | None  (génère le chunk si absent)
        get_tile_at_pixel(px, py)       → Tile | None
        iter_loaded_tiles()             → Iterator[Tile]
        iter_loaded_tiles_with_coords() → Iterator[tuple[int, int, Tile]]
        loaded_chunks                   → dict[(cx, cy), Chunk]  (lecture seule)
        ensure_chunks_around(cx, cy, r) → précharge + évacue chunks hors rayon

    Supprimé : world.width, world.height, world.grid
    """

    def __init__(self, seed: int = 42, storage: "StorageInterface | None" = None) -> None:
        self._seed      = seed
        self._generator = WorldGenerator(seed)
        self._chunks: dict[tuple[int, int], Chunk] = {}
        self._storage   = storage

    @property
    def seed(self) -> int:
        return self._seed

    # ------------------------------------------------------------------
    # Gestion des chunks
    # ------------------------------------------------------------------

    def _get_or_generate(self, cx: int, cy: int) -> Chunk:
        key = (cx, cy)
        if key not in self._chunks:
            chunk = None
            if self._storage is not None:
                chunk = self._storage.load_chunk(self._seed, cx, cy)
            if chunk is None:
                chunk = self._generator.generate_chunk(cx, cy)
            self._chunks[key] = chunk
        return self._chunks[key]

    def ensure_chunks_around(self, camera_cx: int, camera_cy: int, radius: int) -> None:
        """Précharge les chunks dans le rayon; évacue ceux hors rayon."""
        required: set[tuple[int, int]] = {
            (camera_cx + dx, camera_cy + dy)
            for dy in range(-radius, radius + 1)
            for dx in range(-radius, radius + 1)
        }
        for key in required:
            if key not in self._chunks:
                self._get_or_generate(*key)
        for key in list(self._chunks):
            if key not in required:
                del self._chunks[key]

    @property
    def loaded_chunks(self) -> dict[tuple[int, int], Chunk]:
        return self._chunks

    # ------------------------------------------------------------------
    # API publique tiles (signature identique à l'ancienne World)
    # ------------------------------------------------------------------

    def get_tile(self, tx: int, ty: int) -> Tile | None:
        # // et % sont corrects pour les coordonnées négatives en Python
        cx, cy = tx // CHUNK_SIZE, ty // CHUNK_SIZE
        lx, ly = tx % CHUNK_SIZE,  ty % CHUNK_SIZE
        return self._get_or_generate(cx, cy).get_local(lx, ly)

    def get_tile_at_pixel(self, px: float, py: float) -> Tile | None:
        return self.get_tile(int(px // TILE_SIZE), int(py // TILE_SIZE))

    # ------------------------------------------------------------------
    # Itérateurs (remplacent world.grid)
    # ------------------------------------------------------------------

    def iter_loaded_tiles(self):
        """Yields chaque Tile dans tous les chunks chargés.
        Snapshot les chunks pour éviter un RuntimeError si get_tile() génère un chunk pendant l'itération.
        """
        for chunk in list(self._chunks.values()):
            yield from chunk.iter_tiles()

    def iter_loaded_tiles_with_coords(self):
        """Yields (tx, ty, tile) pour tous les tiles chargés."""
        for chunk in list(self._chunks.values()):
            yield from chunk.iter_tiles_with_coords()
