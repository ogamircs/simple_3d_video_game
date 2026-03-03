"""
Game Configuration Constants
All game settings and tunable parameters in one place.
"""
from dataclasses import dataclass

# =============================================================================
# WINDOW SETTINGS
# =============================================================================
WINDOW_TITLE = "Doom-like FPS"
WINDOW_SIZE = (1280, 720)
FULLSCREEN = False
SHOW_FPS = True
DEFAULT_FOV = 90

# =============================================================================
# PLAYER SETTINGS
# =============================================================================
PLAYER_SPEED = 6
PLAYER_SPRINT_MULTIPLIER = 1.5
PLAYER_MAX_HEALTH = 100
PLAYER_HEIGHT = 2
MOUSE_SENSITIVITY = 40

# =============================================================================
# WEAPON SETTINGS
# =============================================================================
WEAPONS = {
    'pistol': {
        'damage': 15,
        'fire_rate': 0.3,      # seconds between shots
        'range': 100,
        'spread': 0.02,        # accuracy spread
        'ammo_max': 50,
        'ammo_per_clip': 12,
    },
    'shotgun': {
        'damage': 8,           # per pellet
        'pellets': 8,
        'fire_rate': 0.8,
        'range': 30,
        'spread': 0.15,
        'ammo_max': 24,
        'ammo_per_clip': 6,
    },
    'rifle': {
        'damage': 9,
        'fire_rate': 0.12,
        'range': 120,
        'spread': 0.01,
        'ammo_max': 90,
        'ammo_per_clip': 30,
    },
}

# =============================================================================
# ENEMY SETTINGS
# =============================================================================
ENEMIES = {
    'zombie': {
        'health': 50,
        'damage': 10,
        'speed': 2,
        'attack_range': 2.5,
        'attack_cooldown': 1.0,
        'detection_range': 40,
        'color': (0.8, 0.2, 0.2),  # Red (fallback)
        'scale': (1, 2, 1),  # Fallback cube scale
        'model_scale': 0.04,  # Scale for OBJ model (model is ~50 units tall)
        'model_height': 2.0,  # Height for health bar positioning
    },
    'demon': {
        'health': 100,
        'damage': 25,
        'speed': 5,
        'attack_range': 2.5,
        'attack_cooldown': 0.8,
        'detection_range': 50,
        'color': (0.6, 0.1, 0.1),  # Dark red
        'scale': (1.5, 2.5, 1.5),
        'model_scale': 0.02,
        'model_height': 2.5,
    },
    'imp': {
        'health': 40,
        'damage': 15,
        'speed': 3,
        'attack_range': 25,    # Ranged
        'attack_cooldown': 1.5,
        'detection_range': 60,
        'projectile_speed': 15,
        'color': (0.8, 0.4, 0.1),  # Orange
        'scale': (0.8, 1.5, 0.8),
    },
}

# =============================================================================
# COMBAT SETTINGS
# =============================================================================
DAMAGE_FALLOFF_START = 15      # Distance where damage starts to fall off
DAMAGE_FALLOFF_END = 40        # Distance where damage is minimum
DAMAGE_MINIMUM_MULTIPLIER = 0.25
HEADSHOT_MULTIPLIER = 2.0

# =============================================================================
# UI SETTINGS
# =============================================================================
HEALTH_BAR_WIDTH = 0.3
HEALTH_BAR_HEIGHT = 0.03
HEALTH_BAR_POSITION = (-0.65, -0.45)

CROSSHAIR_SIZE = 0.02
CROSSHAIR_GAP = 0.008
CROSSHAIR_THICKNESS = 0.003

DAMAGE_FLASH_INTENSITY = 0.4
DAMAGE_FLASH_DURATION = 0.3

# Typography and menu sizing
UI_FONT_PRIMARY = 'OpenSans-Regular.ttf'
UI_FONT_MONO = 'VeraMono.ttf'

MENU_TITLE_SCALE = 2.4
MENU_SUBTITLE_SCALE = 1.1
MENU_BODY_TEXT_SCALE = 0.8
MENU_BUTTON_SCALE = (0.58, 0.12)
MENU_BUTTON_TEXT_SCALE = 3.4

HUD_VALUE_TEXT_SCALE = 1.7
HUD_LABEL_TEXT_SCALE = 0.72

UI_SCALE_PRESETS = {
    'small': 0.9,
    'normal': 1.0,
    'large': 1.15,
}


