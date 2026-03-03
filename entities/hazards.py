"""
Hazard entities: explosive barrels and timed floor traps.
"""
from ursina import Entity, color, time, distance
from config import (
    BARREL_EXPLOSION_RADIUS, BARREL_EXPLOSION_DAMAGE,
    TRAP_DAMAGE, TRAP_PERIOD
)
from core.services import Services


class ExplosiveBarrel(Entity):
    """Explodes when damaged, dealing radial damage."""

    def __init__(self, **kwargs):
        super().__init__(
            model='cube',
            color=color.rgb(200, 90, 40),
            scale=(0.8, 1.2, 0.8),
            collider='box',
            **kwargs
        )
        self.is_alive = True

    def take_damage(self, amount, source=None):
        if not self.is_alive:
            return
        self.explode(source=source)

    def explode(self, source=None):
        if not self.is_alive:
            return
        self.is_alive = False
        self.collider = None
        self.color = color.yellow
        self.scale = self.scale * 1.4

        # Damage nearby entities with take_damage.
        import main
        game = getattr(main, 'game', None)
        entities = []
        if game:
            entities.extend(game.enemies)
            if game.player:
                entities.append(game.player)

        for target in entities:
            if not target or not getattr(target, 'is_alive', True):
                continue
            if not hasattr(target, 'take_damage'):
                continue
            dist = distance(self.position, target.position)
            if dist > BARREL_EXPLOSION_RADIUS:
                continue
            multiplier = max(0.1, 1 - (dist / BARREL_EXPLOSION_RADIUS))
            target.take_damage(int(BARREL_EXPLOSION_DAMAGE * multiplier), source=source or self)

        if Services.telemetry:
            Services.telemetry.log('barrel_exploded', x=round(self.x, 2), z=round(self.z, 2))

        from ursina import destroy, invoke
        invoke(destroy, self, delay=0.1)


class FloorTrap(Entity):
    """Periodic area trap that damages entities standing on it."""

    def __init__(self, **kwargs):
        super().__init__(
            model='quad',
            rotation_x=90,
            scale=(2.2, 2.2, 2.2),
            color=color.rgb(120, 20, 20),
            collider='box',
            **kwargs
        )
        self.period = TRAP_PERIOD
        self.timer = 0
        self.active = False

    def update(self):
        self.timer += time.dt
        phase = (self.timer % self.period) / self.period
        self.active = phase > 0.55
        self.color = color.rgb(220, 55, 55) if self.active else color.rgb(80, 25, 25)

        if not self.active:
            return

        import main
        game = getattr(main, 'game', None)
        if not game:
            return

        targets = [e for e in game.enemies if e and e.is_alive]
        if game.player and game.player.is_alive:
            targets.append(game.player)

        for target in targets:
            if distance(self.position, target.position) <= 1.4:
                target.take_damage(TRAP_DAMAGE * time.dt, source=self)


class TimedDoor(Entity):
    """Door that periodically opens/closes to alter navigation lanes."""

    def __init__(self, **kwargs):
        super().__init__(
            model='cube',
            color=color.rgb(80, 80, 95),
            scale=(1.0, 3.2, 0.6),
            collider='box',
            **kwargs
        )
        self.period = 3.6
        self.timer = 0
        self.closed = True

    def update(self):
        self.timer += time.dt
        phase = (self.timer % self.period) / self.period
        self.closed = phase < 0.55
        self.collider = 'box' if self.closed else None
        self.color = color.rgb(110, 110, 130) if self.closed else color.rgb(70, 120, 90)
