import sys
import pygame

from config.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, CAMERA_PAN_SPEED, TILE_SIZE, UI_PANEL_HEIGHT,
    WORLD_SEED,
)
from core.game import Game
from core.settings import Settings
from game.world import World
from game.resources import Resources
from game.entity_registry import EntityRegistry
from game.game_state import GameState
from game.mission import Mission, MISSION_JARDIN_ABANDONNE
from entities.bee import Bee
from render.camera import Camera
from render.renderer import Renderer
from render.ui import HUD
from render.mission_overlay import MissionOverlay
from services.local_storage import LocalStorage
from systems.input_system import InputSystem
from systems.movement_system import MovementSystem
from systems.ecosystem_system import EcosystemSystem
from systems.threat_system import ThreatSystem
from systems.mission_system import MissionSystem


def _save_session(storage: LocalStorage, world: World, resources: Resources,
                  registry: EntityRegistry, camera: Camera) -> None:
    seed = world.seed
    for (cx, cy), chunk in world.loaded_chunks.items():
        storage.save_chunk(seed, cx, cy, chunk)
    meta = {
        "resources": {
            "nectar":      resources.nectar,
            "pollen":      resources.pollen,
            "hive_energy": resources.hive_energy,
        },
        "camera": {
            "offset_x": camera.offset_x,
            "offset_y": camera.offset_y,
            "zoom":     camera.zoom,
        },
        "bees": [
            {
                "x":        b.x,
                "y":        b.y,
                "bee_type": b.bee_type,
                "target":   list(b.target) if b.target else None,
                "speed":    b.speed,
                "energy":   b.energy,
                "in_hive":  b.in_hive,
            }
            for b in registry.bees
        ],
    }
    storage.save_meta(seed, meta)


def _build_session(screen: pygame.Surface, mission: Mission,
                   storage: LocalStorage) -> tuple:
    world    = World(seed=WORLD_SEED, storage=storage)
    registry = EntityRegistry()
    camera   = Camera()
    game     = Game()

    meta = storage.load_meta(WORLD_SEED)
    if meta is None:
        # Nouveau jeu : reveal de départ + bee initiale
        resources  = Resources(nectar=mission.start_nectar)
        r = mission.start_revealed_radius
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= r * r:
                    t = world.get_tile(dx, dy)
                    if t:
                        t.revealed = True
        camera.offset_x = -SCREEN_WIDTH  / (2.0 * camera.zoom)
        camera.offset_y = -(SCREEN_HEIGHT - UI_PANEL_HEIGHT) / (2.0 * camera.zoom)
        registry.add_bee(Bee(x=TILE_SIZE / 2, y=TILE_SIZE / 2))
    else:
        # Restauration depuis sauvegarde
        r = meta["resources"]
        resources = Resources(nectar=r["nectar"], pollen=r["pollen"],
                              hive_energy=r["hive_energy"])
        c = meta["camera"]
        camera.offset_x, camera.offset_y, camera.zoom = c["offset_x"], c["offset_y"], c["zoom"]
        for bd in meta.get("bees", []):
            b = Bee(x=bd["x"], y=bd["y"], bee_type=bd["bee_type"])
            b.target   = tuple(bd["target"]) if bd["target"] else None
            b.speed    = bd["speed"]
            b.energy   = bd["energy"]
            b.in_hive  = bd["in_hive"]
            registry.add_bee(b)

    game_state = GameState(time_remaining=mission.time_limit)

    hud              = HUD(screen, resources, registry, game_state, mission)
    input_system     = InputSystem(registry, camera, resources, hud)
    movement_system  = MovementSystem(registry)
    ecosystem_system = EcosystemSystem(world, resources, registry)
    threat_system    = ThreatSystem(world)
    mission_system   = MissionSystem(world, game_state, mission)  # last — reads final biome state

    for sys in (input_system, movement_system, ecosystem_system,
                threat_system, mission_system):
        game.add_system(sys)

    settings = Settings()
    renderer = Renderer(screen, world, registry, camera, settings)
    overlay  = MissionOverlay(screen)

    return game, game_state, input_system, camera, renderer, hud, overlay, world, resources, registry


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Hiveheart")
    clock   = pygame.time.Clock()
    mission = MISSION_JARDIN_ABANDONNE
    storage = LocalStorage()

    app_running = True
    while app_running:
        (game, game_state, input_system, camera, renderer,
         hud, overlay, world, resources, registry) = _build_session(screen, mission, storage)

        while True:
            dt = clock.tick(FPS) / 1000.0

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    _save_session(storage, world, resources, registry, camera)
                    app_running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        _save_session(storage, world, resources, registry, camera)
                        app_running = False
                    elif event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        _save_session(storage, world, resources, registry, camera)

            if not app_running:
                break

            overlay.handle_events(events, game_state)
            if game_state.restart_requested:
                break  # inner loop → outer loop rebuilds session

            if game_state.phase == "playing":
                input_system.handle_events(events)
                keys = pygame.key.get_pressed()
                pan = CAMERA_PAN_SPEED * dt / camera.zoom
                if keys[pygame.K_LEFT]  or keys[pygame.K_a]: camera.offset_x -= pan
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]: camera.offset_x += pan
                if keys[pygame.K_UP]    or keys[pygame.K_w]: camera.offset_y -= pan
                if keys[pygame.K_DOWN]  or keys[pygame.K_s]: camera.offset_y += pan
                game.update(dt)  # frozen on win/lose

            renderer.draw(dt)                    # always — world visible under overlay
            hud.draw(pygame.mouse.get_pos())
            overlay.draw(game_state)             # no-op while "playing"
            pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
