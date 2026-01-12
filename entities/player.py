"""
Player Controller
First-person player with movement, looking, and shooting.
"""
from ursina import (
    Entity, camera, mouse, held_keys, time, Vec3, Vec2,
    color, raycast, destroy, clamp
)
from ursina.prefabs.first_person_controller import FirstPersonController
from config import (
    PLAYER_SPEED, PLAYER_SPRINT_MULTIPLIER, PLAYER_MAX_HEALTH,
    PLAYER_HEIGHT, MOUSE_SENSITIVITY, GameState
)


class Player(FirstPersonController):
    """First-person player controller with health and weapons."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Override default settings
        self.speed = PLAYER_SPEED
        self.mouse_sensitivity = Vec2(MOUSE_SENSITIVITY, MOUSE_SENSITIVITY)
        self.height = PLAYER_HEIGHT
        self.camera_pivot.y = PLAYER_HEIGHT * 0.9

        # Health system
        self._max_health = PLAYER_MAX_HEALTH
        self._health = PLAYER_MAX_HEALTH
        self.is_alive = True

        # Weapon system
        self.weapons = []
        self.current_weapon_index = 0
        self.gun_pivot = Entity(parent=camera)

        # Initialize pistol
        from weapons.pistol import Pistol
        pistol = Pistol(parent=self.gun_pivot)
        self.weapons.append(pistol)
        pistol.equip()

        # Damage feedback
        self.damage_cooldown = 0

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, value):
        self._health = clamp(value, 0, self._max_health)
        if self._health <= 0 and self.is_alive:
            self.die()

    @property
    def max_health(self):
        return self._max_health

    @property
    def health_percentage(self):
        return self._health / self._max_health

    @property
    def current_weapon(self):
        """Get the currently equipped weapon."""
        if self.weapons and 0 <= self.current_weapon_index < len(self.weapons):
            return self.weapons[self.current_weapon_index]
        return None

    def update(self):
        """Update player each frame."""
        if not self.is_alive:
            return

        # Get game state from main module
        import main
        if main.game and main.game.state != GameState.PLAYING:
            return

        # Call parent update for movement
        super().update()

        # Sprint
        if held_keys['shift']:
            self.speed = PLAYER_SPEED * PLAYER_SPRINT_MULTIPLIER
        else:
            self.speed = PLAYER_SPEED

        # Shooting with left mouse button
        if mouse.left and self.current_weapon:
            self.current_weapon.try_fire(self)

        # Update damage cooldown
        if self.damage_cooldown > 0:
            self.damage_cooldown -= time.dt

    def input(self, key):
        """Handle discrete input events."""
        if not self.is_alive:
            return

        # Get game state
        import main
        if main.game and main.game.state != GameState.PLAYING:
            return

        # Weapon switching with number keys
        if key in '123456789':
            index = int(key) - 1
            if 0 <= index < len(self.weapons):
                self.switch_weapon(index)

        # Scroll wheel weapon switch
        if key == 'scroll up':
            self.switch_weapon((self.current_weapon_index + 1) % max(1, len(self.weapons)))
        if key == 'scroll down':
            self.switch_weapon((self.current_weapon_index - 1) % max(1, len(self.weapons)))

        # Reload
        if key == 'r' and self.current_weapon:
            self.current_weapon.reload()

    def switch_weapon(self, index):
        """Switch to a different weapon."""
        if index == self.current_weapon_index:
            return
        if not (0 <= index < len(self.weapons)):
            return

        # Holster current weapon
        if self.current_weapon:
            self.current_weapon.holster()

        # Equip new weapon
        self.current_weapon_index = index
        if self.current_weapon:
            self.current_weapon.equip()

    def take_damage(self, amount, source=None):
        """Take damage from a source."""
        if not self.is_alive:
            return
        if self.damage_cooldown > 0:
            return

        self.health -= amount
        self.damage_cooldown = 0.1  # Brief invincibility

        # Notify HUD
        import main
        if main.game and main.game.hud:
            main.game.hud.on_player_damaged(amount, source)

    def heal(self, amount):
        """Restore health."""
        old_health = self._health
        self.health += amount
        return self._health - old_health

    def die(self):
        """Handle player death."""
        self.is_alive = False
        self.speed = 0

        # Trigger game over
        import main
        if main.game:
            main.game.game_over()

    def get_shoot_origin(self):
        """Get the origin point for shooting (camera position)."""
        return camera.world_position

    def get_shoot_direction(self):
        """Get the direction for shooting (camera forward)."""
        return camera.forward
