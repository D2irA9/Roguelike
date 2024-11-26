import pygame
import random
import math
# from datetime import datetime
# from sqlalchemy import create_engine, Column, DateTime, Integer
# from sqlalchemy.orm import sessionmaker, DeclarativeBase

pygame.init()

infoObject = pygame.display.Info()
WIDTH, HEIGHT = infoObject.current_w, infoObject.current_h
PLAYER_SIZE = 50
ENEMY_SIZE = 30
ENEMY_SPEED = 3
INITIAL_LIVES = 3
player_speed = 4

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PINK = (241, 156, 187)

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Game")

# ```Для рекорда```
# class Base(DeclarativeBase):
#     pass
#
# engine = create_engine("mysql+pymysql://root:1111@127.0.0.1/3ip")
# engine.connect()
# Session = sessionmaker(bind=engine)
#
# class Record(Base):
#     __tablename__ = 'Record'
#     id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
#     datetime = Column(DateTime)
#
# Base.metadata.create_all(engine)
#
# def save_record():
#     session = Session()
#     new_record = Record(datetime=datetime.now())
#     session.add(new_record)
#     session.commit()
#     session.close()


def draw_text(text, size, color, surface, x, y):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)


def draw_text1(text, size, color, surface, x, y):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)
    return text_rect


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


def game_loop():
    player_pos = [WIDTH // 2, HEIGHT // 2]
    lives = INITIAL_LIVES
    enemies = []
    enemy_spawn_time = 2
    clock = pygame.time.Clock()
    running = True
    timer = 40
    last_time = pygame.time.get_ticks()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame .K_a]:
            player_pos[0] -= player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_pos[0] += player_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player_pos[1] -= player_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player_pos[1] += player_speed

        player_pos[0] = max(0, min(WIDTH - PLAYER_SIZE, player_pos[0]))
        player_pos[1] = max(0, min(HEIGHT - PLAYER_SIZE, player_pos[1]))

        enemy_spawn_time += 1
        if enemy_spawn_time > 60:
            new_enemy = spawn_enemy()
            enemies.append(new_enemy)
            enemy_spawn_time = 0

        # Обновление врагов и проверка коллизий
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

        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - last_time) / 1000
        timer -= elapsed_time
        last_time = current_time

        if timer <= 0:
            return "WIN"

        # Отрисовка игрока
        screen.fill(WHITE)
        pygame.draw.rect(screen, GREEN, (player_pos[0], player_pos[1], PLAYER_SIZE, PLAYER_SIZE))

        for enemy in enemies:
            enemy.draw(screen)

        draw_text(f'Жизни: {lives}', 36, BLACK, screen, WIDTH // 2, 30)
        draw_text(f'Осталось времени: {int(timer)}', 36, BLACK, screen, WIDTH // 2, 60)
        pygame.display.flip()

        clock.tick(120)

    return "QUIT"


def menu(result, record_saved):
    running = True
    while running:
        screen.fill(WHITE)

        if result == "WIN":
            # ```Сохранение рекорда```
            # if not record_saved:
            #     save_record()
            #     record_saved = True
            draw_text('Поздравляем! Вы выиграли!', 85, GREEN, screen, WIDTH // 2, HEIGHT // 2 - 200)
        else:
            draw_text('Ты проиграл', 85, RED, screen, WIDTH // 2, HEIGHT // 2 - 200)

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
                        return True, record_saved  #
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
        game_result = game_loop()
        if game_result == "QUIT":
            break

        continue_game, record_saved = menu(game_result, record_saved)
        if not continue_game:
            break

    pygame.quit()


if __name__ == "__main__":
    main()
