import pygame
import random
import math

pygame.init()

infoObject = pygame.display.Info()
WIDTH, HEIGHT = infoObject.current_w, infoObject.current_h
PLAYER_SIZE = 50
ENEMY_SIZE = 30
ENEMY_SPEED = 3
INITIAL_LIVES = 3
player_speed = 4
bullet_speed = 5
killed_enemies = 0

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PINK = (241, 156, 187)

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Game")

training = [pygame.image.load('img/training1.jpg'),
            pygame.image.load('img/training2.jpg'),
            pygame.image.load('img/training3.jpg'),
            pygame.image.load('img/training2.jpg'),
            pygame.image.load('img/training1.jpg')]


class Bullet:
    def __init__(self, x, y, direction):
        self.pos = [x, y]
        self.direction = direction  # направление: (dx, dy)

    def move(self):
        self.pos[0] += self.direction[0] * bullet_speed
        self.pos[1] += self.direction[1] * bullet_speed

    def draw(self, surface):
        pygame.draw.circle(surface, BLACK, (int(self.pos[0]), int(self.pos[1])), 10)


class Enemy:
    def __init__(self, x, y):
        self.size = ENEMY_SIZE
        self.pos = [x, y]

    def move_towards_player(self, player_pos):
        direction_x = player_pos[0] - self.pos[0]
        direction_y = player_pos[1] - self.pos[1]
        distance = math.hypot(direction_x, direction_y)
        if distance > 0:
            direction_x /= distance
            direction_y /= distance
            self.pos[0] += direction_x * ENEMY_SPEED
            self.pos[1] += direction_y * ENEMY_SPEED

    def draw(self, surface):
        pygame.draw.rect(surface, RED, (self.pos[0], self.pos[1], self.size, self.size))


def spawn_enemy():
    side = random.choice(['top', 'bottom', 'left', 'right'])
    if side == 'top':
        x = random.randint(0, WIDTH - ENEMY_SIZE)
        y = 0
    elif side == 'bottom':
        x = random.randint(0, WIDTH - ENEMY_SIZE)
        y = HEIGHT - ENEMY_SIZE
    elif side == 'left':
        x = 0
        y = random.randint(0, HEIGHT - ENEMY_SIZE)
    else:
        x = WIDTH - ENEMY_SIZE
        y = random.randint(0, HEIGHT - ENEMY_SIZE)

    return Enemy(x, y)


def draw_text(text, size, color, surface, x, y, font_path='text/EpilepsySans.ttf'):
    font = pygame.font.Font(font_path, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)


def draw_text1(text, size, color, surface, x, y, font_path='text/EpilepsySans.ttf'):
    font = pygame.font.Font(font_path, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)
    return text_rect


