TILE_SIZE = 32
GRID_WIDTH = 20
GRID_HEIGHT = 15
CHUNK_SIZE        = 16   # tiles par côté (puissance de 2)
CHUNK_LOAD_RADIUS = 3    # chunks chargés autour caméra → 7×7 = 49 max
SCREEN_WIDTH  = GRID_WIDTH  * TILE_SIZE    # 640
UI_PANEL_HEIGHT = 80
SCREEN_HEIGHT = GRID_HEIGHT * TILE_SIZE + UI_PANEL_HEIGHT  # 560

FPS = 60

# --- Gameplay rates ---
BEE_SPEED = 100              # px/sec
BEE_FERTILITY_BOOST = 0.05
BEE_ENERGY_DRAIN = 0.05      # per second while active
BEE_ENERGY_RECHARGE = 0.2    # per second at hive

FLOWER_GROWTH_RATE = 0.01
POLLUTION_DAMAGE_RATE = 0.02
POLLUTION_FERTILITY_DAMAGE = 0.005
NECTAR_PER_FLOWER = 0.001
SPREAD_RATE = 0.01           # pollution added per second to each neighbor of a toxic tile

# --- Bee types ---
BEE_TYPE_WORKER = "worker"
BEE_TYPE_SCOUT = "scout"

# --- Biomes ---
BIOME_WASTELAND = "wasteland"
BIOME_MEADOW    = "meadow"
BIOME_FOREST    = "forest"
BIOME_TOXIC     = "toxic"
BIOME_WATER     = "water"

# --- Bee visuals ---
BEE_BODY_COLOR   = (255, 220, 50)
BEE_GLOW_COLOR   = (255, 255, 150)
BEE_SHADOW_COLOR = (0, 0, 0)
BEE_RADIUS       = 6
BEE_GLOW_RADIUS  = 10
BEE_SHADOW_DROP  = 5
BEE_BOB_SPEED    = 5.0   # rad/s
BEE_BOB_AMP      = 3.0   # px
BEE_BOB_PHASE    = 0.05  # phase shift per pixel of x position

# --- Mouse event type integers (mirrors pygame values, no pygame import needed in systems/) ---
MOUSE_BUTTON_DOWN = 1025   # pygame.MOUSEBUTTONDOWN
MOUSE_BUTTON_UP   = 1026   # pygame.MOUSEBUTTONUP
MOUSE_MOTION      = 1024   # pygame.MOUSEMOTION

# --- Hover highlight (essentiel — tile cible pendant le drag) ---
HOVER_BORDER_COLOR = (255, 255, 255)
HOVER_BORDER_ALPHA = 80
HOVER_BORDER_WIDTH = 3

# --- Target marker (optionnel — settings.show_target_marker) ---
TARGET_MARKER_COLOR       = (255, 220, 50)   # même jaune que l'abeille
TARGET_MARKER_BASE_RADIUS = 6
TARGET_MARKER_PULSE_AMP   = 3                # px
TARGET_MARKER_PULSE_SPEED = 4.0              # rad/s
TARGET_MARKER_WIDTH       = 2

# --- Camera ---
CAMERA_DEFAULT_OFFSET_X: float = 0.0
CAMERA_DEFAULT_OFFSET_Y: float = 0.0
CAMERA_DEFAULT_ZOOM:     float = 1.0
CAMERA_PAN_SPEED         = 200.0   # world-px/s (divided by zoom for consistent feel)
CAMERA_ZOOM_STEP         = 0.1
CAMERA_ZOOM_MIN          = 0.5
CAMERA_ZOOM_MAX          = 2.5
MOUSE_WHEEL              = 1027    # pygame.MOUSEWHEEL

# --- Bee glow effect ---
BEE_GLOW_EFFECT_RADIUS = 20
BEE_GLOW_EFFECT_COLOR  = (255, 200, 80)

