"""Persistence JSON locale par chunk (Phase 11).

Structure :
    saves/{seed}/meta.json
    saves/{seed}/chunks/{cx}_{cy}.json   (uniquement les chunks avec deltas)

Stratégie delta : compare-at-save via WorldGenerator(seed).generate_chunk().
humidity est exclu (jamais muté par les systèmes).
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from config.constants import CHUNK_SIZE, SAVE_DIR
from game.chunk import Chunk
from game.world_generator import WorldGenerator
from services.storage_interface import StorageInterface

_MUTABLE_FIELDS = ("fertility", "pollution", "flowers", "biome", "revealed")


class LocalStorage(StorageInterface):

    def _seed_dir(self, seed: int) -> str:
        return os.path.join(SAVE_DIR, str(seed))

    def _chunks_dir(self, seed: int) -> str:
        return os.path.join(self._seed_dir(seed), "chunks")

    def _chunk_path(self, seed: int, cx: int, cy: int) -> str:
        return os.path.join(self._chunks_dir(seed), f"{cx}_{cy}.json")

    def _meta_path(self, seed: int) -> str:
        return os.path.join(self._seed_dir(seed), "meta.json")

    # ------------------------------------------------------------------

    def save_chunk(self, seed: int, cx: int, cy: int, chunk: Chunk) -> None:
        baseline = WorldGenerator(seed).generate_chunk(cx, cy)
        deltas = []
        for ly in range(CHUNK_SIZE):
            for lx in range(CHUNK_SIZE):
                cur = chunk.grid[ly][lx]
                ref = baseline.grid[ly][lx]
                if any(getattr(cur, f) != getattr(ref, f) for f in _MUTABLE_FIELDS):
                    deltas.append({
                        "lx": lx, "ly": ly,
                        "fertility": round(cur.fertility, 6),
                        "pollution": round(cur.pollution, 6),
                        "flowers": round(cur.flowers, 6),
                        "biome": cur.biome,
                        "revealed": cur.revealed,
                    })
        path = self._chunk_path(seed, cx, cy)
        if not deltas:
            if os.path.exists(path):
                os.remove(path)
            return
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"cx": cx, "cy": cy, "tile_deltas": deltas}, f, separators=(",", ":"))

    def load_chunk(self, seed: int, cx: int, cy: int) -> Chunk | None:
        path = self._chunk_path(seed, cx, cy)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            return None
        chunk = WorldGenerator(seed).generate_chunk(cx, cy)
        for d in data.get("tile_deltas", []):
            t = chunk.grid[d["ly"]][d["lx"]]
            t.fertility = d["fertility"]
            t.pollution = d["pollution"]
            t.flowers   = d["flowers"]
            t.biome     = d["biome"]
            t.revealed  = d["revealed"]
        return chunk

    def save_meta(self, seed: int, metadata: dict) -> None:
        os.makedirs(self._seed_dir(seed), exist_ok=True)
        metadata["seed"]     = seed
        metadata["saved_at"] = datetime.now(timezone.utc).isoformat()
        with open(self._meta_path(seed), "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

    def load_meta(self, seed: int) -> dict | None:
        path = self._meta_path(seed)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return None
