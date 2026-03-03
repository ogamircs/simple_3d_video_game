# Pause Input Lock Checklist

Use this checklist for each build before merging UI/input changes.

## Preconditions
- [ ] Launch game (`uv run python main.py`).
- [ ] Start a run and confirm enemies are active.

## Pause behavior
- [ ] Press `ESC` during gameplay and confirm pause menu appears.
- [ ] Confirm mouse cursor is visible in pause/options screens.
- [ ] Confirm mouse is locked again after resume.

## Input lock while paused
- [ ] Hold `W` while paused: player does not move.
- [ ] Left click while paused: weapon does not fire.
- [ ] Press `R` while paused: weapon does not reload.
- [ ] Scroll / number keys while paused: weapon does not switch.
- [ ] Enemies do not chase/attack while paused.

## Options menu pause behavior
- [ ] Open `OPTIONS` from pause menu.
- [ ] Press `ESC` in options: returns to pause menu (does not resume immediately).
- [ ] Press `BACK` in options: returns to pause menu.
- [ ] Press `RESUME` from pause: returns to gameplay.

## Regression checks
- [ ] Restart from pause menu works and creates one HUD (no duplicate overlays).
- [ ] Restart from game over works and creates one HUD.
- [ ] Hit marker and damage feedback still function after pause/resume cycles.
