import pygame
import random
import os
import sys

def resource_path(relative_path):
    """ Get the correct path whether running as script or exe """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

pygame.init()

# --- Audio ---
pygame.mixer.init()
pygame.mixer.music.load(resource_path("assets/music.wav"))
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

shoot_sound     = pygame.mixer.Sound(resource_path("assets/shoot.wav"))
explosion_sound = pygame.mixer.Sound(resource_path("assets/explosion.wav"))
shoot_sound.set_volume(0.3)
explosion_sound.set_volume(0.5)

SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Shooter")

# --- Colors ---
BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
YELLOW = (255, 210, 0)
RED    = (255, 100, 0)
GREEN  = (50,  200, 50)

# --- Font ---
font       = pygame.font.SysFont(None, 60)
font_small = pygame.font.SysFont(None, 35)

# --- Load sprites ---
player_img = pygame.image.load(resource_path("assets/player.png")).convert_alpha()
enemy_img  = pygame.image.load(resource_path("assets/enemy.png")).convert_alpha()
bg_img     = pygame.image.load(resource_path("assets/background.png")).convert()

# --- Scale ---
bg_img      = pygame.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT * 2))
player_img  = pygame.transform.scale(player_img, (50, 50))
player_life = pygame.transform.scale(player_img, (30, 30))
enemy_img   = pygame.transform.scale(enemy_img,  (80, 40))

# --- Background scroll ---
bg_y         = 0
scroll_speed = 4

# --- Explosions ---
explosions = []

def reset_game():
    player      = pygame.Rect(375, 500, 50, 50)
    bullets     = []
    enemies     = []
    score       = 0
    lives       = 3
    wave        = 1
    spawn_timer = 0
    game_over   = False
    won         = False
    return player, bullets, enemies, score, lives, wave, spawn_timer, game_over, won

player, bullets, enemies, score, lives, wave, spawn_timer, game_over, won = reset_game()

# --- Physics ---
player_speed = 5
bullet_speed = 8
bullet_ready = True

# --- Clock ---
clock = pygame.time.Clock()
FPS   = 60

running = True
while running:

    spawn_delay = max(20, 60 - (wave * 8))
    enemy_speed = 1 + (wave * 0.5)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and (game_over or won):
                player, bullets, enemies, score, lives, wave, spawn_timer, game_over, won = reset_game()
                explosions.clear()

    if not game_over and not won:

        # --- Input ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]  and player.left  > 0:
            player.x -= player_speed
        if keys[pygame.K_RIGHT] and player.right < SCREEN_WIDTH:
            player.x += player_speed
        if keys[pygame.K_UP]    and player.top   > 0:
            player.y -= player_speed
        if keys[pygame.K_DOWN]  and player.bottom < SCREEN_HEIGHT:
            player.y += player_speed

        # --- Shoot ---
        if keys[pygame.K_SPACE] and bullet_ready:
            bullet = pygame.Rect(player.centerx - 5, player.top, 10, 20)
            bullets.append(bullet)
            bullet_ready = False
            shoot_sound.play()
        if not keys[pygame.K_SPACE]:
            bullet_ready = True

        # --- Move bullets ---
        for bullet in bullets[:]:
            bullet.y -= bullet_speed
            if bullet.bottom < 0:
                bullets.remove(bullet)

        # --- Spawn enemies ---
        spawn_timer += 1
        if spawn_timer >= spawn_delay:
            spawn_timer = 0
            enemy_x = random.randint(0, SCREEN_WIDTH - 80)
            enemy   = pygame.Rect(enemy_x, -40, 80, 40)
            enemies.append(enemy)

        # --- Move enemies ---
        for enemy in enemies[:]:
            enemy.y += enemy_speed
            if enemy.top > SCREEN_HEIGHT:
                enemies.remove(enemy)
                lives -= 1
                if lives <= 0:
                    game_over = True

        # --- Bullet vs enemy ---
        for enemy in enemies[:]:
            for bullet in bullets[:]:
                if enemy.colliderect(bullet):
                    explosions.append([enemy.centerx, enemy.centery, 5, 40])
                    explosion_sound.play()
                    enemies.remove(enemy)
                    bullets.remove(bullet)
                    score += 10
                    break

        # --- Enemy vs player ---
        for enemy in enemies[:]:
            if player.colliderect(enemy.inflate(-10, -10)):
                explosions.append([enemy.centerx, enemy.centery, 5, 40])
                explosion_sound.play()
                enemies.remove(enemy)
                lives -= 1
                if lives <= 0:
                    game_over = True

        # --- Update explosions ---
        for exp in explosions[:]:
            exp[2] += 3
            if exp[2] >= exp[3]:
                explosions.remove(exp)

        # --- Wave progression ---
        if score >= wave * 100:
            wave += 1
            if wave > 5:
                won = True

    # --- Draw ---
    bg_y += scroll_speed
    if bg_y >= SCREEN_HEIGHT:
        bg_y = 0
    screen.blit(bg_img, (0, bg_y - SCREEN_HEIGHT))
    screen.blit(bg_img, (0, bg_y))

    # --- Draw explosions ---
    for exp in explosions:
        progress = exp[2] / exp[3]
        color    = (255, int(120 + 80 * (1 - progress)), 0)
        pygame.draw.circle(screen, color, (exp[0], exp[1]), exp[2])
        pygame.draw.circle(screen, WHITE, (exp[0], exp[1]), exp[2] // 3)

    for bullet in bullets:
        pygame.draw.circle(screen, WHITE, bullet.center, 4)
    for enemy in enemies:
        screen.blit(enemy_img, enemy)
    screen.blit(player_img, player)

    # --- HUD ---
    hud = font_small.render(f"Score: {score}   Wave: {wave}/5   Lives: {lives}", True, WHITE)
    screen.blit(hud, (10, 10))

    for i in range(lives):
        screen.blit(player_life, (SCREEN_WIDTH - 40 - (i * 35), 5))

    # --- Game over screen ---
    if game_over:
        msg  = font.render("GAME OVER :(", True, RED)
        msg2 = font_small.render(f"Final score: {score}   Press R to restart", True, WHITE)
        screen.blit(msg,  (220, 220))
        screen.blit(msg2, (160, 300))

    # --- Win screen ---
    if won:
        msg  = font.render("YOU WIN! :)", True, YELLOW)
        msg2 = font_small.render(f"Final score: {score}   Press R to restart", True, WHITE)
        screen.blit(msg,  (230, 220))
        screen.blit(msg2, (160, 300))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()