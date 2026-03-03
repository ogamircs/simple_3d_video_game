"""
Doom-like FPS Game - Main Entry Point
A first-person shooter with enemies that chase you, shooting mechanics, and health.
"""
import random
from ursina import *
from config import (
    WINDOW_TITLE, FULLSCREEN, SHOW_FPS,
    GameState, DEFAULT_LEVEL_SIZE, WALL_HEIGHT, RuntimeSettings,
    MAX_WAVES, BASE_ENEMIES_PER_WAVE, ENEMIES_PER_WAVE_STEP,
    BASE_SPAWN_INTERVAL, SPAWN_INTERVAL_DECAY, MIN_SPAWN_INTERVAL,
    WAVE_BREAK_DURATION, SPAWN_MIN_PLAYER_DISTANCE, SPAWN_DIRECTOR_LOS_ATTEMPTS,
    PICKUP_MAX_ACTIVE, PICKUP_SPAWN_COOLDOWN, HEALTH_PICKUP_VALUE, AMMO_PICKUP_VALUE,
    SCORE_REWARD_STEP, SCORE_REWARD_HEAL, SCORE_REWARD_AMMO,
    ARENA_LAYOUT_VARIANTS, EXPLOSIVE_BARRELS_PER_LAYOUT, FLOOR_TRAPS_PER_LAYOUT,
    SPAWN_BLOCKER_RADIUS, SPAWN_BLOCKERS
)
import game_state
from core.event_bus import EventBus
from core.services import Services
from systems.audio_manager import AudioManager
from systems.telemetry import Telemetry


