# Doom-like FPS - Critique and Improvement TODO

## Critique (current state)

### 1) Core gameplay loop is too shallow
- The game is fun for a short demo, but there is no long-term loop.
- Enemies spawn once at fixed points and there is no wave escalation, objective, or win condition.
- Score increases, but score is not connected to progression, unlocks, or risk/reward decisions.

### 2) Enemy/content variety is limited
- In practice, only zombies are used, even though config hints at more enemy types.
- Enemy behavior is mostly direct chase + melee; combat quickly becomes predictable.
- Arena layout is static and does not force changing tactics.

### 3) Combat feel needs more depth
- Shooting works, but lacks layered feedback (strong hit confirms, kill effects, combo moments).
- Weapon system supports extension, but there is effectively one primary flow.
- Ammo/reload pressure is basic and does not drive interesting decisions.

### 4) UI/UX consistency and responsiveness
- Typography and scale were inconsistent before recent fixes; this needs ongoing central control.
- HUD elements are functional but minimal, with little contextual information (wave, threats, objective).
- Menus do not include options users expect (sensitivity, FOV, audio volume, resolution/fullscreen).

### 5) Technical architecture can become hard to scale
- Several modules reach into global state (`game_state` / `import main`) which increases coupling.
- Some systems are present but underused or partially implemented.
- No automated tests or content validation, which increases regression risk as features grow.

---

## Prioritized TODO

## P0 - Immediate polish and stability
- [x] Centralize all UI scale/font constants in `config.py` and use them everywhere in UI modules.
- [x] Add a runtime UI scale multiplier (small/normal/large) in options menu.
- [x] Add options menu: mouse sensitivity, audio volume, fullscreen toggle, FOV slider.
- [x] Replace remaining placeholder/pass UI hooks with real behavior (damage feedback, hit confirmation consistency).
- [x] Standardize text alignment/anchors for all HUD values to avoid drift across resolutions.
- [x] Add a basic pause-state input lock test checklist (no shooting/moving while paused).

## P1 - Make the gameplay loop actually sticky
- [x] Implement wave-based spawning with increasing difficulty over time.
- [x] Add a clear run objective (survive X waves or reach score threshold) and victory screen.
- [x] Add spawn director logic (spawn timing + location bias away from player line-of-sight).
- [x] Add health/ammo pickups with spawn rules and cooldowns.
- [x] Tie score to gameplay utility (temporary buffs, weapon unlocks, or buy station).

## P2 - Combat and enemy depth
- [ ] Implement at least two additional enemy archetypes using existing config (`demon`, `imp`) with distinct behaviors.
- [ ] Add ranged projectile logic for `imp` with telegraphed windup.
- [ ] Add hit reaction states/stagger chance for enemies on high-damage hits.
- [ ] Add at least one additional weapon with different role (close burst vs precision vs crowd control).
- [ ] Introduce optional alt-fire or cooldown abilities to break repetitive shooting rhythm.

## P3 - Level and encounter design
- [ ] Add multiple arenas or procedural arena variants (layout seeds).
- [ ] Improve cover placement and pathing lanes to encourage movement decisions.
- [ ] Add hazard or interactive elements (explosive barrels, temporary doors, traps).
- [ ] Add spawn blockers to prevent enemies spawning in immediate view unless intentional.

## P4 - Audio/visual feedback
- [ ] Add layered audio mix (ambient loop, combat intensity, low-health cue).
- [ ] Add stronger VFX for hit/kill/headshot (flash, particles, subtle camera impulse).
- [ ] Add screen-space feedback for major events (wave start, elite spawn, objective complete).
- [ ] Preload frequently used sounds to avoid runtime hitching from on-demand loads.

## P5 - Code quality and maintainability
- [ ] Reduce global coupling by introducing a lightweight event bus or service container.
- [ ] Move game constants into typed config structures for safer evolution.
- [ ] Add smoke tests for critical flows: game start, restart, pause/resume, game over.
- [ ] Add a minimal balancing doc (enemy HP/damage/speed and weapon DPS assumptions).
- [ ] Add logging hooks for combat events and spawn telemetry to support tuning.

---

## Suggested milestone plan

### Milestone A (1-2 days): "Playable polish"
- Deliver P0 + basic P1 wave system.
- Goal: game feels coherent and replayable for at least 10-15 minutes.

### Milestone B (2-4 days): "Depth pass"
- Deliver P2 + targeted P3 layout upgrades.
- Goal: combat variety and encounters feel meaningfully different run-to-run.

### Milestone C (2-3 days): "Production hardening"
- Deliver P4 + P5.
- Goal: less hitching, better feedback, safer future iteration.

---

## Definition of done for "much better"
- [ ] New players can understand controls/objective in under 30 seconds.
- [ ] A full run has clear pacing (early, mid, late pressure).
- [ ] At least 3 enemy behaviors and 2+ weapon playstyles are available.
- [ ] UI is readable at 1080p and 1440p without manual edits.
- [ ] Restart/pause/game-over flows are stable with no duplicate UI artifacts.
