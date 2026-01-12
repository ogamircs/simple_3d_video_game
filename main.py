"""
Doom-like FPS Game - Main Entry Point
A first-person shooter with enemies that chase you, shooting mechanics, and health.
"""
from ursina import *
from config import (
    WINDOW_TITLE, FULLSCREEN, SHOW_FPS,
    GameState, DEFAULT_LEVEL_SIZE, WALL_HEIGHT
)
import game_state


class Game:
    """Main game controller that manages all game systems."""

    def __init__(self):
        self.state = GameState.MENU
        self.player = None
        self.enemies = []
        self.level_geometry = []
        self.hud = None
        self.menu = None
        self.score = 0

    def start_game(self):
        """Initialize and start a new game."""
        self.state = GameState.PLAYING
        self.score = 0

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

        # Spawn initial enemies
        self.spawn_enemies()

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

    def spawn_enemies(self):
        """Spawn enemies in the level."""
        from entities.enemies.zombie import Zombie

        # Clear existing enemies
        for enemy in self.enemies:
            if enemy:
                destroy(enemy)
        self.enemies = []

        # Spawn positions (away from player spawn at 0,0,0)
        spawn_positions = [
            (15, 0, 15),
            (-15, 0, 15),
            (15, 0, -15),
            (-15, 0, -15),
            (0, 0, 20),
        ]

        for pos in spawn_positions:
            enemy = Zombie(position=pos)
            enemy.target = self.player
            self.enemies.append(enemy)

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

    def restart(self):
        """Restart the game."""
        # Cleanup
        if self.player:
            destroy(self.player)
        for enemy in self.enemies:
            if enemy:
                destroy(enemy)
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

        # Remove dead enemies and check for respawn
        self.enemies = [e for e in self.enemies if e and e.is_alive]

        # Check player death
        if self.player and not self.player.is_alive:
            self.game_over()

    def on_enemy_killed(self, enemy):
        """Called when an enemy is killed."""
        self.score += 10


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

    # Create menu
    from ui.menu import MainMenu
    game.menu = MainMenu(game)

    # Show main menu initially
    game.state = GameState.MENU

    # Run game
    app.run()


if __name__ == '__main__':
    main()
