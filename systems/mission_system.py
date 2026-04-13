from config.constants import BIOME_TOXIC, BIOME_WATER, BIOME_FOREST, BIOME_MEADOW
from game.world import World
from game.game_state import GameState
from game.mission import Mission


class MissionSystem:
    """Tracks biodiversity and toxic fraction; transitions GameState phase on win/lose.

    Must be added last to the game system list so it reads biome state after
    EcosystemSystem and ThreatSystem have already updated tiles this frame.
    """

    def __init__(self, world: World, state: GameState, mission: Mission) -> None:
        self._world   = world
        self._state   = state
        self._mission = mission

    def update(self, dt: float) -> None:
        if self._state.phase != "playing":
            return
        self._state.time_remaining = max(0.0, self._state.time_remaining - dt)
        self._recompute_scores()
        self._evaluate_conditions()

    def _recompute_scores(self) -> None:
        total = meadow = forest = toxic = 0
        for tile in self._world.iter_loaded_tiles():
                if tile.biome == BIOME_WATER:
                    continue
                total += 1
                if tile.biome == BIOME_FOREST:
                    forest += 1
                elif tile.biome == BIOME_MEADOW:
                    meadow += 1
                elif tile.biome == BIOME_TOXIC:
                    toxic += 1
        if total == 0:
            return
        # Forest tiles count double — a stricter ecological achievement than meadow
        self._state.biodiversity_score = (meadow + forest * 2) / (total * 2)
        self._state.toxic_fraction = toxic / total

    def _evaluate_conditions(self) -> None:
        if self._state.biodiversity_score >= self._mission.win_target:
            self._state.phase = "won"
        elif self._state.toxic_fraction >= self._mission.lose_toxic_fraction:
            self._state.phase = "lost"
        elif self._state.time_remaining <= 0.0:
            self._state.phase = "lost"