def game_loop():
    player_pos = [WIDTH // 2, HEIGHT // 2]
    lives = INITIAL_LIVES
    enemies = []
    bullets = []
    enemy_spawn_time = 2
    clock = pygame.time.Clock()
    running = True
    timer = 40
    last_time = pygame.time.get_ticks()
    last_shot_time = 0
    global killed_enemies

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:  # Влево
            player_pos[0] -= player_speed
        if keys[pygame.K_d]:  # Вправо
            player_pos[0] += player_speed
        if keys[pygame.K_w]:  # Вверх
            player_pos[1] -= player_speed
        if keys[pygame.K_s]:  # Вниз
            player_pos[1] += player_speed

        current_time = pygame.time.get_ticks()
        if keys[pygame.K_UP] and current_time - last_shot_time > 200:  # Стрельба вверх
            bullet = Bullet(player_pos[0] + PLAYER_SIZE // 2, player_pos[1], (0, -1))
            bullets.append(bullet)
            last_shot_time = current_time
        if keys[pygame.K_DOWN] and current_time - last_shot_time > 200:  # Стрельба вниз
            bullet = Bullet(player_pos[0] + PLAYER_SIZE // 2, player_pos[1], (0, 1))
            bullets.append(bullet)
            last_shot_time = current_time
        if keys[pygame.K_LEFT] and current_time - last_shot_time > 200:  # Стрельба влево
            bullet = Bullet(player_pos[0] + PLAYER_SIZE // 2, player_pos[1], (-1, 0))
            bullets.append(bullet)
            last_shot_time = current_time
        if keys[pygame.K_RIGHT] and current_time - last_shot_time > 200:  # Стрельба вправо
            bullet = Bullet(player_pos[0] + PLAYER_SIZE // 2, player_pos[1], (1, 0))
            bullets.append(bullet)
            last_shot_time = current_time

        for bullet in bullets:
            bullet.move()

        player_pos[0] = max(0, min(WIDTH - PLAYER_SIZE, player_pos[0]))
        player_pos[1] = max(0, min(HEIGHT - PLAYER_SIZE, player_pos[1]))

        enemy_spawn_time += 1
        if enemy_spawn_time > 60:
            new_enemy = spawn_enemy()
            enemies.append(new_enemy)
            enemy_spawn_time = 0

        # ```Обновление врагов и проверка коллизий```
        for enemy in enemies[:]:
            enemy.move_towards_player(player_pos)
            if (player_pos[0] < enemy.pos[0] + enemy.size and
                    player_pos[0] + PLAYER_SIZE > enemy.pos[0] and
                    player_pos[1] < enemy.pos[1] + enemy.size and
                    player_pos[1] + PLAYER_SIZE > enemy.pos[1]):
                lives -= 1
                enemies.remove(enemy)
                if lives <= 0:
                    return "LOSE"

        # ```Обновление пуль```
        for bullet in bullets[:]:
            bullet.move()
            if bullet.pos[0] < 0 or bullet.pos[0] > WIDTH or bullet.pos[1] < 0 or bullet.pos[1] > HEIGHT:
                # ```Удаление пуль, которые вышли за пределы экрана```
                bullets.remove(bullet)

        # ```Проверка коллизий между пулями и врагами```
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if (enemy.pos[0] < bullet.pos[0] < enemy.pos[0] + enemy.size and enemy.pos[1] < bullet.pos[1] < enemy.pos[1] + enemy.size):
                    enemies.remove(enemy)
                    bullets.remove(bullet)
                    killed_enemies += 1
                    break

        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - last_time) / 1000
        timer -= elapsed_time
        last_time = current_time

        if timer <= 0:
            return "WIN"

        # Отрисовка
        screen.fill(WHITE)
        pygame.draw.rect(screen, GREEN, (player_pos[0], player_pos[1], PLAYER_SIZE, PLAYER_SIZE))

        for enemy in enemies:
            enemy.draw(screen)
        for bullet in bullets:
            bullet.draw(screen)

        draw_text(f'Жизни: {lives}', 36, BLACK, screen, WIDTH // 2, 30)
        draw_text(f'Осталось времени: {int(timer)}', 36, BLACK, screen, WIDTH // 2, 60)
        draw_text(f'Убито врагов: {killed_enemies}', 36, BLACK, screen, WIDTH // 2, 90)

        pygame.display.flip()
        clock.tick(120)

    return "QUIT"


def show_training():
    running = True
    index = 0
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return False

        screen.fill(WHITE)
        screen.blit(training[index], (0, 0))
        draw_text('Двигаться', 65, BLACK, screen, WIDTH // 2 - 500, HEIGHT // 2 - 300)
        draw_text('Атака', 65, BLACK, screen, WIDTH // 2 + 500, HEIGHT // 2 - 300)
        draw_text('Для продолжения - нажмите пробел', 70, BLACK, screen, WIDTH // 2, HEIGHT // 2 + 450)
        pygame.display.flip()

        index += 1
        if index >= len(training):
            index = 0

        clock.tick(1)

    return


def display_final(result, record_saved):
    running = True
    while running:
        screen.fill(WHITE)

        if result == "WIN":
            draw_text('Поздравляем! Вы выиграли!', 85, GREEN, screen, WIDTH // 2, HEIGHT // 2 - 200)
        else:
            draw_text('Ты проиграл', 85, RED, screen, WIDTH // 2, HEIGHT // 2 - 200)

        draw_text('Убито врагов: {}'.format(killed_enemies), 70, BLACK, screen, WIDTH // 2, HEIGHT // 2 )
        menu_text = draw_text1('В меню', 75, BLACK, screen, WIDTH // 2, HEIGHT // 2 + 100)
        exit_text = draw_text1('Выход', 75, RED, screen, WIDTH // 2, HEIGHT // 2 + 200)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, record_saved
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    if menu_text.collidepoint(mouse_pos):
                        return True, record_saved
                    if exit_text.collidepoint(mouse_pos):
                        return False, record_saved

    return False, record_saved


def main_menu():
    running = True

    while running:
        screen.fill(WHITE)

        draw_text('Рогалик', 85, PINK, screen, WIDTH // 2, HEIGHT // 2 - 200)
        start_text_rect = draw_text1('Начать', 75, BLACK, screen, WIDTH // 2, HEIGHT // 2 + 100)
        exit_text_rect = draw_text1('Выход', 75, RED, screen, WIDTH // 2, HEIGHT // 2 + 200)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    if start_text_rect.collidepoint(mouse_pos):
                        return True
                    if exit_text_rect.collidepoint(mouse_pos):
                        return False

    return False


def main():
    record_saved = False  # Инициализируем флаг сохранения рекорда
    while True:
        if not main_menu():
            break
        show_training()

        game_result = game_loop()
        if game_result == "QUIT":
            break

        continue_game, record_saved = display_final(game_result, record_saved)
        if not continue_game:
            break

    pygame.quit()


if __name__ == "__main__":
    main()
