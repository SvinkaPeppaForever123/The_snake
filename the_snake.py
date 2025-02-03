"""
Модуль для реализации игры 'Змейка'
с использованием библиотеки pygame.
"""
from random import choice

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTION_MAP = {
    (UP, pg.K_LEFT): LEFT,
    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_LEFT): LEFT,
    (DOWN, pg.K_RIGHT): RIGHT,
    (LEFT, pg.K_UP): UP,
    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_UP): UP,
    (RIGHT, pg.K_DOWN): DOWN,
}
START_POSITION = (
    (GRID_WIDTH // 2) * GRID_SIZE,
    (GRID_HEIGHT // 2) * GRID_SIZE
)

# Цвета:
BOARD_BACKGROUND_COLOR = (192, 192, 192)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
BODY_COLOR = (0, 0, 0)

# Начальная скорость движения змейки:
INITIAL_SPEED = 10
MIN_SPEED = 5
MAX_SPEED = 20

# Создаем множество всех возможных позиций на поле
ALL_CELLS = {
    (x * GRID_SIZE, y * GRID_SIZE)
    for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT)
}

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption(
    'Змейка: Управление -'
    'Стрелки, Пауза - P, Скорость - +/-'
)
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, color=None):
        """Инициализирует объект с заданным цветом и позицией."""
        self.position = START_POSITION
        self.body_color = color or BODY_COLOR

    def draw(self):
        """Абстрактный метод для отрисовки объекта."""
        raise NotImplementedError(
            'Метод draw должен быть реализован '
            f'в дочерних классах {type(self).__name__}'
        )

    def draw_cell(self, position, color=None):
        """Отрисовка одной ячейки на экране."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color or color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Класс для яблока."""

    def __init__(self, occupied_positions=None, color=APPLE_COLOR):
        """Инициализирует яблоко с случайной позицией."""
        super().__init__(color)
        self.randomize_position(occupied_positions or [])

    def randomize_position(self, occupied_positions):
        """Устанавливает случайную позицию для яблока"""
        self.position = choice(tuple(ALL_CELLS - set(occupied_positions)))

    def draw(self):
        """Отрисовывает яблоко на экране."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Класс для змейки."""

    def __init__(self, color=SNAKE_COLOR):
        """Инициализирует змейку."""
        super().__init__(color)
        self.reset()

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [START_POSITION]
        self.direction = RIGHT
        self.last = None

    def update_direction(self, new_direction):
        """Обновляет направление движения змейки."""
        opposite = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}
        if new_direction and new_direction != opposite[self.direction]:
            self.direction = new_direction

    def get_new_head_position(self):
        """Определяет, куда переместится голова змейки."""
        return (
            (self.positions[0][0] + self.direction[0] * GRID_SIZE)
            % SCREEN_WIDTH,
            (self.positions[0][1] + self.direction[1] * GRID_SIZE)
            % SCREEN_HEIGHT
        )

    def move(self):
        """Двигает змейку в текущем направлении."""
        self.positions.insert(0, self.get_new_head_position())
        self.last = (
            self.positions.pop()
            if len(self.positions) > self.length
            else None
        )

    def draw(self):
        """Отрисовывает змейку."""
        head_rect = pg.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, head_rect)  # Рисуем голову
        pg.draw.rect(screen, BORDER_COLOR, head_rect, 1)  # Рисуем границу

        if self.last:
            erase_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, erase_rect)
            # Убираем границу, чтобы не оставался след:
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, erase_rect, 1)

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def check_self_collision(self):
        """Проверяет, не укусила ли змея сама себя."""
        if (self.length > 1 and self.get_head_position() in
                self.positions[1:]):
            self.reset()
            return True


def quit_game():
    """Завершается игра."""
    pg.quit()
    raise SystemExit


def handle_keys(snake, speed, paused):
    """Обрабатывает нажатия клавиш и обновляет направление змейки."""
    for event in pg.event.get():
        if (
            event.type == pg.QUIT
            or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE)
        ):
            quit_game()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_p:
                paused = not paused
            elif event.key in [pg.K_PLUS, pg.K_EQUALS]:
                speed = min(speed + 1, MAX_SPEED)
            elif event.key == pg.K_MINUS:
                speed = max(speed - 1, MIN_SPEED)
            else:
                snake.update_direction(
                    DIRECTION_MAP.get(
                        (snake.direction, event.key),
                        snake.direction
                    )
                )
    return speed, paused


def update_window_title(speed, max_length, paused):
    """Обновляет заголовок окна с информацией о скорости и рекордной длине."""
    title = f'Змейка: Скорость - {speed}, Рекорд - {max_length}'
    if paused:
        title += ' (Пауза)'
    pg.display.set_caption(title)


def main():
    """Основной игровой цикл."""
    pg.init()
    snake = Snake()
    apple = Apple(snake.positions)
    speed = INITIAL_SPEED
    max_length = 1
    paused = False
    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        if not paused:
            clock.tick(speed)
            speed, paused = handle_keys(snake, speed, paused)
            snake.move()

            if snake.check_self_collision():
                apple = Apple(snake.positions)

            if snake.get_head_position() == apple.position:
                snake.length += 1
                max_length = max(snake.length, max_length)
                apple.randomize_position(snake.positions)

            snake.draw()
            apple.draw()
            update_window_title(speed, max_length, paused)
            pg.display.update()
        else:
            speed, paused = handle_keys(snake, speed, paused)
            update_window_title(speed, max_length, paused)
            pg.time.wait(100)


if __name__ == '__main__':
    main()
