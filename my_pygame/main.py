import pygame

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 500
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("My Platformer")

# --- Colors ---
WHITE  = (255, 255, 255)
BLUE   = (50, 120, 200)
GREEN  = (50, 180, 50)
YELLOW = (255, 210, 0)
RED    = (200, 50, 50)
BLACK  = (0, 0, 0)
ORANGE = (255, 165, 0)
PURPLE = (150, 50, 200)

# --- Font ---
font       = pygame.font.SysFont(None, 60)
font_small = pygame.font.SysFont(None, 35)

# --- Load sprites ---
player_img = pygame.image.load("assets/player.png").convert_alpha()
enemy_img  = pygame.image.load("assets/enemy.png").convert_alpha()
coin_img   = pygame.image.load("assets/coin.png").convert_alpha()

# --- Scale to match rect sizes ---
player_img = pygame.transform.scale(player_img, (50, 50))
enemy_img  = pygame.transform.scale(enemy_img,  (50, 50))
coin_img   = pygame.transform.scale(coin_img,   (20, 20))

# --- Level definitions ---
levels = [
    {   # Level 1 - easy
        "platforms": [
            pygame.Rect(0,   450, 800, 20),
            pygame.Rect(150, 350, 150, 20),
            pygame.Rect(400, 270, 150, 20),
            pygame.Rect(620, 180, 150, 20),
        ],
        "coins": [
            pygame.Rect(170, 320, 20, 20),
            pygame.Rect(250, 320, 20, 20),
            pygame.Rect(420, 240, 20, 20),
            pygame.Rect(500, 240, 20, 20),
            pygame.Rect(640, 150, 20, 20),
            pygame.Rect(300, 420, 20, 20),
        ],
        "enemy_start": 300,
        "enemy_range": (200, 500),
        "enemy_speed": 2,
        "goal": pygame.Rect(670, 140, 40, 40),
    },
    {   # Level 2 - medium
        "platforms": [
            pygame.Rect(0,   450, 800, 20),
            pygame.Rect(100, 370, 120, 20),
            pygame.Rect(300, 300, 100, 20),
            pygame.Rect(500, 220, 120, 20),
            pygame.Rect(250, 150, 100, 20),
            pygame.Rect(620, 140, 120, 20),
        ],
        "coins": [
            pygame.Rect(110, 340, 20, 20),
            pygame.Rect(180, 340, 20, 20),
            pygame.Rect(310, 270, 20, 20),
            pygame.Rect(510, 190, 20, 20),
            pygame.Rect(570, 190, 20, 20),
            pygame.Rect(260, 120, 20, 20),
            pygame.Rect(630, 110, 20, 20),
        ],
        "enemy_start": 400,
        "enemy_range": (100, 600),
        "enemy_speed": 3,
        "goal": pygame.Rect(650, 100, 40, 40),
    },
    {   # Level 3 - hard
        "platforms": [
            pygame.Rect(0,   450, 800, 20),
            pygame.Rect(50,  380, 80,  20),
            pygame.Rect(200, 310, 80,  20),
            pygame.Rect(350, 240, 80,  20),
            pygame.Rect(500, 170, 80,  20),
            pygame.Rect(350, 100, 80,  20),
            pygame.Rect(180, 100, 80,  20),
        ],
        "coins": [
            pygame.Rect(60,  350, 20, 20),
            pygame.Rect(210, 280, 20, 20),
            pygame.Rect(360, 210, 20, 20),
            pygame.Rect(510, 140, 20, 20),
            pygame.Rect(360,  70, 20, 20),
            pygame.Rect(190,  70, 20, 20),
        ],
        "enemy_start": 300,
        "enemy_range": (50, 700),
        "enemy_speed": 4,
        "goal": pygame.Rect(185, 60, 40, 40),
    },
]

def load_level(level_index):
    data           = levels[level_index]
    platforms      = data["platforms"]
    coins          = [pygame.Rect(c.x, c.y, c.w, c.h) for c in data["coins"]]
    goal           = data["goal"]
    enemy          = pygame.Rect(data["enemy_start"], 410, 50, 30)
    enemy_speed    = data["enemy_speed"]
    enemy_range    = data["enemy_range"]
    player         = pygame.Rect(30, 380, 50, 50)
    velocity_y     = 0
    on_ground      = False
    return platforms, coins, goal, enemy, enemy_speed, enemy_range, player, velocity_y, on_ground

