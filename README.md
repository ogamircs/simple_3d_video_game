# Doom-like FPS Game

A retro-style first-person shooter inspired by classic Doom, built with Python and the Ursina engine.

## Current Gameplay

- Wave-based survival loop with escalating pressure and a victory objective.
- Multiple enemy archetypes:
  - Zombie: baseline melee chaser.
  - Demon: faster melee bruiser with burst pressure.
  - Imp: ranged attacker with telegraphed projectile shots.
- Weapon variety:
  - Shotgun-style primary weapon.
  - Rifle for fast precise fire.
  - Alt-fire support (right mouse button) with cooldown-based burst/power shots.
- Arena variants with encounter elements:
  - Different cover layouts.
  - Spawn blockers to reduce unfair near-player spawns.
  - Interactive hazards (explosive barrels, floor traps, timed doors).
- Pickup economy (health/ammo) and score milestone rewards (heal + ammo).

## UI and Feedback

- Doom-style bottom HUD (ammo, health, score, kills).
- Top-level objective HUD for wave and enemy-remaining info.
- Event messages for wave starts, clears, elite spawns, and objective completion.
- Damage flash, hit marker, and headshot feedback.
- In-game options menu:
  - UI scale (small/normal/large)
  - Mouse sensitivity
  - FOV
  - Audio volume
  - Fullscreen toggle

## Technical Highlights

- Central combat system with damage falloff and headshot detection.
- Lightweight event bus and service container for reduced coupling.
- Layered audio manager (ambient/combat/low-health mix) with preload support.
- Telemetry hooks writing gameplay events to `gameplay.log`.
- Smoke tests for critical flows in `tests/smoke/test_game_smoke.py`.

## Requirements

- Python 3.11+
- Windows/Linux/macOS capable of running Ursina + Panda3D

## Setup

### Preferred: UV

```bash
uv sync
```

### Alternative: pip

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Run

```bash
uv run python main.py
```

or (pip/venv workflow):

```bash
python main.py
```

## Controls

- `WASD`: move
- `Mouse`: look
- `Left Click`: fire
- `Right Click`: alt fire
- `R`: reload
- `1` / `2` or mouse wheel: switch weapon
- `ESC`: pause / resume menu flow

## Test

```bash
uv run python -m unittest tests.smoke.test_game_smoke
```

## Key Files

- `main.py`: game loop, waves, spawning, objective flow, hazards integration
- `config.py`: tunable constants and typed config structures
- `entities/`: player, enemies, pickups, hazards
- `weapons/`: base weapon, shotgun-style primary, rifle
- `ui/`: menu/options and HUD
- `systems/`: combat, audio manager, telemetry
- `core/`: event bus and shared service container

## License

MIT
