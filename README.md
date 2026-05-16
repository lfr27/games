# Games

A collection of two games built with Python and Pygame.

---

## Games

### 1. Platformer (`my_pygame/`)

A 2D side-scrolling platformer. Navigate across platforms, collect coins, and reach the goal while avoiding a patrolling enemy — across 3 levels of increasing difficulty.

**Controls**

| Key | Action |
|-----|--------|
| Arrow Left / Right | Move |
| Space | Jump |
| R | Restart |

**Features**
- 3 levels with increasing enemy speed and platform complexity
- Gravity physics and platform collision
- Score based on coins collected, goals reached, and time survived

---

### 2. Space Shooter (`my_shooter/`)

A vertical space shooter. Pilot a ship at the bottom of the screen, shoot enemies coming from above, and survive 5 waves of increasing difficulty.

**Controls**

| Key | Action |
|-----|--------|
| Arrow Keys | Move ship |
| Space | Shoot |
| R | Restart |

**Features**
- 5 waves with faster and more frequent enemies each wave
- 3 lives system
- Animated explosions, scrolling background, background music and sound effects
- Windows executable available in `my_shooter/dist/main.exe`

---

## Requirements

- Python 3
- Pygame

```bash
pip install pygame
```

## Running the Games

```bash
# Platformer
cd my_pygame
python main.py

# Space Shooter
cd my_shooter
python main.py
```
