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
    SCORE_REWARD_STEP, SCORE_REWARD_HEAL, SCORE_REWARD_AMMO
)
import game_state


class Game:
    """Main game controller that manages all game systems."""

    def __init__(self):
        self.state = GameState.MENU
        self.player = None
        self.enemies = []
        self.pickups = []
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

        # Add some pillars for cover
        pillar_positions = [
            (-10, 0, 10), (10, 0, 10), (-10, 0, -10), (10, 0, -10),
            (0, 0, 15), (0, 0, -15), (15, 0, 0), (-15, 0, 0),
        ]

        for pos in pillar_positions:
            pillar = Entity(
                model='cube',
                position=(pos[0], WALL_HEIGHT/2, pos[2]),
                scale=(2, WALL_HEIGHT, 2),
                color=color.brown,
                collider='box'
            )
            self.level_geometry.append(pillar)

        # Spawn/pickup points used by the wave director.
        self.spawn_points = [
            (20, 0, 20), (-20, 0, 20), (20, 0, -20), (-20, 0, -20),
            (0, 0, 22), (22, 0, 0), (-22, 0, 0), (0, 0, -22),
            (-8, 0, 22), (8, 0, -22), (22, 0, 8), (-22, 0, -8),
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

    def _spawn_wave_enemy(self):
        """Spawn one enemy using the spawn director."""
        from entities.enemies.zombie import Zombie

        position = self._choose_spawn_position()
        enemy = Zombie(position=position)
        enemy.target = self.player

        # Mild wave scaling.
        wave_index = max(0, self.current_wave - 1)
        enemy.damage = int(enemy.damage * (1 + (0.08 * wave_index)))
        enemy.speed = enemy.speed * (1 + (0.04 * wave_index))
        enemy._max_health = int(enemy._max_health * (1 + (0.12 * wave_index)))
        enemy._health = enemy._max_health

        self.enemies.append(enemy)
        self.wave_spawned_enemies += 1

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

            if dist_to_player > fallback_distance:
                fallback = position
                fallback_distance = dist_to_player

            if not self._has_line_of_sight_from_player(position):
                return position

        return fallback

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
        mouse.locked = False
        mouse.visible = True
        if self.menu:
            self.menu.show_game_over(self.score)

    def victory(self):
        """Handle successful completion of all waves."""
        self.state = GameState.VICTORY
        self.wave_in_progress = False
        mouse.locked = False
        mouse.visible = True
        if self.menu:
            self.menu.show_victory(score=self.score, waves=self.current_wave)

    def restart(self):
        """Restart the game."""
        # Cleanup
        if self.player:
            destroy(self.player)
        self.clear_enemies()
        self.clear_pickups()
        if self.hud:
            self.hud.cleanup()

        # Start fresh
        self.start_game()

    def quit_game(self):
        """Quit to main menu or exit."""
        application.quit()

    def update(self):
        """Main game update loop."""
        if self.state != GameState.PLAYING:
            return

        # Remove dead entities from active lists.
        self.enemies = [e for e in self.enemies if e and e.is_alive]
        self.pickups = [p for p in self.pickups if p and p.enabled]

        # Check player death
        if self.player and not self.player.is_alive:
            self.game_over()
            return

        self._update_wave_progress()
        self._update_pickup_spawner()

    def on_enemy_killed(self, enemy):
        """Called when an enemy is killed."""
        self.score += 10

        while self.score >= self.next_score_reward:
            self._grant_score_reward()
            self.next_score_reward += SCORE_REWARD_STEP

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
