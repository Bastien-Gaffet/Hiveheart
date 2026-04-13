from dataclasses import dataclass


@dataclass
class Mission:
    name: str
    time_limit: float           # seconds
    win_target: float           # biodiversity_score threshold (0–1)
    lose_toxic_fraction: float  # fraction of non-water tiles toxic that triggers loss
    start_nectar: float
    start_revealed_radius: int  # tiles revealed around centre at session start


MISSION_JARDIN_ABANDONNE = Mission(
    name="Jardin abandonné",
    time_limit=600.0,
    win_target=0.25,
    lose_toxic_fraction=0.60,
    start_nectar=25.0,
    start_revealed_radius=4,
)
