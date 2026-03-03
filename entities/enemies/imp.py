"""
Imp Enemy
Ranged caster with telegraphed projectile attacks.
"""
from ursina import Entity, color, Vec3, time, invoke, destroy, distance
from entities.enemy import Enemy
from config import ENEMIES


class ImpProjectile(Entity):
    """Simple projectile fired by imps."""

    def __init__(self, position, direction, speed, damage, source, **kwargs):
        super().__init__(
            model='sphere',
            color=color.orange,
            scale=0.28,
            position=position,
            collider='box',
            **kwargs
        )
        self.direction = direction.normalized()
        self.speed = speed
        self.damage = damage
        self.source = source
        self.life = 3.5

    def update(self):
        self.position += self.direction * self.speed * time.dt
        self.life -= time.dt
        if self.life <= 0:
            destroy(self)
            return

        import main
        game = getattr(main, 'game', None)
        if not game or not game.player or not game.player.is_alive:
            return

        player = game.player
        if distance(self.position, player.position + Vec3(0, 0.8, 0)) <= 1.0:
            player.take_damage(self.damage, source=self.source)
            destroy(self)


class Imp(Enemy):
    """Ranged enemy with windup animation before shooting."""

    def __init__(self, position=(0, 0, 0), **kwargs):
        super().__init__(
            position=position,
            enemy_type='imp',
            use_model=True,
            **kwargs
        )
        self.model = 'cube'
        self.scale = (0.8, 1.7, 0.8)
        self.color = color.rgb(190, 110, 30)
        self.projectile_speed = ENEMIES['imp'].get('projectile_speed', 14)
        self.windup = False

    def perform_attack(self):
        if self.windup or not self.target:
            return
        if self.distance_to_target() > self.attack_range:
            return

        self.windup = True
        self.color = color.rgb(255, 160, 70)
        invoke(self._release_projectile, delay=0.45)

    def _release_projectile(self):
        self.windup = False
        self.color = color.rgb(190, 110, 30)
        if not self.target or not self.target.is_alive or not self.is_alive:
            return

        origin = self.position + Vec3(0, 1.2, 0)
        direction = (self.target.position + Vec3(0, 1.0, 0)) - origin
        ImpProjectile(
            position=origin,
            direction=direction,
            speed=self.projectile_speed,
            damage=self.damage,
            source=self
        )