class Game:
    """Main game controller that manages all game systems."""

    def __init__(self):
        self.state = GameState.MENU
        self.player = None
        self.enemies = []
        self.pickups = []
        self.hazards = []
        self.level_geometry = []
        self.hud = None
        self.menu = None
        self.score = 0
        self.max_waves = MAX_WAVES
        self.current_wave = 0
        self.wave_in_progress = False
        self.wave_break_timer = 0
        self.wave_spawn_timer = 0
        self.wave_spawn_interval = BASE_SPAWN_INTERVAL
        self.wave_target_enemies = 0
        self.wave_spawned_enemies = 0
        self.pickup_spawn_timer = 0
        self.next_score_reward = SCORE_REWARD_STEP
        self.spawn_points = []
        self.pickup_points = []
        self.layout_variant = 0

        # Shared services (P5 decoupling).
        Services.event_bus = EventBus()
        Services.telemetry = Telemetry()
        Services.audio_manager = AudioManager()

        Services.event_bus.subscribe('enemy_killed', self._on_enemy_killed_event)
        Services.event_bus.subscribe('damage_applied', self._on_damage_event)

    def apply_runtime_settings(self, rebuild_hud=False):
        """Apply mutable settings changed from the options panel."""
        from ursina.audio import Audio

        window.fullscreen = RuntimeSettings.fullscreen
        camera.fov = RuntimeSettings.fov
        Audio.volume_multiplier = RuntimeSettings.audio_volume

        if self.player:
            self.player.set_mouse_sensitivity(RuntimeSettings.mouse_sensitivity)

        if rebuild_hud and self.player and self.hud:
            from ui.hud import HUD
            self.hud.cleanup()
            self.hud = HUD(self.player)

    def start_game(self):
        """Initialize and start a new game."""
        self.state = GameState.PLAYING
        self.score = 0
        self.current_wave = 0
        self.wave_in_progress = False
        self.wave_break_timer = 0
        self.wave_spawn_timer = 0
        self.wave_target_enemies = 0
        self.wave_spawned_enemies = 0
        self.pickup_spawn_timer = 0
        self.next_score_reward = SCORE_REWARD_STEP

        # Hide menu if exists
        if self.menu:
            self.menu.hide()

        # Create level
        self.create_level()

        # Create player
        from entities.player import Player
        self.player = Player()

        # Create HUD
        from ui.hud import HUD
        self.hud = HUD(self.player)

        # Apply live-configurable options (FOV, sensitivity, volume, UI scale)
        self.apply_runtime_settings()

        # Clear entities from any prior run and start wave progression
        self.clear_enemies()
        self.clear_pickups()
        if Services.audio_manager:
            Services.audio_manager.start_layers()
        self.start_wave(1)

        # Lock mouse for FPS controls
        mouse.locked = True
        mouse.visible = False

    def create_level(self):
        """Create the game level with floor and walls."""
        # Clear existing geometry
        for entity in self.level_geometry:
            destroy(entity)
        self.level_geometry = []

        # Floor
        floor = Entity(
            model='plane',
            scale=DEFAULT_LEVEL_SIZE,
            color=color.dark_gray,
            texture='white_cube',
            texture_scale=(DEFAULT_LEVEL_SIZE, DEFAULT_LEVEL_SIZE),
            collider='box'
        )
        self.level_geometry.append(floor)

        # Ceiling (optional, adds atmosphere)
        ceiling = Entity(
            model='plane',
            scale=DEFAULT_LEVEL_SIZE,
            y=WALL_HEIGHT,
            rotation_x=180,
            color=color.gray,
            texture='white_cube',
            texture_scale=(DEFAULT_LEVEL_SIZE, DEFAULT_LEVEL_SIZE)
        )
        self.level_geometry.append(ceiling)

        # Walls
        wall_positions = [
            {'pos': (0, WALL_HEIGHT/2, DEFAULT_LEVEL_SIZE/2), 'scale': (DEFAULT_LEVEL_SIZE, WALL_HEIGHT, 1)},      # North
            {'pos': (0, WALL_HEIGHT/2, -DEFAULT_LEVEL_SIZE/2), 'scale': (DEFAULT_LEVEL_SIZE, WALL_HEIGHT, 1)},     # South
            {'pos': (DEFAULT_LEVEL_SIZE/2, WALL_HEIGHT/2, 0), 'scale': (1, WALL_HEIGHT, DEFAULT_LEVEL_SIZE)},      # East
            {'pos': (-DEFAULT_LEVEL_SIZE/2, WALL_HEIGHT/2, 0), 'scale': (1, WALL_HEIGHT, DEFAULT_LEVEL_SIZE)},     # West
        ]

        for wall_data in wall_positions:
            wall = Entity(
                model='cube',
                position=wall_data['pos'],
                scale=wall_data['scale'],
                color=color.light_gray,
                texture='white_cube',
                texture_scale=(wall_data['scale'][0]/2, wall_data['scale'][1]/2),
                collider='box'
            )
            self.level_geometry.append(wall)

        # Procedural arena variant with lane-friendly cover placement.
        self.layout_variant = random.randint(0, ARENA_LAYOUT_VARIANTS - 1)
        if self.layout_variant == 0:
            pillar_positions = [(-12, 0, 12), (12, 0, 12), (-12, 0, -12), (12, 0, -12), (0, 0, 16), (0, 0, -16)]
        elif self.layout_variant == 1:
            pillar_positions = [(-16, 0, 0), (16, 0, 0), (-8, 0, 14), (8, 0, 14), (-8, 0, -14), (8, 0, -14)]
        else:
            pillar_positions = [(-14, 0, 8), (14, 0, 8), (-14, 0, -8), (14, 0, -8), (0, 0, 18), (0, 0, -18)]

        for pos in pillar_positions:
            pillar = Entity(
                model='cube',
                position=(pos[0], WALL_HEIGHT / 2, pos[2]),
                scale=(2.1, WALL_HEIGHT, 2.1),
                color=color.brown,
                collider='box'
            )
            self.level_geometry.append(pillar)

        # Lane walls create safer/reachable traversal routes through arena center.
        lane_walls = [
            (-6, WALL_HEIGHT / 2, 0, 1, WALL_HEIGHT, 10),
            (6, WALL_HEIGHT / 2, 0, 1, WALL_HEIGHT, 10),
        ]
        if self.layout_variant == 1:
            lane_walls = [
                (0, WALL_HEIGHT / 2, -6, 10, WALL_HEIGHT, 1),
                (0, WALL_HEIGHT / 2, 6, 10, WALL_HEIGHT, 1),
            ]
        for lx, ly, lz, sx, sy, sz in lane_walls:
            lane = Entity(
                model='cube',
                position=(lx, ly, lz),
                scale=(sx, sy, sz),
                color=color.rgb(100, 90, 90),
                collider='box'
            )
            self.level_geometry.append(lane)

        self._spawn_hazards()

        # Spawn/pickup points used by the wave director.
        self.spawn_points = [
            (20, 0, 20), (-20, 0, 20), (20, 0, -20), (-20, 0, -20),
            (0, 0, 22), (22, 0, 0), (-22, 0, 0), (0, 0, -22),
            (-8, 0, 22), (8, 0, -22), (22, 0, 8), (-22, 0, -8),
            (17, 0, 14), (-17, 0, -14), (14, 0, -17), (-14, 0, 17),
        ]
        self.pickup_points = [
            (-12, 0.6, 0), (12, 0.6, 0), (0, 0.6, 12), (0, 0.6, -12),
            (-8, 0.6, 8), (8, 0.6, -8), (-8, 0.6, -8), (8, 0.6, 8),
            (0, 0.6, 0)
        ]

    def clear_enemies(self):
        """Destroy all active enemies."""
        for enemy in self.enemies:
            if enemy:
                destroy(enemy)
        self.enemies = []

    def clear_pickups(self):
        """Destroy all active pickups."""
        for pickup in self.pickups:
            if pickup:
                destroy(pickup)
        self.pickups = []

    def clear_hazards(self):
        """Destroy active hazards."""
        for hazard in self.hazards:
            if hazard:
                destroy(hazard)
        self.hazards = []

    def _spawn_hazards(self):
        """Place interactive hazards into the active arena layout."""
        from entities.hazards import ExplosiveBarrel, FloorTrap, TimedDoor

        self.clear_hazards()
        barrel_positions = [(-18, 0.7, 4), (18, 0.7, -4), (-4, 0.7, -18), (4, 0.7, 18), (0, 0.7, 14), (0, 0.7, -14)]
        trap_positions = [(-10, 0.02, 0), (10, 0.02, 0), (0, 0.02, 10), (0, 0.02, -10), (0, 0.02, 0)]

        random.shuffle(barrel_positions)
        random.shuffle(trap_positions)

        for pos in barrel_positions[:EXPLOSIVE_BARRELS_PER_LAYOUT]:
            barrel = ExplosiveBarrel(position=pos)
            self.hazards.append(barrel)

        for pos in trap_positions[:FLOOR_TRAPS_PER_LAYOUT]:
            trap = FloorTrap(position=pos)
            self.hazards.append(trap)

        door_positions = [(-2, 1.6, 0), (2, 1.6, 0)]
        for pos in door_positions:
            door = TimedDoor(position=pos)
            self.hazards.append(door)

    def start_wave(self, wave_number):
        """Initialize a wave with scaling enemy count and spawn pace."""
        if wave_number > self.max_waves:
            self.victory()
            return

        self.current_wave = wave_number
        self.wave_in_progress = True
        self.wave_break_timer = 0
        self.wave_spawn_timer = 0
        self.wave_target_enemies = BASE_ENEMIES_PER_WAVE + ((wave_number - 1) * ENEMIES_PER_WAVE_STEP)
        self.wave_spawned_enemies = 0
        self.wave_spawn_interval = max(
            MIN_SPAWN_INTERVAL,
            BASE_SPAWN_INTERVAL - ((wave_number - 1) * SPAWN_INTERVAL_DECAY)
        )

        if self.hud:
            self.hud.show_event(f'Wave {wave_number} started', duration=2.0)
        if Services.event_bus:
            Services.event_bus.emit('wave_started', wave=wave_number, target=self.wave_target_enemies)
        if Services.telemetry:
            Services.telemetry.log('wave_started', wave=wave_number, target=self.wave_target_enemies)

    def _spawn_wave_enemy(self):
        """Spawn one enemy using the spawn director."""
        from entities.enemies.zombie import Zombie
        from entities.enemies.demon import Demon
        from entities.enemies.imp import Imp

        position = self._choose_spawn_position()
        enemy_cls = Zombie
        elite = False

        # Wave-based roster unlocks.
        roll = random.random()
        if self.current_wave >= 3 and roll > 0.72:
            enemy_cls = Demon
            elite = True
        elif self.current_wave >= 2 and roll > 0.55:
            enemy_cls = Imp
            elite = True

        enemy = enemy_cls(position=position)
        enemy.target = self.player

        # Mild wave scaling.
        wave_index = max(0, self.current_wave - 1)
        enemy.damage = int(enemy.damage * (1 + (0.08 * wave_index)))
        enemy.speed = enemy.speed * (1 + (0.04 * wave_index))
        enemy._max_health = int(enemy._max_health * (1 + (0.12 * wave_index)))
        enemy._health = enemy._max_health

        self.enemies.append(enemy)
        self.wave_spawned_enemies += 1

        if elite and self.hud:
            self.hud.show_event(f'{enemy.enemy_type.upper()} spawned', duration=1.5)
        if Services.telemetry:
            Services.telemetry.log(
                'enemy_spawned',
                enemy_type=enemy.enemy_type,
                wave=self.current_wave,
                x=round(enemy.x, 2),
                z=round(enemy.z, 2)
            )

    def _choose_spawn_position(self):
        """Choose a spawn point away from player LOS when possible."""
        if not self.player or not self.spawn_points:
            return (15, 0, 15)

        candidates = list(self.spawn_points)
        random.shuffle(candidates)
        fallback = candidates[0]
        fallback_distance = -1

        for index, position in enumerate(candidates):
            if index >= SPAWN_DIRECTOR_LOS_ATTEMPTS:
                break

            dist_to_player = distance(Vec3(*position), self.player.position)
            if dist_to_player < SPAWN_MIN_PLAYER_DISTANCE:
                continue
            if self._is_in_spawn_blocker(position):
                continue

            if dist_to_player > fallback_distance:
                fallback = position
                fallback_distance = dist_to_player

            if not self._has_line_of_sight_from_player(position):
                return position

        return fallback

    def _is_in_spawn_blocker(self, position):
        """Prevent unfair near-center spawns around blocker zones."""
        for blocker in SPAWN_BLOCKERS:
            if distance(Vec3(*position), Vec3(*blocker)) <= SPAWN_BLOCKER_RADIUS:
                if self.player and distance(self.player.position, Vec3(*blocker)) < SPAWN_BLOCKER_RADIUS * 1.5:
                    return True
        return False

    def _has_line_of_sight_from_player(self, position):
        """Return True if the player has direct line of sight to position."""
        if not self.player:
            return False

        origin = self.player.world_position + Vec3(0, 1, 0)
        target = Vec3(position[0], 1, position[2])
        ray = target - origin
        dist = ray.length()
        if dist <= 0.1:
            return True

        hit_info = raycast(
            origin=origin,
            direction=ray.normalized(),
            distance=max(0.1, dist - 0.5),
            ignore=[self.player]
        )
        return not hit_info.hit

    def wave_enemies_remaining(self):
        """Total enemies left in this wave (alive + queued spawns)."""
        unspawned = max(0, self.wave_target_enemies - self.wave_spawned_enemies)
        return len(self.enemies) + unspawned

    def _update_wave_progress(self):
        """Drive spawning and wave transition timing."""
        if self.wave_in_progress:
            self.wave_spawn_timer += time.dt

            if self.wave_spawned_enemies < self.wave_target_enemies and self.wave_spawn_timer >= self.wave_spawn_interval:
                self.wave_spawn_timer = 0
                self._spawn_wave_enemy()

            if self.wave_spawned_enemies >= self.wave_target_enemies and not self.enemies:
                self.wave_in_progress = False
                if self.current_wave >= self.max_waves:
                    self.victory()
                    return
                self.wave_break_timer = WAVE_BREAK_DURATION
                if self.hud:
                    self.hud.show_event('Wave cleared', duration=1.8)
                if Services.telemetry:
                    Services.telemetry.log('wave_cleared', wave=self.current_wave, score=self.score)

            return

        if self.wave_break_timer > 0:
            self.wave_break_timer -= time.dt
            if self.wave_break_timer <= 0:
                self.start_wave(self.current_wave + 1)

    def _choose_pickup_type(self):
        """Choose pickup based on player needs."""
        if self.player and self.player.health < 45:
            return 'health'

        weapon = self.player.current_weapon if self.player else None
        if weapon and weapon.ammo_current <= int(weapon.ammo_max * 0.3):
            return 'ammo'

        return random.choice(['health', 'ammo'])

    def _choose_pickup_position(self):
        """Choose pickup location away from player center."""
        if not self.pickup_points:
            return (0, 0.6, 0)
        if not self.player:
            return random.choice(self.pickup_points)

        candidates = list(self.pickup_points)
        random.shuffle(candidates)
        best = candidates[0]
        best_distance = -1
        for pos in candidates:
            dist_to_player = distance(Vec3(*pos), self.player.position)
            if dist_to_player > best_distance:
                best = pos
                best_distance = dist_to_player
            if dist_to_player >= 8:
                return pos
        return best

    def spawn_pickup(self):
        """Spawn health/ammo pickup based on player state and cooldown rules."""
        from entities.pickup import Pickup

        pickup_type = self._choose_pickup_type()
        pickup_value = HEALTH_PICKUP_VALUE if pickup_type == 'health' else AMMO_PICKUP_VALUE
        pickup = Pickup(
            pickup_type=pickup_type,
            value=pickup_value,
            position=self._choose_pickup_position(),
            target=self.player,
            on_collected=self.on_pickup_collected
        )
        self.pickups.append(pickup)

    def _update_pickup_spawner(self):
        """Spawn pickups on cooldown while respecting max active count."""
        if not self.player or not self.player.is_alive:
            return
        if len(self.pickups) >= PICKUP_MAX_ACTIVE:
            return

        self.pickup_spawn_timer += time.dt
        if self.pickup_spawn_timer >= PICKUP_SPAWN_COOLDOWN:
            self.pickup_spawn_timer = 0
            self.spawn_pickup()

    def on_pickup_collected(self, pickup, player):
        """Show pickup feedback in HUD."""
        if Services.event_bus:
            Services.event_bus.emit('pickup_collected', pickup_type=pickup.pickup_type, value=pickup.value)
        if Services.telemetry:
            Services.telemetry.log('pickup_collected', pickup_type=pickup.pickup_type, value=pickup.value)

        if not self.hud:
            return
        if pickup.pickup_type == 'health':
            self.hud.show_event(f'Picked health (+{pickup.value})', duration=1.6)
        else:
            self.hud.show_event(f'Picked ammo (+{pickup.value})', duration=1.6)

    def pause(self):
        """Pause the game."""
        if self.state == GameState.PLAYING:
            self.state = GameState.PAUSED
            mouse.locked = False
            mouse.visible = True
            if self.menu:
                self.menu.show_pause()

    def resume(self):
        """Resume the game from pause."""
        if self.state == GameState.PAUSED:
            self.state = GameState.PLAYING
            mouse.locked = True
            mouse.visible = False
            if self.menu:
                self.menu.hide()

    def game_over(self):
        """Handle game over state."""
        self.state = GameState.GAME_OVER
        self.wave_in_progress = False
        if Services.audio_manager:
            Services.audio_manager.stop()
        mouse.locked = False
        mouse.visible = True
        if self.menu:
            self.menu.show_game_over(self.score)
        if Services.telemetry:
            Services.telemetry.log('game_over', score=self.score, wave=self.current_wave)

    def victory(self):
        """Handle successful completion of all waves."""
        self.state = GameState.VICTORY
        self.wave_in_progress = False
        if Services.audio_manager:
            Services.audio_manager.stop()
        mouse.locked = False
        mouse.visible = True
        if self.menu:
            self.menu.show_victory(score=self.score, waves=self.current_wave)
        if self.hud:
            self.hud.show_event('Objective complete!', duration=2.5)
        if Services.telemetry:
            Services.telemetry.log('victory', score=self.score, wave=self.current_wave)

    def restart(self):
        """Restart the game."""
        # Cleanup
        if self.player:
            destroy(self.player)
        self.clear_enemies()
        self.clear_pickups()
        self.clear_hazards()
        if self.hud:
            self.hud.cleanup()
        if Services.audio_manager:
            Services.audio_manager.stop()

        # Start fresh
        self.start_game()

    def quit_game(self):
        """Quit to main menu or exit."""
        if Services.audio_manager:
            Services.audio_manager.stop()
        application.quit()

    def update(self):
        """Main game update loop."""
        if self.state != GameState.PLAYING:
            return

        # Remove dead entities from active lists.
        self.enemies = [e for e in self.enemies if e and e.is_alive]
        self.pickups = [p for p in self.pickups if p and p.enabled]
        self.hazards = [h for h in self.hazards if h and h.enabled]

        # Check player death
        if self.player and not self.player.is_alive:
            self.game_over()
            return

        self._update_wave_progress()
        self._update_pickup_spawner()
        if Services.audio_manager and self.player:
            Services.audio_manager.update_layers(
                enemies_alive=len(self.enemies),
                player_health_pct=self.player.health_percentage
            )

    def on_enemy_killed(self, enemy):
        """Called when an enemy is killed."""
        self.score += 10
        if Services.telemetry:
            Services.telemetry.log('score_changed', score=self.score)

        while self.score >= self.next_score_reward:
            self._grant_score_reward()
            self.next_score_reward += SCORE_REWARD_STEP

    def _on_enemy_killed_event(self, enemy):
        """Event-bus callback for enemy kill notifications."""
        # Placeholder hook keeps event bus connected for future systems.
        _ = enemy

    def _on_damage_event(self, damage, headshot, target, source):
        """Event-bus callback for damage notifications."""
        _ = (damage, headshot, target, source)

    def _grant_score_reward(self):
        """Convert score milestones into survivability utility."""
        if not self.player:
            return

        healed = int(self.player.heal(SCORE_REWARD_HEAL))
        ammo_added = 0
        weapon = self.player.current_weapon
        if weapon:
            before = weapon.ammo_current
            weapon.ammo_current = min(weapon.ammo_max, weapon.ammo_current + SCORE_REWARD_AMMO)
            ammo_added = weapon.ammo_current - before

        if self.hud:
            self.hud.show_event(
                f'Score reward: +{healed} HP +{ammo_added} ammo',
                duration=2.2
            )


