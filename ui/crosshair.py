"""
Crosshair UI Component
Center screen aiming crosshair.
"""
from ursina import Entity, camera, color, invoke
from config import CROSSHAIR_SIZE, CROSSHAIR_GAP, CROSSHAIR_THICKNESS


class Crosshair(Entity):
    """Aiming crosshair in the center of the screen."""

    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, **kwargs)

        size = CROSSHAIR_SIZE
        gap = CROSSHAIR_GAP
        thickness = CROSSHAIR_THICKNESS

        # Create crosshair lines
        # Top line
        Entity(
            parent=self,
            model='quad',
            scale=(thickness, size),
            y=gap + size / 2,
            color=color.white
        )

        # Bottom line
        Entity(
            parent=self,
            model='quad',
            scale=(thickness, size),
            y=-(gap + size / 2),
            color=color.white
        )

        # Left line
        Entity(
            parent=self,
            model='quad',
            scale=(size, thickness),
            x=-(gap + size / 2),
            color=color.white
        )

        # Right line
        Entity(
            parent=self,
            model='quad',
            scale=(size, thickness),
            x=gap + size / 2,
            color=color.white
        )

        # Center dot (optional)
        Entity(
            parent=self,
            model='quad',
            scale=thickness,
            color=color.white
        )

        # Hit marker (hidden by default)
        self.hit_marker = Entity(
            parent=self,
            enabled=False
        )

        # Hit marker X shape
        hit_size = 0.02
        for angle in [45, -45]:
            Entity(
                parent=self.hit_marker,
                model='quad',
                scale=(hit_size * 2, thickness),
                rotation_z=angle,
                color=color.red
            )

    def show_hit(self):
        """Show hit marker briefly."""
        self.hit_marker.enabled = True
        self.hit_marker.scale = 1
        self.hit_marker.animate_scale(1.3, duration=0.1)
        invoke(self.hide_hit, delay=0.15)

    def hide_hit(self):
        """Hide hit marker."""
        self.hit_marker.enabled = False
        self.hit_marker.scale = 1

    def cleanup(self):
        """Clean up crosshair."""
        from ursina import destroy
        destroy(self)
