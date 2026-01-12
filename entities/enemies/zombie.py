"""
Zombie Enemy
Slow melee enemy that chases and attacks the player.
"""
import math
import random
from ursina import Entity, Vec3, color, time, destroy
from entities.enemy import Enemy
from config import ENEMIES


class Zombie(Enemy):
    """Slow melee zombie enemy with animated humanoid model."""

    # Available zombie model variants
    ZOMBIE_VARIANTS = [
        'zombie_centered',  # Default zombie
    ]

    # Variant colors for visual diversity (tint applied to model)
    VARIANT_TINTS = [
        None,  # Original colors
        (0.9, 1.0, 0.9),   # Slightly green tint
        (0.85, 0.85, 0.9), # Pale blue/gray
        (1.0, 0.9, 0.85),  # Warm/tan
        (0.95, 0.9, 1.0),  # Purple tint
    ]

    # Scale variations
    SCALE_VARIANTS = [
        1.0,    # Normal
        0.85,   # Smaller
        1.15,   # Larger
        0.95,   # Slightly smaller
        1.05,   # Slightly larger
    ]

    def __init__(self, position=(0, 0, 0), variant_id=None, **kwargs):
        # Get zombie config
        config = ENEMIES.get('zombie', ENEMIES['zombie'])

        # Initialize with parent class (no model yet)
        super().__init__(
            position=position,
            enemy_type='zombie',
            use_model=False,
            **kwargs
        )

        # Select random variant if not specified
        if variant_id is None:
            variant_id = random.randint(0, len(self.SCALE_VARIANTS) - 1)
        self.variant_id = variant_id

        # Try to load 3D model
        self.using_3d_model = self._try_load_glb_model(config)

        # If model failed, just use a simple cube (no complex primitives)
        if not self.using_3d_model:
            self.model = 'cube'
            self.scale = (0.5, 2, 0.5)
            self.color = color.rgb(100, 140, 100)  # Green for zombie

        # Set up collider
        self.collider = 'box'

        # Animation state
        self.anim_time = 0
        self.walk_cycle = 0  # For walking animation

        # Animation tracking
        self.target_rotation_y = 180  # Store the direction we should face
        self._current_bob = 0  # Track current vertical bob offset

        # No separate arm entities - model already has arms in T-pose
        # Animation is done through body movement (lean, sway, bob)
        self.left_arm_entity = None
        self.right_arm_entity = None

    def _try_load_glb_model(self, config):
        """Try to load the OBJ model with variant modifications."""
        try:
            from ursina import load_model, load_texture

            # Select model variant
            model_name = self.ZOMBIE_VARIANTS[0]  # Currently only one model

            # Load the OBJ model using just the name (Ursina searches asset folders)
            loaded_model = load_model(model_name, use_deepcopy=True)

            if loaded_model:
                self.model = loaded_model

                # Apply scale variant
                base_scale = self.SCALE_VARIANTS[self.variant_id % len(self.SCALE_VARIANTS)]
                self.scale = base_scale
                self.rotation_y = 180

                # Always apply texture - don't use color tint as it overrides texture
                try:
                    tex = load_texture('assets/models/peopleColors.png')
                    if tex:
                        self.texture = tex
                    else:
                        self.texture = 'assets/models/peopleColors.png'
                except Exception as tex_err:
                    print(f"Texture load error: {tex_err}")
                    self.texture = 'assets/models/peopleColors.png'

                # Don't apply color tint - it overrides the texture
                # Keep original texture colors
                self.color = color.white

                return True
            else:
                return False

        except Exception as e:
            print(f"Model load failed: {e}")
            return False

    def _create_zombie_model(self):
        """Create a zombie-looking humanoid from colored primitives."""
        # Zombie skin colors - pale greenish/grayish
        skin_color = color.rgb(140, 160, 130)  # Pale green zombie skin
        dark_skin = color.rgb(100, 120, 90)    # Darker areas
        cloth_color = color.rgb(60, 50, 45)    # Torn clothes - dark brown
        blood_color = color.rgb(80, 30, 30)    # Blood stains

        # Torso (main body)
        self.model = 'cube'
        self.scale = (0.6, 1.2, 0.35)
        self.color = cloth_color

        # Head - slightly larger, zombie-like
        self.head = Entity(
            parent=self,
            model='sphere',
            scale=(0.7, 0.6, 0.6),
            position=(0, 0.9, 0),
            color=skin_color
        )

        # Sunken eyes area (dark patches)
        self.eye_left = Entity(
            parent=self.head,
            model='sphere',
            scale=(0.2, 0.15, 0.1),
            position=(-0.2, 0.1, 0.4),
            color=color.rgb(30, 30, 30)
        )
        self.eye_right = Entity(
            parent=self.head,
            model='sphere',
            scale=(0.2, 0.15, 0.1),
            position=(0.2, 0.1, 0.4),
            color=color.rgb(30, 30, 30)
        )

        # Arms - reaching forward (zombie pose)
        self.left_arm = Entity(
            parent=self,
            model='cube',
            scale=(0.18, 0.7, 0.18),
            position=(-0.55, 0.3, 0.15),
            rotation=(45, 0, -10),  # Arms forward
            color=skin_color
        )

        self.right_arm = Entity(
            parent=self,
            model='cube',
            scale=(0.18, 0.7, 0.18),
            position=(0.55, 0.3, 0.15),
            rotation=(45, 0, 10),
            color=skin_color
        )

        # Hands
        self.left_hand = Entity(
            parent=self.left_arm,
            model='sphere',
            scale=(0.7, 0.5, 0.9),
            position=(0, -0.55, 0),
            color=dark_skin
        )

        self.right_hand = Entity(
            parent=self.right_arm,
            model='sphere',
            scale=(0.7, 0.5, 0.9),
            position=(0, -0.55, 0),
            color=dark_skin
        )

        # Legs
        self.left_leg = Entity(
            parent=self,
            model='cube',
            scale=(0.22, 0.8, 0.22),
            position=(-0.2, -1.0, 0),
            color=cloth_color
        )

        self.right_leg = Entity(
            parent=self,
            model='cube',
            scale=(0.22, 0.8, 0.22),
            position=(0.2, -1.0, 0),
            color=cloth_color
        )

        # Blood stain on torso
        self.blood_stain = Entity(
            parent=self,
            model='quad',
            scale=(0.3, 0.3),
            position=(0.1, 0.2, 0.19),
            color=blood_color
        )

    def update(self):
        """Update with smooth walking animation."""
        super().update()

        # Animate based on model type
        if self.is_alive:
            if self.using_3d_model:
                self._animate_3d_model()
            elif hasattr(self, 'left_leg'):
                self._animate()

    def _animate_3d_model(self):
        """Procedural walking animation for 3D model (no skeleton)."""
        from entities.enemy import EnemyState

        # Get base Y position (current Y minus any bob we applied)
        base_y = self.y - self._current_bob

        if self.state == EnemyState.CHASE:
            # Walking/shambling animation
            self.walk_cycle += time.dt * 6  # Walking speed

            # Vertical bob - simulates stepping
            new_bob = math.sin(self.walk_cycle * 2) * 0.08
            self.y = base_y + new_bob
            self._current_bob = new_bob

            # Side-to-side sway - zombie shamble
            sway = math.sin(self.walk_cycle) * 4
            self.rotation_z = sway

            # Forward lean while walking
            lean = 8 + math.sin(self.walk_cycle * 2) * 3
            self.rotation_x = lean

            # Face target with subtle wobble
            wobble = math.sin(self.walk_cycle * 0.7) * 3
            self.rotation_y = self.target_rotation_y + wobble

        elif self.state == EnemyState.ATTACK:
            # Attack animation - lunge forward
            self.walk_cycle += time.dt * 10

            # Aggressive forward lean
            attack_lean = 15 + math.sin(self.walk_cycle) * 10
            self.rotation_x = attack_lean

            # Quick side movement during attack
            self.rotation_z = math.sin(self.walk_cycle * 2) * 5

            # Bob during attack
            new_bob = abs(math.sin(self.walk_cycle)) * 0.1
            self.y = base_y + new_bob
            self._current_bob = new_bob

            # Face target
            self.rotation_y = self.target_rotation_y

        else:  # IDLE
            # Subtle idle animation - breathing/swaying
            self.walk_cycle += time.dt * 1.5

            # Gentle sway
            sway = math.sin(self.walk_cycle) * 2
            self.rotation_z = sway

            # Slight breathing bob
            new_bob = math.sin(self.walk_cycle * 0.8) * 0.02
            self.y = base_y + new_bob
            self._current_bob = new_bob

            # Reset lean
            self.rotation_x = math.sin(self.walk_cycle * 0.5) * 2

            # Idle facing with subtle variation
            self.rotation_y = self.target_rotation_y + math.sin(self.walk_cycle * 0.3) * 1

    def _animate(self):
        """Smooth zombie shamble animation."""
        from entities.enemy import EnemyState

        if self.state == EnemyState.CHASE:
            self.anim_time += time.dt * 5

            # Leg walking motion
            leg_swing = math.sin(self.anim_time) * 30
            self.left_leg.rotation_x = leg_swing
            self.right_leg.rotation_x = -leg_swing

            # Arm swing (arms mostly forward, slight movement)
            arm_swing = math.sin(self.anim_time) * 8
            self.left_arm.rotation_x = 45 + arm_swing
            self.right_arm.rotation_x = 45 - arm_swing

            # Head bob
            self.head.y = 0.9 + math.sin(self.anim_time * 2) * 0.03

            # Subtle body sway
            self.rotation_z = math.sin(self.anim_time * 0.5) * 3

        elif self.state == EnemyState.ATTACK:
            self.anim_time += time.dt * 8

            # Attack lunge
            lunge = abs(math.sin(self.anim_time)) * 40
            self.left_arm.rotation_x = 45 + lunge
            self.right_arm.rotation_x = 45 + lunge

        else:  # IDLE
            self.anim_time += time.dt * 2

            # Subtle breathing/swaying
            sway = math.sin(self.anim_time) * 2
            self.rotation_z = sway

            # Reset limbs
            if hasattr(self, 'left_leg'):
                self.left_leg.rotation_x = 0
                self.right_leg.rotation_x = 0
                self.left_arm.rotation_x = 45
                self.right_arm.rotation_x = 45

    def look_at_target(self):
        """Override to store target rotation without resetting animation rotations."""
        if not self.target:
            return

        # Calculate angle to target
        direction = self.target.position - self.position
        direction.y = 0

        if direction.length() > 0:
            # Calculate the Y rotation needed to face target
            import math as m
            angle = m.atan2(direction.x, direction.z)
            self.target_rotation_y = m.degrees(angle) + 180  # +180 because model faces backward

            # For 3D model, we apply rotation in the animation method
            # For primitive model, use standard look_at
            if not self.using_3d_model:
                self.look_at(self.position + direction)
                self.rotation_x = 0
                self.rotation_z = 0

    def perform_attack(self):
        """Zombie melee attack."""
        if not self.target or not hasattr(self.target, 'take_damage'):
            return

        if self.distance_to_target() <= self.attack_range:
            self.target.take_damage(self.damage, source=self)

    def on_death(self):
        """Handle zombie death."""
        # Call parent death handler
        super().on_death()
