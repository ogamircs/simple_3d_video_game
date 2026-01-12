"""
Health Bar UI Component
Displays player health as a visual bar.
"""
from ursina import Entity, Text, camera, color
from config import HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT, HEALTH_BAR_POSITION


class PlayerHealthBar(Entity):
    """Visual health bar for the player."""

    def __init__(self, max_health=100, **kwargs):
        super().__init__(parent=camera.ui, **kwargs)

        self.max_health = max_health

        # Border (outer white)
        self.border = Entity(
            parent=self,
            model='quad',
            color=color.white,
            scale=(HEALTH_BAR_WIDTH + 0.01, HEALTH_BAR_HEIGHT + 0.01),
            position=HEALTH_BAR_POSITION,
            origin=(-0.5, 0)
        )

        # Background bar (dark gray)
        self.bg = Entity(
            parent=self,
            model='quad',
            color=color.dark_gray,
            scale=(HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT),
            position=HEALTH_BAR_POSITION,
            origin=(-0.5, 0),
            z=-0.01
        )

        # Health bar (foreground - green/yellow/red)
        self.bar = Entity(
            parent=self,
            model='quad',
            color=color.lime,
            scale=(HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT * 0.8),
            position=HEALTH_BAR_POSITION,
            origin=(-0.5, 0),
            z=-0.02
        )

        # Label
        self.label = Text(
            parent=self,
            text='HEALTH',
            position=(HEALTH_BAR_POSITION[0], HEALTH_BAR_POSITION[1] + 0.035),
            origin=(-0.5, 0),
            scale=1,
            color=color.light_gray
        )

    def set_value(self, health):
        """Update the health bar value."""
        percentage = max(0, min(1, health / self.max_health))
        self.bar.scale_x = HEALTH_BAR_WIDTH * percentage

        # Color based on health
        if percentage > 0.6:
            self.bar.color = color.lime
        elif percentage > 0.3:
            self.bar.color = color.yellow
        else:
            self.bar.color = color.red

    def cleanup(self):
        """Clean up the health bar."""
        from ursina import destroy
        destroy(self)
