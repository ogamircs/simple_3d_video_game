"""
Rifle weapon.
"""
import random
from ursina import Entity, raycast, Vec3, color, Audio
from weapons.base_weapon import BaseWeapon
from config import WEAPONS, RIFLE_ALT_FIRE_COOLDOWN


class Rifle(BaseWeapon):
    """Accurate rapid-fire rifle with piercing alt-shot cooldown ability."""

    def __init__(self, **kwargs):
        config = WEAPONS['rifle']
        super().__init__(
            weapon_name='Rifle',
            damage=config['damage'],
            fire_rate=config['fire_rate'],
            alt_fire_cooldown=RIFLE_ALT_FIRE_COOLDOWN,
            range_distance=config['range'],
            spread=config['spread'],
            ammo_max=config['ammo_max'],
            **kwargs
        )

        self.model = 'cube'
        self.scale = (0.1, 0.12, 0.7)
        self.color = color.rgb(70, 70, 80)
        self.default_position = Vec3(0.04, -0.14, 0.42)
        self.default_rotation = Vec3(2, 88, 0)
        self.position = self.default_position
        self.rotation = self.default_rotation

    def _spread_direction(self, direction, spread):
        return Vec3(
            direction.x + random.uniform(-spread, spread),
            direction.y + random.uniform(-spread, spread),
            direction.z + random.uniform(-spread, spread)
        ).normalized()

    def fire(self, owner):
        Audio('assets/sounds/hit.wav', autoplay=True)

        direction = self._spread_direction(owner.get_shoot_direction(), self.spread)
        hit_info = raycast(
            origin=owner.get_shoot_origin(),
            direction=direction,
            distance=self.range_distance,
            ignore=[owner, self]
        )

        if hit_info.hit and hasattr(hit_info.entity, 'take_damage'):
            from systems.combat_system import CombatSystem
            result = CombatSystem.apply_damage(
                target=hit_info.entity,
                damage=self.damage,
                source=owner,
                hit_position=hit_info.world_point
            )
            import main
            if main.game and main.game.hud:
                main.game.hud.show_hit_marker()
                if result.get('headshot'):
                    main.game.hud.show_event('Critical headshot', duration=0.6)

        self._animate_recoil(0.03, 0.015)

    def alt_fire(self, owner):
        """Power shot with long cooldown and high penetration-like damage."""
        ammo_cost = self.alt_fire_ammo_cost()
        if self.ammo_current < ammo_cost:
            return 0

        Audio('assets/sounds/shotgun.wav', autoplay=True)
        direction = owner.get_shoot_direction()
        hit_info = raycast(
            origin=owner.get_shoot_origin(),
            direction=direction,
            distance=self.range_distance * 1.1,
            ignore=[owner, self]
        )
        if hit_info.hit and hasattr(hit_info.entity, 'take_damage'):
            from systems.combat_system import CombatSystem
            CombatSystem.apply_damage(
                target=hit_info.entity,
                damage=int(self.damage * 3.2),
                source=owner,
                hit_position=hit_info.world_point
            )
            import main
            if main.game and main.game.hud:
                main.game.hud.show_event('Power shot!', duration=0.8)

        self._animate_recoil(0.1, 0.05)
        return ammo_cost

    def alt_fire_ammo_cost(self):
        return 6

    def _animate_recoil(self, kick, rise):
        self.position = self.default_position + Vec3(0, rise, -kick)
        self.rotation = self.default_rotation + Vec3(-7, 0, 1)
        self.animate_position(self.default_position, duration=0.1)
        self.animate_rotation(self.default_rotation, duration=0.12)
