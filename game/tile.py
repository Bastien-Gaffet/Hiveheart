from dataclasses import dataclass
from config.constants import BIOME_WASTELAND


@dataclass
class Tile:
    fertility:  float = 0.2
    pollution:  float = 0.5
    humidity:   float = 0.3
    flowers:    float = 0.0
    biome:      str   = BIOME_WASTELAND
    revealed:   bool  = False
