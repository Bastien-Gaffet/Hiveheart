from dataclasses import dataclass


@dataclass
class Resources:
    nectar:      float = 0.0
    pollen:      float = 0.0
    hive_energy: float = 1.0
