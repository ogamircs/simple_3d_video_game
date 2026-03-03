"""
Primary shotgun-style weapon.
"""
import random
from ursina import Entity, raycast, Vec3, color, Audio
from weapons.base_weapon import BaseWeapon
from config import WEAPONS


class Pistol(BaseWeapon):
    """Shotgun-like close/mid-range hitscan with burst alt fire."""

    def __init__(self, **kwargs):
        config = WEAPONS['pistol']

        super().__init__(
            weapon_name='Shotgun',
            damage=config['damage'],
            fire_rate=config['fire_rate'],
            alt_fire_cooldown=2.0,
            range_distance=config['range'],
            spread=config['spread'],
            ammo_max=config['ammo_max'],
            **kwargs
        )

        self._load_shotgun_model()
        self._load_hands()

        self.default_position = Vec3(0.05, -0.15, 0.4)
        self.default_rotation = Vec3(0, 90, 0)
        self.position = self.default_position
        self.rotation = self.default_rotation

    def _load_shotgun_model(self):
        """Load the shotgun GLB model."""
        try:
            from ursina import load_model
            loaded = load_model('assets/models/shotgun.glb')
            if loaded:
                self.model = loaded
                self.scale = 0.08
                self.rotation = Vec3(0, 90, 0)
                self.color = color.white
                return
        except Exception as e:
            print(f"Failed to load shotgun model: {e}")

        self.model = 'cube'
        self.scale = (0.1, 0.15, 0.5)
        self.color = color.dark_gray

    def _load_hands(self):
        """Load hand model."""
        from ursina import load_model

        try:
            hand_model = load_model('assets/models/hand.glb')
            if hand_model:
                self.right_hand = Entity(
                    parent=self,
                    model=hand_model,
                    scale=0.5,
                    position=Vec3(0, -0.1, 0.2),
                    rotation=Vec3(90, 0, 90),
                    color=color.white
                )
                self.left_hand = None
                return
        except Exception as e:
            print(f"Failed to load hand model: {e}")

        self.right_hand = None
        self.left_hand = None

    def _spread_direction(self, direction, spread):
        return Vec3(
            direction.x + random.uniform(-spread, spread),
            direction.y + random.uniform(-spread, spread),
            direction.z + random.uniform(-spread, spread)
        ).normalized()

    def _fire_single_hit(self, owner, direction, damage):
        hit_info = raycast(
            origin=owner.get_shoot_origin(),
            direction=direction,
            distance=self.range_distance,
            ignore=[owner, self]
        )
        if hit_info.hit:
            self.on_hit(hit_info, owner, damage)
            return True
        return False

    def fire(self, owner):
        """Standard accurate shot."""
        Audio('assets/sounds/shotgun.wav', autoplay=True)

        direction = owner.get_shoot_direction()
        self._fire_single_hit(owner, direction, self.damage)
        self._animate_recoil(kick=0.08, rise=0.03)

    def alt_fire(self, owner):
        """Close-range burst spread shot."""
        pellets = 6
        ammo_cost = 3
        if self.ammo_current < ammo_cost:
            return 0

        Audio('assets/sounds/shotgun.wav', autoplay=True)
        direction = owner.get_shoot_direction()
        for _ in range(pellets):
            pellet_dir = self._spread_direction(direction, self.spread * 4)
            self._fire_single_hit(owner, pellet_dir, int(self.damage * 0.7))

        self._animate_recoil(kick=0.13, rise=0.06)
        return ammo_cost

    def _animate_recoil(self, kick, rise):
        self.position = self.default_position + Vec3(0, rise, -kick)
        self.rotation = self.default_rotation + Vec3(-12, 0, 5)
        self.animate_position(self.default_position, duration=0.16)
        self.animate_rotation(self.default_rotation, duration=0.18)

    def on_hit(self, hit_info, owner, damage):
        """Apply hit behavior with richer feedback."""
        target = hit_info.entity
        self.create_hit_effect(hit_info.world_point)

        if hasattr(target, 'take_damage'):
            Audio('assets/sounds/hit.wav', autoplay=True)
            from systems.combat_system import CombatSystem
            result = CombatSystem.apply_damage(
                target=target,
                damage=damage,
                source=owner,
                hit_position=hit_info.world_point
            )

            import main
            if main.game and main.game.hud:
                main.game.hud.show_hit_marker()
                if result.get('headshot'):
                    main.game.hud.show_event('Headshot!', duration=0.6)

            # Subtle camera impulse.
            if hasattr(owner, 'camera_pivot'):
                owner.camera_pivot.rotation_x += 0.8

    def create_hit_effect(self, position):
        """Create a visual effect at hit point."""
        from ursina import invoke, destroy

        hit_effect = Entity(
            model='sphere',
            scale=0.1,
            position=position,
            color=color.yellow
        )
        hit_effect.animate_scale(0, duration=0.2)
        hit_effect.animate_color(color.clear, duration=0.2)
        invoke(destroy, hit_effect, delay=0.2)
