"""
Base Weapon Class
Abstract weapon interface with fire rate, ammo, and damage.
"""
from ursina import Entity, time, Vec3, color


class BaseWeapon(Entity):
    """Base class for all weapons."""

    def __init__(
        self,
        weapon_name='weapon',
        damage=10,
        fire_rate=0.5,
        range_distance=100,
        spread=0.01,
        ammo_max=50,
        **kwargs
    ):
        super().__init__(**kwargs)

        # Weapon properties
        self.weapon_name = weapon_name
        self.damage = damage
        self.fire_rate = fire_rate
        self.range_distance = range_distance
        self.spread = spread
        self.ammo_max = ammo_max
        self.ammo_current = ammo_max

        # State
        self.time_since_fire = fire_rate  # Ready to fire immediately
        self.is_equipped = False
        self.is_reloading = False

        # Muzzle flash placeholder
        self.muzzle_flash = Entity(
            parent=self,
            model='cube',
            scale=0.1,
            color=color.yellow,
            position=(0, 0, 0.5),
            enabled=False
        )

    def update(self):
        """Update weapon state each frame."""
        self.time_since_fire += time.dt

    def can_fire(self):
        """Check if the weapon can fire."""
        return (
            self.is_equipped and
            not self.is_reloading and
            self.time_since_fire >= self.fire_rate and
            self.ammo_current > 0
        )

    def try_fire(self, owner):
        """Attempt to fire the weapon."""
        if not self.can_fire():
            return False

        self.fire(owner)
        self.time_since_fire = 0
        self.ammo_current -= 1
        self.show_muzzle_flash()
        return True

    def fire(self, owner):
        """
        Fire the weapon. Override in subclasses.

        Args:
            owner: The entity firing the weapon (usually player)
        """
        raise NotImplementedError("Subclasses must implement fire()")

    def reload(self):
        """Reload the weapon."""
        if self.ammo_current < self.ammo_max and not self.is_reloading:
            self.is_reloading = True
            # Instant reload for now
            self.ammo_current = self.ammo_max
            self.is_reloading = False

    def equip(self):
        """Equip this weapon (make visible and active)."""
        self.is_equipped = True
        self.enabled = True

    def holster(self):
        """Holster this weapon (hide and deactivate)."""
        self.is_equipped = False
        self.enabled = False

    def show_muzzle_flash(self):
        """Show muzzle flash effect."""
        from ursina import invoke
        self.muzzle_flash.enabled = True
        invoke(self.hide_muzzle_flash, delay=0.05)

    def hide_muzzle_flash(self):
        """Hide muzzle flash effect."""
        self.muzzle_flash.enabled = False
