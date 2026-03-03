"""
Demon Enemy
Fast melee bruiser with short charge bursts.
"""
from ursina import color, time, Vec3
from entities.enemy import Enemy, EnemyState


class Demon(Enemy):
    """Aggressive melee enemy that bursts forward when attacking."""

    def __init__(self, position=(0, 0, 0), **kwargs):
        super().__init__(
            position=position,
            enemy_type='demon',
            use_model=True,
            **kwargs
        )
        self.model = 'cube'
        self.color = color.rgb(150, 30, 30)
        self.scale = (1.3, 2.2, 1.3)
        self.charge_timer = 0

    def update(self):
        super().update()
        if not self.is_alive:
            return

        if self.state == EnemyState.CHASE:
            self.charge_timer += time.dt
            if self.charge_timer >= 2.2 and self.target:
                self.charge_timer = 0
                direction = self.target.position - self.position
                direction.y = 0
                if direction.length() > 0:
                    self.position += direction.normalized() * 1.9
