import random
import pygame
from config.constants import POLLEN_COLOR


def spawn_particle(particles: list[dict], x: float, y: float) -> None:
    particles.append({
        "x": x,
        "y": y,
        "vx": random.uniform(-20, 20),
        "vy": random.uniform(-30, -10),
        "life": 1.0,
    })


def update_particles(particles: list[dict], dt: float) -> None:
    for p in particles:
        p["x"] += p["vx"] * dt
        p["y"] += p["vy"] * dt
        p["life"] -= dt
    particles[:] = [p for p in particles if p["life"] > 0]


def draw_particles(screen: pygame.Surface, particles: list[dict]) -> None:
    for p in particles:
        r = max(1, int(p["life"] * 3))
        pygame.draw.circle(screen, POLLEN_COLOR, (int(p["x"]), int(p["y"])), r)
