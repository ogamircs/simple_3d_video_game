"""
Base Enemy Class
Enemy with AI state machine: IDLE -> CHASE -> ATTACK.
"""
from ursina import Entity, Vec3, time, destroy, invoke, color, distance, Audio
from entities.base_entity import BaseGameEntity
from config import ENEMIES, GameState


class EnemyState:
    """Enemy AI states."""
    IDLE = 'idle'
    CHASE = 'chase'
    ATTACK = 'attack'
    DEAD = 'dead'


class Enemy(BaseGameEntity):
    """Base enemy class with AI behavior."""

    def __init__(
        self,
        position=(0, 0, 0),
        enemy_type='zombie',
        use_model=True,
        **kwargs
    ):
        # Get config for this enemy type
        config = ENEMIES.get(enemy_type, ENEMIES['zombie'])

        # Set up base entity - subclasses can override model loading
        if use_model:
            super().__init__(
                model='cube',
                color=color.rgb(*[int(c * 255) for c in config['color']]),
                position=position,
                scale=config['scale'],
                collider='box',
                max_health=config['health'],
                **kwargs
            )
        else:
            # Subclass will set up model
            super().__init__(
                position=position,
                max_health=config['health'],
                **kwargs
            )

        # Enemy properties
        self.enemy_type = enemy_type
        self.damage = config['damage']
        self.speed = config['speed']
        self.attack_range = config['attack_range']
        self.attack_cooldown = config['attack_cooldown']
        self.detection_range = config['detection_range']

        # AI state
        self.state = EnemyState.IDLE
        self.prev_state = None
        self.target = None
        self.time_since_attack = self.attack_cooldown

        # Store config for health bar positioning
        self.model_height = config.get('model_height', config['scale'][1])

        # Health bar above enemy - not parented to avoid scale issues
        self.health_bar_bg = Entity(
            model='quad',
            color=color.dark_gray,
            scale=(0.8, 0.08),  # Smaller health bar
            billboard=True
        )
        self.health_bar = Entity(
            parent=self.health_bar_bg,
            model='quad',
            color=color.red,
            scale=(0.95, 0.7),
            z=-0.01
        )

    def update(self):
        """Update enemy AI each frame."""
        # Update health bar position above enemy
        if self.health_bar_bg:
            self.health_bar_bg.position = (
                self.position.x,
                self.position.y + self.model_height + 0.3,
                self.position.z
            )

        if not self.is_alive:
            return

        # Check game state
        import main
        if main.game and main.game.state != GameState.PLAYING:
            return

        if not self.target or not self.target.is_alive:
            if self.state != EnemyState.IDLE:
                self.state = EnemyState.IDLE
                self.on_idle_start()
            return

        # Calculate distance to target
        dist = self.distance_to_target()

        # Store previous state for transition detection
        old_state = self.state

        # State machine transitions
        if dist > self.detection_range:
            self.state = EnemyState.IDLE
        elif dist <= self.attack_range:
            self.state = EnemyState.ATTACK
        else:
            self.state = EnemyState.CHASE

        # Call state transition hooks
        if old_state != self.state:
            if self.state == EnemyState.IDLE:
                self.on_idle_start()
            elif self.state == EnemyState.CHASE:
                self.on_chase_start()
            elif self.state == EnemyState.ATTACK:
                self.on_attack_start()

        # Execute current state behavior
        if self.state == EnemyState.CHASE:
            self.chase()
        elif self.state == EnemyState.ATTACK:
            self.attack()

        # Update attack cooldown
        self.time_since_attack += time.dt

    def on_idle_start(self):
        """Called when entering idle state. Override in subclasses."""
        pass

    def on_chase_start(self):
        """Called when entering chase state. Override in subclasses."""
        pass

    def on_attack_start(self):
        """Called when entering attack state. Override in subclasses."""
        pass

    def distance_to_target(self):
        """Calculate distance to target."""
        if not self.target:
            return float('inf')
        return distance(self.position, self.target.position)

    def chase(self):
        """Move toward the target with smooth walking."""
        if not self.target:
            return

        # Get direction to target (ignoring Y for ground movement)
        direction = Vec3(
            self.target.position.x - self.position.x,
            0,
            self.target.position.z - self.position.z
        )

        if direction.length() > 0:
            direction = direction.normalized()
            # Move smoothly toward target
            self.position += direction * self.speed * time.dt

        # Face the target
        self.look_at_target()

    def look_at_target(self):
        """Rotate to face the target (Y-axis only)."""
        if not self.target:
            return

        # Calculate angle to target
        direction = self.target.position - self.position
        direction.y = 0

        if direction.length() > 0:
            self.look_at(self.position + direction)
            # Keep upright
            self.rotation_x = 0
            self.rotation_z = 0

    def attack(self):
        """Execute attack if cooldown is ready."""
        if self.time_since_attack < self.attack_cooldown:
            return

        self.perform_attack()
        self.time_since_attack = 0

    def perform_attack(self):
        """Perform the actual attack. Override in subclasses."""
        if not self.target or not hasattr(self.target, 'take_damage'):
            return

        # Check if still in range
        if self.distance_to_target() <= self.attack_range:
            self.target.take_damage(self.damage, source=self)

    def take_damage(self, amount, source=None):
        """Override to update health bar."""
        super().take_damage(amount, source)

        # Update health bar
        if self.health_bar:
            self.health_bar.scale_x = self.health_percentage * 0.95

        # Flash on damage
        self.blink(color.red, duration=0.1)

    def on_death(self):
        """Handle enemy death."""
        self.state = EnemyState.DEAD
        self.collider = None

        # Play death sound
        Audio('assets/sounds/enemy_death.wav', autoplay=True)

        # Clean up health bar
        if self.health_bar_bg:
            destroy(self.health_bar_bg)
            self.health_bar_bg = None

        # Notify game
        import game_state
        if game_state.game:
            game_state.game.on_enemy_killed(self)

        # Death animation
        self.animate_scale(0, duration=0.3)
        invoke(destroy, self, delay=0.3)

    def on_damaged(self, amount, source):
        """Handle damage event."""
        pass
