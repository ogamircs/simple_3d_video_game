"""
Base Entity Class
Foundation for all game entities with health system.
"""
from ursina import Entity, destroy, invoke


class BaseGameEntity(Entity):
    """Base class for all game entities that have health."""

    def __init__(self, max_health=100, **kwargs):
        super().__init__(**kwargs)
        self._max_health = max_health
        self._health = max_health
        self.is_alive = True

    @property
    def health(self):
        """Current health value."""
        return self._health

    @health.setter
    def health(self, value):
        """Set health, clamped between 0 and max_health."""
        self._health = max(0, min(value, self._max_health))
        if self._health <= 0 and self.is_alive:
            self.die()

    @property
    def max_health(self):
        """Maximum health value."""
        return self._max_health

    @property
    def health_percentage(self):
        """Health as a percentage (0-1)."""
        return self._health / self._max_health

    def take_damage(self, amount, source=None):
        """
        Apply damage to this entity.

        Args:
            amount: Damage amount
            source: The entity that caused the damage (optional)
        """
        if not self.is_alive:
            return

        self.health -= amount
        self.on_damaged(amount, source)

    def heal(self, amount):
        """
        Restore health to this entity.

        Args:
            amount: Health amount to restore
        """
        if not self.is_alive:
            return

        old_health = self._health
        self.health += amount
        self.on_healed(self._health - old_health)

    def die(self):
        """Handle entity death."""
        self.is_alive = False
        self.on_death()

    def on_damaged(self, amount, source):
        """Override in subclasses to handle damage events."""
        pass

    def on_healed(self, amount):
        """Override in subclasses to handle heal events."""
        pass

    def on_death(self):
        """Override in subclasses to handle death events."""
        pass
