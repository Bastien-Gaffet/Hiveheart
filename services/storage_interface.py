"""Interface de persistence par chunk.

Phase 10.5 : stub uniquement.
Phase 11 : local_storage.py (JSON par chunk).
Phase 12 : supabase_storage.py (cloud).

Seuls les chunks dont les tiles diffèrent de la génération initiale (deltas)
doivent être stockés — WorldGenerator(seed).generate_chunk(cx, cy) sert de base.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.chunk import Chunk


class StorageInterface:
    """Interface abstraite pour la persistence des chunks."""

    def save_chunk(self, seed: int, cx: int, cy: int, chunk: "Chunk") -> None:
        """Persiste les tiles d'un chunk (delta vs génération)."""
        raise NotImplementedError

    def load_chunk(self, seed: int, cx: int, cy: int) -> "Chunk | None":
        """Charge un chunk sauvegardé, ou None si non persisté.
        L'appelant retombe sur WorldGenerator en cas de None.
        """
        raise NotImplementedError

    def save_meta(self, seed: int, metadata: dict) -> None:
        """Sauvegarde les métadonnées de session (ressources, bees, caméra)."""
        raise NotImplementedError

    def load_meta(self, seed: int) -> dict | None:
        """Charge les métadonnées. None si aucune sauvegarde pour ce seed."""
        raise NotImplementedError
