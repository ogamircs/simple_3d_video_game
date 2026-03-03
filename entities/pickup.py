"""
Pickup Entities
Health and ammo pickups with simple bob/rotate animation.
"""
import math
import random
from ursina import Entity, color, time, destroy, distance
from config import PICKUP_LIFETIME


class Pickup(Entity):
    """Collectible pickup that applies a benefit when the player gets close."""

    def __init__(self, pickup_type='health', value=25, target=None, on_collected=None, **kwargs):
        super().__init__(**kwargs)
        self.pickup_type = pickup_type
        self.value = value
        self.target = target
        self.on_collected = on_collected
        self.life_timer = PICKUP_LIFETIME

        # Visual style by pickup type.
        if self.pickup_type == 'ammo':
            self.model = 'cube'
            self.color = color.azure
            self.scale = (0.45, 0.35, 0.35)
        else:
            self.model = 'sphere'
            self.color = color.lime
            self.scale = 0.4

        self.collider = 'box'
        self.base_y = self.y
        self.anim_time = 0
        self.bob_phase = random.uniform(0, math.pi * 2)
        self.rotation_speed = random.uniform(70, 120)

    def update(self):
        """Animate pickup and handle collection/expiry."""
        self.anim_time += time.dt
        self.rotation_y += self.rotation_speed * time.dt
        self.y = self.base_y + math.sin((self.anim_time * 4) + self.bob_phase) * 0.06

        self.life_timer -= time.dt
        if self.life_timer <= 0:
            destroy(self)
            return

        if not self.target:
            return

        if distance(self.position, self.target.position) <= 1.25:
            if self._apply_to_target(self.target):
                if self.on_collected:
                    self.on_collected(self, self.target)
                destroy(self)

    def _apply_to_target(self, target):
        """Apply pickup effect; return True if consumed."""
        if self.pickup_type == 'health':
            if not hasattr(target, 'heal') or target.health >= target.max_health:
                return False
            return target.heal(self.value) > 0

        if self.pickup_type == 'ammo':
            weapon = getattr(target, 'current_weapon', None)
            if not weapon or weapon.ammo_current >= weapon.ammo_max:
                return False
            before = weapon.ammo_current
            weapon.ammo_current = min(weapon.ammo_max, weapon.ammo_current + self.value)
            return weapon.ammo_current > before

        return False