def reset_game():
    score       = 0
    level_index = 0
    dead        = False
    won         = False
    platforms, coins, goal, enemy, enemy_speed, enemy_range, player, velocity_y, on_ground = load_level(0)
    return score, level_index, dead, won, platforms, coins, goal, enemy, enemy_speed, enemy_range, player, velocity_y, on_ground

score, level_index, dead, won, platforms, coins, goal, enemy, enemy_speed, enemy_range, player, velocity_y, on_ground = reset_game()

# --- Physics ---
player_speed = 5
gravity      = 0.5
jump_force   = -12
score_timer  = 0

clock = pygame.time.Clock()
FPS = 60

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and dead:
                score, level_index, dead, won, platforms, coins, goal, enemy, enemy_speed, enemy_range, player, velocity_y, on_ground = reset_game()
            if event.key == pygame.K_r and won:
                score, level_index, dead, won, platforms, coins, goal, enemy, enemy_speed, enemy_range, player, velocity_y, on_ground = reset_game()

    if not won and not dead:

        # --- Input ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.x -= player_speed
        if keys[pygame.K_RIGHT]:
            player.x += player_speed
        if keys[pygame.K_SPACE] and on_ground:
            velocity_y = jump_force
            on_ground = False

   # --- Keep player inside screen ---
        if player.left < 0:
            player.left = 0
        if player.right > SCREEN_WIDTH:
            player.right = SCREEN_WIDTH

        # --- Gravity ---
        velocity_y += gravity
        player.y += velocity_y



       # --- Platform collision ---
        on_ground = False
        for platform in platforms:
            if player.colliderect(platform):
                # how many pixels are overlapping horizontally
                overlap_x = min(player.right, platform.right) - max(player.left, platform.left)
                if overlap_x > 8:          # only counts if overlapping more than 5px
                    if velocity_y > 0:
                        player.bottom = platform.top
                        velocity_y = 0
                        on_ground = True
                    elif velocity_y < 0:
                        player.top = platform.bottom
                        velocity_y = 0

        # --- Coin collision ---
        for coin in coins[:]:
            if player.colliderect(coin):
                coins.remove(coin)
                score += 10

        # --- Enemy movement ---
        enemy.x += enemy_speed
        if enemy.x > enemy_range[1] or enemy.x < enemy_range[0]:
            enemy_speed *= -1

# --- Enemy collision ---
        if player.colliderect(enemy.inflate(-25, -25)):
            dead = True

        # --- Score over time ---
        score_timer += 1
        if score_timer >= 60:
            score += 1
            score_timer = 0

        # --- Goal collision ---
        if player.colliderect(goal):
            score += 100
            level_index += 1
            if level_index >= len(levels):
                won = True
               
            else:
                # --- Load next level ---
                platforms, coins, goal, enemy, enemy_speed, enemy_range, player, velocity_y, on_ground = load_level(level_index)

# --- Fall out of screen = dead ---
        if player.top > SCREEN_HEIGHT:
            dead = True

       
    # --- Draw ---
    screen.fill(WHITE)

    for platform in platforms:
        pygame.draw.rect(screen, GREEN, platform)

    for coin in coins:
        screen.blit(coin_img, coin)

    pygame.draw.rect(screen, YELLOW, goal)
    screen.blit(enemy_img, enemy)
    # shrink the hitbox to the center of the image
    enemy_hitbox = enemy.inflate(-20, -20)  # 20px smaller on all sides
    if player.colliderect(enemy_hitbox):
        dead = True

    screen.blit(player_img, player)

    # --- HUD ---
    hud = font_small.render(f"Score: {score}   Level: {level_index + 1}/{len(levels)}   Coins: {len(coins)} left", True, BLACK)
    screen.blit(hud, (10, 10))

    # --- Win screen ---
    if won:
        msg  = font.render("YOU WIN! :)", True, BLACK)
        msg2 = font_small.render(f"Final score: {score}   press R to restart", True, BLACK)
        screen.blit(msg,  (230, 180))
        screen.blit(msg2, (170, 260))

    # --- Dead screen ---
    if dead:
        msg  = font.render("YOU DIED! :(", True, RED)
        msg2 = font_small.render("Press R to restart", True, BLACK)
        screen.blit(msg,  (210, 180))
        screen.blit(msg2, (290, 260))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()