# Global game instance (for backwards compatibility)
game = None


def update():
    """Global update function called every frame."""
    if game_state.game:
        game_state.game.update()


def input(key):
    """Global input handler."""
    if not game_state.game:
        return

    if key == 'escape':
        if game_state.game.state == GameState.PLAYING:
            game_state.game.pause()
        elif game_state.game.state == GameState.PAUSED:
            if game_state.game.menu and game_state.game.menu.mode == 'options':
                game_state.game.menu.on_options_back()
            else:
                game_state.game.resume()


def main():
    """Main entry point."""
    global game

    # Initialize Ursina
    app = Ursina(
        title=WINDOW_TITLE,
        fullscreen=FULLSCREEN,
        development_mode=False
    )

    # Configure window
    window.color = color.black
    window.exit_button.visible = False
    window.fps_counter.enabled = SHOW_FPS

    # Add sky for atmosphere
    Sky(color=color.rgb(40, 40, 50))

    # Create game instance and store in game_state
    game = Game()
    game_state.game = game
    if Services.audio_manager:
        Services.audio_manager.preload_sounds()
    game.apply_runtime_settings()

    # Create menu
    from ui.menu import MainMenu
    game.menu = MainMenu(game)

    # Show main menu initially
    game.state = GameState.MENU

    # Run game
    app.run()


if __name__ == '__main__':
    main()
