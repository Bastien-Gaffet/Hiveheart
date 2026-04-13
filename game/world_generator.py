from __future__ import annotations
from opensimplex import OpenSimplex
from game.tile import Tile
from game.chunk import Chunk
from config.constants import (
    CHUNK_SIZE,
    BIOME_WATER, BIOME_FOREST, BIOME_MEADOW, BIOME_TOXIC, BIOME_WASTELAND,
)


class WorldGenerator:
    """Génération procédurale via Simplex noise FBM à 3 couches indépendantes.

    Couche 1 (grande échelle, octaves=4, scale=0.003) → fertilité de base.
    Couche 2 (échelle moyenne, octaves=2, scale=0.015) → pollution / taches industrielles.
    Couche 3 (petite échelle, octaves=3, scale=0.025) → humidité / rivières.

    Les coordonnées wx/wy sont en espace monde absolu → bruit continu aux frontières de chunks.
    """

    def __init__(self, seed: int = 42) -> None:
        self._snx_fertility = OpenSimplex(seed)
        self._snx_pollution = OpenSimplex(seed + 1_000_003)
        self._snx_humidity  = OpenSimplex(seed + 2_000_003)

    def generate_chunk(self, cx: int, cy: int) -> Chunk:
        chunk = Chunk(cx, cy)
        ox = cx * CHUNK_SIZE
        oy = cy * CHUNK_SIZE
        for ly in range(CHUNK_SIZE):
            for lx in range(CHUNK_SIZE):
                chunk.grid[ly][lx] = self._generate_tile(ox + lx, oy + ly)
        return chunk

    # ------------------------------------------------------------------

    def _noise(self, gen: OpenSimplex, wx: int, wy: int,
               scale: float, octaves: int) -> float:
        """FBM (fractal Brownian motion) → [0, 1]."""
        v, amp, freq, total = 0.0, 1.0, 1.0, 0.0
        for _ in range(octaves):
            v     += gen.noise2(wx * scale * freq, wy * scale * freq) * amp
            total += amp
            amp   *= 0.5
            freq  *= 2.0
        return (v / total + 1.0) / 2.0   # remap [-1, 1] → [0, 1]

    def _generate_tile(self, wx: int, wy: int) -> Tile:
        fertility = self._noise(self._snx_fertility, wx, wy, scale=0.003, octaves=4)
        raw_poll  = self._noise(self._snx_pollution, wx, wy, scale=0.015, octaves=2)
        # Seuil pollution : la plupart des tiles restent propres, taches concentrées
        pollution = min(1.0, max(0.0, (raw_poll - 0.40) * (5.0 / 3.0)))
        humidity  = self._noise(self._snx_humidity,  wx, wy, scale=0.025, octaves=3)

        # La pollution supprime la fertilité
        fertility = max(0.0, fertility - pollution * 0.4)

        biome: str
        if humidity > 0.82:
            biome = BIOME_WATER
        elif pollution > 0.70:
            biome = BIOME_TOXIC
        elif fertility > 0.80 and pollution < 0.10:
            biome = BIOME_FOREST
        elif fertility > 0.60 and pollution < 0.20:
            biome = BIOME_MEADOW
        else:
            biome = BIOME_WASTELAND

        return Tile(
            fertility=round(fertility, 4),
            pollution=round(pollution, 4),
            humidity=round(humidity, 4),
            flowers=0.0,
            biome=biome,
            revealed=False,
        )
