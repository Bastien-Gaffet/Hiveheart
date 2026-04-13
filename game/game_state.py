from dataclasses import dataclass
from typing import Literal

GamePhase = Literal["playing", "won", "lost"]


@dataclass
class GameState:
    phase: GamePhase = "playing"
    time_remaining: float = 0.0      # countdown in seconds; initialised from mission.time_limit
    biodiversity_score: float = 0.0  # 0–1, recomputed each frame by MissionSystem
    toxic_fraction: float = 0.0      # 0–1, recomputed each frame by MissionSystem
    restart_requested: bool = False
