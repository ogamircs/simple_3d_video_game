"""
Layered runtime audio controller.
"""
from ursina import Audio, application
from config import (
    AMBIENT_TRACK, COMBAT_TRACK, LOW_HEALTH_TRACK,
    COMBAT_AUDIO_MIN, COMBAT_AUDIO_MAX, LOW_HEALTH_AUDIO_LEVEL
)


class AudioManager:
    """Controls ambient/combat/low-health layers and preloads one-shot sounds."""

    def __init__(self):
        self.ambient = None
        self.combat = None
        self.low_health = None
        self._preloaded = {}
        self._preloaded_once = False

    def preload_sounds(self):
        """Preload one-shot effects to reduce first-hit hitching."""
        if self._preloaded_once:
            return
        if getattr(application, 'base', None) is None:
            return
        for sound_name in ('assets/sounds/shotgun.wav', 'assets/sounds/hit.wav', 'assets/sounds/enemy_death.wav'):
            try:
                self._preloaded[sound_name] = Audio(sound_name, autoplay=False, auto_destroy=False)
            except Exception:
                # Unit tests and headless contexts may not have Panda loader yet.
                return
        self._preloaded_once = True

    def start_layers(self):
        """Start persistent audio layers at low base level."""
        if getattr(application, 'base', None) is None:
            return
        self.preload_sounds()
        if not self.ambient:
            try:
                self.ambient = Audio(AMBIENT_TRACK, loop=True, autoplay=True, auto_destroy=False, volume=0.16)
                self.ambient.pitch = 0.5
            except Exception:
                return
        if not self.combat:
            try:
                self.combat = Audio(COMBAT_TRACK, loop=True, autoplay=True, auto_destroy=False, volume=COMBAT_AUDIO_MIN)
                self.combat.pitch = 0.35
            except Exception:
                return
        if not self.low_health:
            try:
                self.low_health = Audio(LOW_HEALTH_TRACK, loop=True, autoplay=True, auto_destroy=False, volume=0.0)
                self.low_health.pitch = 0.18
            except Exception:
                return

    def update_layers(self, enemies_alive, player_health_pct):
        """Blend layer volumes from gameplay intensity."""
        if not self.ambient:
            return
        enemy_factor = max(0.0, min(1.0, enemies_alive / 12))
        self.combat.volume = COMBAT_AUDIO_MIN + ((COMBAT_AUDIO_MAX - COMBAT_AUDIO_MIN) * enemy_factor)

        low_health_factor = max(0.0, min(1.0, (0.35 - player_health_pct) / 0.35))
        self.low_health.volume = LOW_HEALTH_AUDIO_LEVEL * low_health_factor

    def stop(self):
        for layer in (self.ambient, self.combat, self.low_health):
            if layer:
                layer.stop(destroy=True)
        self.ambient = None
        self.combat = None
        self.low_health = None