# --- Flowers ---
FLOWER_DOT_COLOR  = (255, 200, 50)
FLOWER_DOT_RADIUS = 2
FLOWER_MAX_COUNT  = 5

# --- Pollen particles (optionnel — settings.show_pollen_particles) ---
POLLEN_SPAWN_RATE = 4.0          # particles/s per active worker bee
POLLEN_COLOR      = (255, 220, 100)

# --- Tile colour interpolation (optionnel — settings.show_tile_transitions) ---
TILE_COLOR_LERP_SPEED = 5.0      # higher = faster lerp

# --- Selection visual ---
BEE_SELECT_COLOR  = (255, 255, 255)
BEE_SELECT_RADIUS = BEE_GLOW_RADIUS + 4
BEE_SELECT_WIDTH  = 2

# --- Tile colour formula coefficients (fertility/pollution → RGB) ---
TILE_R_BASE = 80
TILE_R_POLL = 120   # pollution contribution to red channel
TILE_G_BASE = 60
TILE_G_FERT = 180   # fertility contribution to green channel
TILE_B_BASE = 40
TILE_B_FLOW = 80    # flowers contribution to blue channel

# --- Scout bee ---
SCOUT_SPAWN_COST    = 15.0
SCOUT_REVEAL_RADIUS = 3      # tiles revealed around scout current position
BEE_SCOUT_COLOR     = (130, 190, 255)   # blue tint

# --- Threat / toxic pulse ---
TOXIC_PULSE_COLOR      = (200, 20, 20)
TOXIC_PULSE_ALPHA_BASE = 25    # minimum overlay alpha
TOXIC_PULSE_ALPHA_AMP  = 25    # oscillation amplitude
TOXIC_PULSE_SPEED      = 3.0   # rad/s

# --- Fog of war ---
FOG_COLOR = (15, 15, 20)     # same as background — unrevealed tiles vanish into void

# --- Mission overlay ---
MISSION_OVERLAY_BG_COLOR     = (10, 10, 18)
MISSION_OVERLAY_BG_ALPHA     = 200
MISSION_WIN_COLOR            = (120, 220, 100)
MISSION_LOSE_COLOR           = (220, 60, 60)
MISSION_TITLE_FONT_SIZE      = 48
MISSION_BODY_FONT_SIZE       = 28
MISSION_BTN_WIDTH            = 200
MISSION_BTN_HEIGHT           = 50
MISSION_BTN_COLOR            = (80, 140, 60)
MISSION_BTN_FONT_SIZE        = 22

# --- HUD score bar / timer ---
MISSION_SCORE_BAR_WIDTH      = 260
MISSION_SCORE_BAR_HEIGHT     = 10
MISSION_SCORE_BAR_COLOR      = (80, 200, 100)
MISSION_SCORE_BAR_BG_COLOR   = (40, 40, 50)
MISSION_TIMER_WARN_THRESHOLD = 60.0
MISSION_TIMER_WARN_COLOR     = (220, 140, 40)

# --- HUD panel ---
BEE_SPAWN_COST         = 10.0
UI_PANEL_COLOR         = (15, 15, 25)
UI_PANEL_BORDER_COLOR  = (60, 60, 80)
UI_FONT_COLOR          = (220, 200, 120)
UI_FONT_SIZE_LARGE     = 22
UI_FONT_SIZE_SMALL     = 16
UI_BEE_SLOTS_X         = 200    # x-centre of first slot
UI_BEE_SLOT_SIZE       = 44     # diameter of slot ring
UI_BEE_SLOT_GAP        = 14
UI_BEE_SLOT_COLOR      = (80, 70, 40)
UI_SPAWN_BTN_WIDTH     = 130
UI_SPAWN_BTN_COLOR_ON  = (100, 180, 60)
UI_SPAWN_BTN_COLOR_OFF = (60, 60, 60)

# --- Save system ---
WORLD_SEED = 42
SAVE_DIR   = "saves"