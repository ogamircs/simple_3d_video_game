"""
Pistol Weapon
Hitscan weapon with moderate damage and fire rate.
"""
from ursina import Entity, raycast, camera, Vec3, color, random
from weapons.base_weapon import BaseWeapon
from config import WEAPONS


class Pistol(BaseWeapon):
    """Hitscan shotgun weapon."""

    def __init__(self, **kwargs):
        config = WEAPONS['pistol']

        super().__init__(
            weapon_name='Shotgun',
            damage=config['damage'],
            fire_rate=config['fire_rate'],
            range_distance=config['range'],
            spread=config['spread'],
            ammo_max=config['ammo_max'],
            **kwargs
        )

        # Load shotgun model
        self._load_shotgun_model()

        # Load hands
        self._load_hands()

        # Store default position for recoil animation (centered, bottom of screen)
        self.default_position = Vec3(0.05, -0.15, 0.4)
        self.default_rotation = Vec3(0, 90, 0)
        self.position = self.default_position

    def _load_shotgun_model(self):
        """Load the shotgun GLB model."""
        try:
            from ursina import load_model
            loaded = load_model('assets/models/shotgun.glb')
            if loaded:
                self.model = loaded
                self.scale = 0.08
                self.rotation = Vec3(0, 90, 0)  # Aim forward
                self.color = color.white
            else:
                # Fallback to cube
                self.model = 'cube'
                self.scale = (0.1, 0.15, 0.5)
                self.color = color.dark_gray
        except Exception as e:
            print(f"Failed to load shotgun model: {e}")
            self.model = 'cube'
            self.scale = (0.1, 0.15, 0.5)
            self.color = color.dark_gray

    def _load_hands(self):
        """Load hand models to hold the shotgun like classic Doom."""
        from ursina import load_model, Entity

        try:
            hand_model = load_model('assets/models/hand.glb')
            if hand_model:
                # Single hand gripping from behind (centered under shotgun)
                self.right_hand = Entity(
                    parent=self,
                    model=hand_model,
                    scale=0.5,
                    position=Vec3(0, -0.1, 0.2),
                    rotation=Vec3(90, 0, 90),
                    color=color.white
                )

                # Left hand not used for now
                self.left_hand = None
            else:
                self.right_hand = None
                self.left_hand = None
        except Exception as e:
            print(f"Failed to load hand model: {e}")
            self.right_hand = None
            self.left_hand = None

    def fire(self, owner):
        """
        Fire a hitscan shot.

        Args:
            owner: The entity firing (player)
        """
        # Get shoot origin and direction - shoot straight at crosshair
        origin = owner.get_shoot_origin()
        direction = owner.get_shoot_direction()

        # Raycast to find hit (no spread for accurate shots)
        hit_info = raycast(
            origin=origin,
            direction=direction,
            distance=self.range_distance,
            ignore=[owner, self]
        )

        if hit_info.hit:
            self.on_hit(hit_info, owner)

        # Shotgun recoil - immediate kick then animate back
        # Kick slightly up and forward (towards player)
        self.position = self.default_position + Vec3(0, 0.03, -0.08)
        self.rotation = self.default_rotation + Vec3(-10, 0, 3)

        # Animate back to default position
        self.animate_position(self.default_position, duration=0.15)
        self.animate_rotation(self.default_rotation, duration=0.18)

    def on_hit(self, hit_info, owner):
        """
        Handle hitting something.

        Args:
            hit_info: Raycast hit information
            owner: The entity that fired
        """
        # Create hit effect
        self.create_hit_effect(hit_info.world_point)

        target = hit_info.entity

        # Apply damage if target has take_damage method
        if hasattr(target, 'take_damage'):
            from systems.combat_system import CombatSystem
            CombatSystem.apply_damage(
                target=target,
                damage=self.damage,
                source=owner,
                hit_position=hit_info.world_point
            )

            # Show hit marker on HUD
            import main
            if main.game and main.game.hud:
                main.game.hud.show_hit_marker()

    def create_hit_effect(self, position):
        """Create a visual effect at the hit position."""
        from ursina import destroy, invoke

        # Simple hit spark
        hit_effect = Entity(
            model='sphere',
            scale=0.1,
            position=position,
            color=color.yellow
        )

        # Fade out and destroy
        hit_effect.animate_scale(0, duration=0.2)
        hit_effect.animate_color(color.clear, duration=0.2)
        invoke(destroy, hit_effect, delay=0.2)
