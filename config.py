"""
Game Configuration Constants
All game settings and tunable parameters in one place.
"""

# =============================================================================
# WINDOW SETTINGS
# =============================================================================
WINDOW_TITLE = "Doom-like FPS"
WINDOW_SIZE = (1280, 720)
FULLSCREEN = False
SHOW_FPS = True

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

# =============================================================================
# LEVEL SETTINGS
# =============================================================================
DEFAULT_LEVEL_SIZE = 50
WALL_HEIGHT = 4
WALL_THICKNESS = 1

# =============================================================================
# GAME STATES
# =============================================================================
class GameState:
    MENU = 'menu'
    PLAYING = 'playing'
    PAUSED = 'paused'
    GAME_OVER = 'game_over'
