"""
Menu System
Main menu, pause menu, game over screen, and options panel.
"""
from ursina import (
    Entity, Text, Button, camera, color,
    mouse, application
)
from ursina.prefabs.slider import Slider
from config import (
    UI_FONT_PRIMARY,
    UI_FONT_MONO,
    MENU_TITLE_SCALE,
    MENU_SUBTITLE_SCALE,
    MENU_BODY_TEXT_SCALE,
    MENU_BUTTON_SCALE,
    MENU_BUTTON_TEXT_SCALE,
    RuntimeSettings,
    UI_SCALE_PRESETS
)


class MainMenu(Entity):
    """Main menu with start game, options, and quit."""

    def __init__(self, game, **kwargs):
        super().__init__(parent=camera.ui, **kwargs)

        self.game = game
        self.options_return_mode = 'main'
        self.apply_menu_ui_scale()

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
            scale=MENU_TITLE_SCALE,
            font=UI_FONT_PRIMARY,
            color=color.red
        )

        # Subtitle
        self.subtitle = Text(
            parent=self,
            text='Pew pew adventure!',
            position=(0, 0.2),
            origin=(0, 0),
            scale=MENU_SUBTITLE_SCALE,
            font=UI_FONT_PRIMARY,
            color=color.light_gray
        )

        # Main menu buttons
        self.main_buttons = []
        self.start_button = MenuButton(
            parent=self,
            text='START GAME',
            position=(0, 0.02),
            on_click=self.on_start
        )
        self.main_buttons.append(self.start_button)

        self.options_button = MenuButton(
            parent=self,
            text='OPTIONS',
            position=(0, -0.13),
            on_click=self.on_options
        )
        self.main_buttons.append(self.options_button)

        self.quit_button = MenuButton(
            parent=self,
            text='QUIT',
            position=(0, -0.28),
            on_click=self.on_quit
        )
        self.main_buttons.append(self.quit_button)

        # Controls hint
        self.controls = Text(
            parent=self,
            text='WASD - Move | Mouse - Look | Click - Shoot | ESC - Pause',
            position=(0, -0.43),
            origin=(0, 0),
            scale=MENU_BODY_TEXT_SCALE,
            font=UI_FONT_PRIMARY,
            color=color.gray
        )

        # Pause menu elements (hidden initially)
        self.pause_title = Text(
            parent=self,
            text='PAUSED',
            position=(0, 0.25),
            origin=(0, 0),
            scale=MENU_TITLE_SCALE,
            font=UI_FONT_PRIMARY,
            color=color.white,
            enabled=False
        )

        self.resume_button = MenuButton(
            parent=self,
            text='RESUME',
            position=(0, 0.08),
            on_click=self.on_resume,
            enabled=False
        )

        self.restart_button = MenuButton(
            parent=self,
            text='RESTART',
            position=(0, -0.07),
            on_click=self.on_restart,
            enabled=False
        )

        self.pause_options_button = MenuButton(
            parent=self,
            text='OPTIONS',
            position=(0, -0.22),
            on_click=self.on_options,
            enabled=False
        )

        self.quit_to_menu_button = MenuButton(
            parent=self,
            text='QUIT',
            position=(0, -0.37),
            on_click=self.on_quit,
            enabled=False
        )

        # Game over elements (hidden initially)
        self.game_over_title = Text(
            parent=self,
            text='GAME OVER',
            position=(0, 0.25),
            origin=(0, 0),
            scale=MENU_TITLE_SCALE,
            font=UI_FONT_PRIMARY,
            color=color.red,
            enabled=False
        )

        self.final_score = Text(
            parent=self,
            text='Score: 0',
            position=(0, 0.1),
            origin=(0, 0),
            scale=MENU_SUBTITLE_SCALE,
            font=UI_FONT_PRIMARY,
            color=color.white,
            enabled=False
        )

        self.play_again_button = MenuButton(
            parent=self,
            text='PLAY AGAIN',
            position=(0, -0.08),
            on_click=self.on_restart,
            enabled=False
        )

        # Options panel
        self.options_widgets = []
        self._create_options_panel()

        # Current mode
        self.mode = 'main'  # 'main', 'pause', 'options', 'game_over'
        self.show_main()

    def _create_options_panel(self):
        self.options_title = Text(
            parent=self,
            text='OPTIONS',
            position=(0, 0.31),
            origin=(0, 0),
            scale=MENU_TITLE_SCALE,
            font=UI_FONT_PRIMARY,
            color=color.white,
            enabled=False
        )
        self.options_widgets.append(self.options_title)

        self.ui_scale_label = Text(
            parent=self,
            text='UI SCALE',
            position=(-0.28, 0.16),
            origin=(0, 0),
            scale=MENU_BODY_TEXT_SCALE,
            font=UI_FONT_PRIMARY,
            color=color.light_gray,
            enabled=False
        )
        self.options_widgets.append(self.ui_scale_label)

        self.ui_scale_button = MenuButton(
            parent=self,
            text=self._ui_scale_button_text(),
            position=(0.2, 0.16),
            on_click=self.on_cycle_ui_scale,
            enabled=False
        )
        self.options_widgets.append(self.ui_scale_button)

        self.sensitivity_slider = self._create_options_slider(
            text='MOUSE SENS',
            y=0.03,
            min_value=10,
            max_value=100,
            default=RuntimeSettings.mouse_sensitivity,
            step=1,
            on_changed=self.on_sensitivity_changed
        )

        self.fov_slider = self._create_options_slider(
            text='FOV',
            y=-0.08,
            min_value=70,
            max_value=120,
            default=RuntimeSettings.fov,
            step=1,
            on_changed=self.on_fov_changed
        )

        self.volume_slider = self._create_options_slider(
            text='AUDIO',
            y=-0.19,
            min_value=0.0,
            max_value=1.0,
            default=RuntimeSettings.audio_volume,
            step=0.01,
            on_changed=self.on_volume_changed
        )

        self.fullscreen_label = Text(
            parent=self,
            text='FULLSCREEN',
            position=(-0.28, -0.31),
            origin=(0, 0),
            scale=MENU_BODY_TEXT_SCALE,
            font=UI_FONT_PRIMARY,
            color=color.light_gray,
            enabled=False
        )
        self.options_widgets.append(self.fullscreen_label)

        self.fullscreen_button = MenuButton(
            parent=self,
            text=self._fullscreen_button_text(),
            position=(0.2, -0.31),
            on_click=self.on_toggle_fullscreen,
            enabled=False
        )
        self.options_widgets.append(self.fullscreen_button)

        self.options_back_button = MenuButton(
            parent=self,
            text='BACK',
            position=(0, -0.43),
            on_click=self.on_options_back,
            enabled=False
        )
        self.options_widgets.append(self.options_back_button)

    def _create_options_slider(self, text, y, min_value, max_value, default, step, on_changed):
        slider = Slider(
            parent=self,
            text=text,
            min=min_value,
            max=max_value,
            default=default,
            step=step,
            dynamic=True,
            on_value_changed=on_changed,
            scale=1.05,
            y=y,
            x=-0.05,
            enabled=False
        )
        slider.label.font = UI_FONT_PRIMARY
        slider.label.scale = MENU_BODY_TEXT_SCALE
        slider.label.color = color.light_gray
        slider.knob.text_entity.font = UI_FONT_MONO
        slider.knob.text_entity.scale = 1.2
        self.options_widgets.append(slider)
        return slider

    def _set_options_visible(self, enabled):
        for widget in self.options_widgets:
            widget.enabled = enabled

    def apply_menu_ui_scale(self):
        self.scale = RuntimeSettings.ui_scale()

    def _ui_scale_button_text(self):
        return RuntimeSettings.ui_scale_name.upper()

    def _fullscreen_button_text(self):
        return 'ON' if RuntimeSettings.fullscreen else 'OFF'

    def show_main(self):
        """Show main menu."""
        self.mode = 'main'
        self.enabled = True
        self.background.enabled = True
        self.apply_menu_ui_scale()

        # Main menu elements
        self.title.enabled = True
        self.subtitle.enabled = True
        self.controls.enabled = True
        for btn in self.main_buttons:
            btn.enabled = True

        # Hide other elements
        self.pause_title.enabled = False
        self.resume_button.enabled = False
        self.restart_button.enabled = False
        self.pause_options_button.enabled = False
        self.quit_to_menu_button.enabled = False
        self.game_over_title.enabled = False
        self.final_score.enabled = False
        self.play_again_button.enabled = False
        self._set_options_visible(False)

        mouse.locked = False
        mouse.visible = True

    def show_pause(self):
        """Show pause menu."""
        self.mode = 'pause'
        self.enabled = True
        self.background.enabled = True
        self.apply_menu_ui_scale()

        # Hide main menu elements
        self.title.enabled = False
        self.subtitle.enabled = False
        self.controls.enabled = False
        for btn in self.main_buttons:
            btn.enabled = False

        # Show pause elements
        self.pause_title.enabled = True
        self.resume_button.enabled = True
        self.restart_button.enabled = True
        self.pause_options_button.enabled = True
        self.quit_to_menu_button.enabled = True

        # Hide game over and options elements
        self.game_over_title.enabled = False
        self.final_score.enabled = False
        self.play_again_button.enabled = False
        self._set_options_visible(False)

    def show_options(self, return_mode):
        """Show options menu and remember where to return."""
        self.mode = 'options'
        self.options_return_mode = return_mode
        self.enabled = True
        self.background.enabled = True

        # Hide all standard menu states
        self.title.enabled = False
        self.subtitle.enabled = False
        self.controls.enabled = False
        self.pause_title.enabled = False
        self.resume_button.enabled = False
        self.restart_button.enabled = False
        self.pause_options_button.enabled = False
        self.quit_to_menu_button.enabled = False
        self.game_over_title.enabled = False
        self.final_score.enabled = False
        self.play_again_button.enabled = False
        for btn in self.main_buttons:
            btn.enabled = False

        # Show options
        self.sensitivity_slider.value = RuntimeSettings.mouse_sensitivity
        self.fov_slider.value = RuntimeSettings.fov
        self.volume_slider.value = RuntimeSettings.audio_volume
        self.ui_scale_button.text = self._ui_scale_button_text()
        self.fullscreen_button.text = self._fullscreen_button_text()
        self._set_options_visible(True)

        mouse.locked = False
        mouse.visible = True

    def show_game_over(self, score=0):
        """Show game over screen."""
        self.mode = 'game_over'
        self.enabled = True
        self.background.enabled = True
        self.apply_menu_ui_scale()

        # Hide other elements
        self.title.enabled = False
        self.subtitle.enabled = False
        self.controls.enabled = False
        for btn in self.main_buttons:
            btn.enabled = False
        self.pause_title.enabled = False
        self.resume_button.enabled = False
        self.restart_button.enabled = False
        self.pause_options_button.enabled = False
        self.quit_to_menu_button.enabled = False
        self._set_options_visible(False)

        # Show game over elements
        self.game_over_title.enabled = True
        self.final_score.enabled = True
        self.final_score.text = f'Final Score: {score}'
        self.play_again_button.enabled = True
        self.quit_to_menu_button.enabled = True
        self.quit_to_menu_button.y = -0.24

    def hide(self):
        """Hide the menu."""
        self.enabled = False
        self.background.enabled = False
        self.title.enabled = False
        self.subtitle.enabled = False
        self.controls.enabled = False
        self.pause_title.enabled = False
        self.resume_button.enabled = False
        self.restart_button.enabled = False
        self.pause_options_button.enabled = False
        self.quit_to_menu_button.enabled = False
        self.game_over_title.enabled = False
        self.final_score.enabled = False
        self.play_again_button.enabled = False
        for btn in self.main_buttons:
            btn.enabled = False
        self._set_options_visible(False)

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

    def on_options(self):
        """Open options from current mode."""
        return_mode = 'pause' if self.mode == 'pause' else 'main'
        self.show_options(return_mode=return_mode)

    def on_options_back(self):
        """Return from options to the previous menu state."""
        if self.options_return_mode == 'pause':
            self.show_pause()
        else:
            self.show_main()

    def on_cycle_ui_scale(self):
        names = list(UI_SCALE_PRESETS.keys())
        current_index = names.index(RuntimeSettings.ui_scale_name)
        RuntimeSettings.ui_scale_name = names[(current_index + 1) % len(names)]
        self.ui_scale_button.text = self._ui_scale_button_text()
        self.apply_menu_ui_scale()
        self.game.apply_runtime_settings(rebuild_hud=True)

    def on_sensitivity_changed(self):
        RuntimeSettings.mouse_sensitivity = round(self.sensitivity_slider.value, 1)
        self.game.apply_runtime_settings()

    def on_fov_changed(self):
        RuntimeSettings.fov = int(round(self.fov_slider.value))
        self.game.apply_runtime_settings()

    def on_volume_changed(self):
        RuntimeSettings.audio_volume = round(self.volume_slider.value, 2)
        self.game.apply_runtime_settings()

    def on_toggle_fullscreen(self):
        RuntimeSettings.fullscreen = not RuntimeSettings.fullscreen
        self.fullscreen_button.text = self._fullscreen_button_text()
        self.game.apply_runtime_settings()

    def on_quit(self):
        """Quit the game."""
        application.quit()


class MenuButton(Button):
    """Styled button for menus."""

    def __init__(self, text='Button', on_click=None, **kwargs):
        super().__init__(
            text=text,
            scale=MENU_BUTTON_SCALE,
            color=color.dark_gray,
            highlight_color=color.gray,
            pressed_color=color.light_gray,
            **kwargs
        )

        self.text_entity.font = UI_FONT_PRIMARY
        self.text_entity.scale = MENU_BUTTON_TEXT_SCALE
        self.text_entity.origin = (0, 0)
        self.original_text_scale = MENU_BUTTON_TEXT_SCALE
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
