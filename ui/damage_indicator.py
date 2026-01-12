"""
Damage Indicator UI Component
Red screen flash when player takes damage.
"""
from ursina import Entity, camera, color
from config import DAMAGE_FLASH_INTENSITY, DAMAGE_FLASH_DURATION


class DamageIndicator(Entity):
    """Screen overlay that flashes red when damaged."""

    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, **kwargs)

        # Full screen overlay
        self.overlay = Entity(
            parent=self,
            model='quad',
            color=color.rgba(255, 0, 0, 0),
            scale=3,
            z=10  # Behind other UI
        )

        # Vignette effect (darker at edges)
        self.vignette = Entity(
            parent=self,
            model='quad',
            color=color.rgba(0, 0, 0, 0),
            scale=3,
            z=9
        )

    def flash(self, intensity=None):
        """
        Flash red to indicate damage.

        Args:
            intensity: Override default intensity (0-1)
        """
        if intensity is None:
            intensity = DAMAGE_FLASH_INTENSITY

        # Set flash color
        self.overlay.color = color.rgba(255, 0, 0, int(intensity * 255))

        # Fade out
        self.overlay.animate_color(
            color.rgba(255, 0, 0, 0),
            duration=DAMAGE_FLASH_DURATION
        )

    def show_low_health_warning(self, health_percentage):
        """
        Show persistent vignette for low health.

        Args:
            health_percentage: Current health as 0-1
        """
        if health_percentage < 0.3:
            # Pulsing red vignette at low health
            alpha = int((0.3 - health_percentage) * 200)
            self.vignette.color = color.rgba(100, 0, 0, alpha)
        else:
            self.vignette.color = color.rgba(0, 0, 0, 0)

    def cleanup(self):
        """Clean up damage indicator."""
        from ursina import destroy
        destroy(self)
