"""
Menu System
Main menu, pause menu, and game over screen.
"""
from ursina import (
    Entity, Text, Button, camera, color,
    destroy, mouse, application
)


class MainMenu(Entity):
    """Main menu with start game and quit options."""

    def __init__(self, game, **kwargs):
        super().__init__(parent=camera.ui, **kwargs)

        self.game = game

        # Background overlay
        self.background = Entity(
            parent=self,
            model='quad',
            color=color.rgba(0, 0, 0, 200),
            scale=3,
            z=1
        )

        # Title
        self.title = Text(
            parent=self,
            text='BLASTER BUDDIES',
            position=(0, 0.35),
            origin=(0, 0),
            scale=3,
            color=color.red
        )

        # Subtitle
        self.subtitle = Text(
            parent=self,
            text='Pew pew adventure!',
            position=(0, 0.2),
            origin=(0, 0),
            scale=1.5,
            color=color.light_gray
        )

        # Buttons container
        self.buttons = []

        # Start button
        self.start_button = MenuButton(
            parent=self,
            text='START GAME',
            position=(0, 0),
            on_click=self.on_start
        )
        self.buttons.append(self.start_button)

        # Quit button
        self.quit_button = MenuButton(
            parent=self,
            text='QUIT',
            position=(0, -0.15),
            on_click=self.on_quit
        )
        self.buttons.append(self.quit_button)

        # Controls hint
        self.controls = Text(
            parent=self,
            text='WASD - Move | Mouse - Look | Click - Shoot | ESC - Pause',
            position=(0, -0.4),
            origin=(0, 0),
            scale=0.8,
            color=color.gray
        )

        # Pause menu elements (hidden initially)
        self.pause_title = Text(
            parent=self,
            text='PAUSED',
            position=(0, 0.25),
            origin=(0, 0),
            scale=3,
            color=color.white,
            enabled=False
        )

        self.resume_button = MenuButton(
            parent=self,
            text='RESUME',
            position=(0, 0.05),
            on_click=self.on_resume,
            enabled=False
        )

        self.restart_button = MenuButton(
            parent=self,
            text='RESTART',
            position=(0, -0.1),
            on_click=self.on_restart,
            enabled=False
        )

        self.quit_to_menu_button = MenuButton(
            parent=self,
            text='QUIT',
            position=(0, -0.25),
            on_click=self.on_quit,
            enabled=False
        )

        # Game over elements (hidden initially)
        self.game_over_title = Text(
            parent=self,
            text='GAME OVER',
            position=(0, 0.25),
            origin=(0, 0),
            scale=4,
            color=color.red,
            enabled=False
        )

        self.final_score = Text(
            parent=self,
            text='Score: 0',
            position=(0, 0.1),
            origin=(0, 0),
            scale=2,
            color=color.white,
            enabled=False
        )

        self.play_again_button = MenuButton(
            parent=self,
            text='PLAY AGAIN',
            position=(0, -0.1),
            on_click=self.on_restart,
            enabled=False
        )

        # Current mode
        self.mode = 'main'  # 'main', 'pause', 'game_over'

    def show_main(self):
        """Show main menu."""
        self.mode = 'main'
        self.enabled = True
        self.background.enabled = True

        # Main menu elements
        self.title.enabled = True
        self.subtitle.enabled = True
        self.controls.enabled = True
        for btn in self.buttons:
            btn.enabled = True

        # Hide other elements
        self.pause_title.enabled = False
        self.resume_button.enabled = False
        self.restart_button.enabled = False
        self.quit_to_menu_button.enabled = False
        self.game_over_title.enabled = False
        self.final_score.enabled = False
        self.play_again_button.enabled = False

        mouse.locked = False
        mouse.visible = True

    def show_pause(self):
        """Show pause menu."""
        self.mode = 'pause'
        self.enabled = True
        self.background.enabled = True

        # Hide main menu elements
        self.title.enabled = False
        self.subtitle.enabled = False
        self.controls.enabled = False
        for btn in self.buttons:
            btn.enabled = False

        # Show pause elements
        self.pause_title.enabled = True
        self.resume_button.enabled = True
        self.restart_button.enabled = True
        self.quit_to_menu_button.enabled = True

        # Hide game over elements
        self.game_over_title.enabled = False
        self.final_score.enabled = False
        self.play_again_button.enabled = False

    def show_game_over(self, score=0):
        """Show game over screen."""
        self.mode = 'game_over'
        self.enabled = True
        self.background.enabled = True

        # Hide other elements
        self.title.enabled = False
        self.subtitle.enabled = False
        self.controls.enabled = False
        for btn in self.buttons:
            btn.enabled = False
        self.pause_title.enabled = False
        self.resume_button.enabled = False
        self.restart_button.enabled = False
        self.quit_to_menu_button.enabled = False

        # Show game over elements
        self.game_over_title.enabled = True
        self.final_score.enabled = True
        self.final_score.text = f'Final Score: {score}'
        self.play_again_button.enabled = True
        self.quit_to_menu_button.enabled = True
        self.quit_to_menu_button.y = -0.25

    def hide(self):
        """Hide the menu."""
        self.enabled = False
        self.background.enabled = False

        # Hide all elements
        self.title.enabled = False
        self.subtitle.enabled = False
        self.controls.enabled = False
        for btn in self.buttons:
            btn.enabled = False
        self.pause_title.enabled = False
        self.resume_button.enabled = False
        self.restart_button.enabled = False
        self.quit_to_menu_button.enabled = False
        self.game_over_title.enabled = False
        self.final_score.enabled = False
        self.play_again_button.enabled = False

    def on_start(self):
        """Start the game."""
        self.hide()
        self.game.start_game()

    def on_resume(self):
        """Resume the game."""
        self.game.resume()

    def on_restart(self):
        """Restart the game."""
        self.hide()
        self.game.restart()

    def on_quit(self):
        """Quit the game."""
        application.quit()


class MenuButton(Button):
    """Styled button for menus."""

    def __init__(self, text='Button', on_click=None, **kwargs):
        super().__init__(
            text=text,
            scale=(0.5, 0.1),
            color=color.dark_gray,
            highlight_color=color.gray,
            pressed_color=color.light_gray,
            **kwargs
        )

        self.text_entity.scale = 5
        self.text_entity.font = 'VeraMono.ttf'
        self.original_text_scale = 5
        self.on_click_callback = on_click

    def on_mouse_enter(self):
        """Keep text size consistent on hover."""
        super().on_mouse_enter()
        self.text_entity.scale = self.original_text_scale

    def on_mouse_exit(self):
        """Keep text size consistent on exit."""
        super().on_mouse_exit()
        self.text_entity.scale = self.original_text_scale

    def on_click(self):
        """Handle button click."""
        if self.on_click_callback:
            self.on_click_callback()
