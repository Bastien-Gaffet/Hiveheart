from dataclasses import dataclass


@dataclass
class Settings:
    # --- Visuels optionnels (menu paramètres futur) ---
    show_target_marker:    bool  = True
    show_pollen_particles: bool  = True
    show_tile_transitions: bool  = True
    # master_volume: float = 1.0    # Phase audio
    # music_volume:  float = 0.7    # Phase audio