class RuntimeSettings:
    """Mutable runtime settings controlled from the options menu."""
    ui_scale_name = 'normal'
    mouse_sensitivity = MOUSE_SENSITIVITY
    audio_volume = 0.5
    fullscreen = FULLSCREEN
    fov = DEFAULT_FOV

    @classmethod
    def ui_scale(cls):
        return UI_SCALE_PRESETS.get(cls.ui_scale_name, 1.0)

# =============================================================================
# LEVEL SETTINGS
# =============================================================================
DEFAULT_LEVEL_SIZE = 50
WALL_HEIGHT = 4
WALL_THICKNESS = 1

# =============================================================================
# PROGRESSION SETTINGS (P1)
# =============================================================================
MAX_WAVES = 5
BASE_ENEMIES_PER_WAVE = 5
ENEMIES_PER_WAVE_STEP = 2
BASE_SPAWN_INTERVAL = 1.2
SPAWN_INTERVAL_DECAY = 0.1
MIN_SPAWN_INTERVAL = 0.45
WAVE_BREAK_DURATION = 3.0
SPAWN_MIN_PLAYER_DISTANCE = 12
SPAWN_DIRECTOR_LOS_ATTEMPTS = 16

PICKUP_MAX_ACTIVE = 2
PICKUP_SPAWN_COOLDOWN = 8.0
PICKUP_LIFETIME = 18.0
HEALTH_PICKUP_VALUE = 30
AMMO_PICKUP_VALUE = 8

SCORE_REWARD_STEP = 50
SCORE_REWARD_HEAL = 15
SCORE_REWARD_AMMO = 6

# =============================================================================
# P2/P3 CONTENT SETTINGS
# =============================================================================
ENEMY_STAGGER_THRESHOLD = 14
ENEMY_STAGGER_CHANCE = 0.3
ENEMY_STAGGER_DURATION = 0.28

ALT_FIRE_COOLDOWN_DEFAULT = 2.0
RIFLE_ALT_FIRE_COOLDOWN = 3.5

ARENA_LAYOUT_VARIANTS = 3
EXPLOSIVE_BARRELS_PER_LAYOUT = 4
FLOOR_TRAPS_PER_LAYOUT = 3
TRAP_DAMAGE = 18
TRAP_PERIOD = 2.2
BARREL_EXPLOSION_RADIUS = 5.2
BARREL_EXPLOSION_DAMAGE = 38
SPAWN_BLOCKER_RADIUS = 8
SPAWN_BLOCKERS = [
    (0, 0, 0),
    (8, 0, 0),
    (-8, 0, 0),
    (0, 0, 8),
    (0, 0, -8),
]

# =============================================================================
# P4 AUDIO/VFX SETTINGS
# =============================================================================
AMBIENT_TRACK = 'sine'
COMBAT_TRACK = 'noise'
LOW_HEALTH_TRACK = 'sine'
COMBAT_AUDIO_MIN = 0.08
COMBAT_AUDIO_MAX = 0.34
LOW_HEALTH_AUDIO_LEVEL = 0.22

# =============================================================================
# P5 TELEMETRY SETTINGS
# =============================================================================
TELEMETRY_LOG_PATH = 'gameplay.log'
TELEMETRY_ENABLED = True


@dataclass(frozen=True)
class WeaponConfig:
    damage: int
    fire_rate: float
    range: float
    spread: float
    ammo_max: int


@dataclass(frozen=True)
class EnemyConfig:
    health: int
    damage: int
    speed: float
    attack_range: float
    attack_cooldown: float
    detection_range: float


WEAPON_CONFIGS = {
    name: WeaponConfig(
        damage=data['damage'],
        fire_rate=data['fire_rate'],
        range=data['range'],
        spread=data['spread'],
        ammo_max=data['ammo_max'],
    )
    for name, data in WEAPONS.items()
}

ENEMY_CONFIGS = {
    name: EnemyConfig(
        health=data['health'],
        damage=data['damage'],
        speed=data['speed'],
        attack_range=data['attack_range'],
        attack_cooldown=data['attack_cooldown'],
        detection_range=data['detection_range'],
    )
    for name, data in ENEMIES.items()
}

# =============================================================================
# GAME STATES
# =============================================================================
class GameState:
    MENU = 'menu'
    PLAYING = 'playing'
    PAUSED = 'paused'
    GAME_OVER = 'game_over'
    VICTORY = 'victory'
