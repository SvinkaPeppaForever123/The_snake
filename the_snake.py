"""
Модуль для реализации игры 'Змейка'
с использованием библиотеки pygame.
"""
from random import randint

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
        self.body_color = color if color else BODY_COLOR

    def draw(self):
        """Абстрактный метод для отрисовки объекта."""
        raise NotImplementedError(
            'Метод draw должен быть реализован '
            f'в дочерних классах {self.__class__.__name__}'
        )

    def draw_cell(self, position, color=None):
        """Отрисовка одной ячейки на экране."""
        if color is None:
            color = self.body_color
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Класс для яблока."""

    def __init__(self, occupied_positions=None, color=APPLE_COLOR):
        """Инициализирует яблоко с случайной позицией, не попадая на змейку."""
        super().__init__(color)
        if occupied_positions is None:
            occupied_positions = []
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions):
        """Устанавливает случайную позицию для яблока."""
        while True:
            new_position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if new_position not in occupied_positions:
                self.position = new_position
                break

    def draw(self):
        """Отрисовывает яблоко на экране."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Класс для змейки."""

    def __init__(self, color=SNAKE_COLOR):
        """Инициализирует змейку, но без начальной инициализации полей."""
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
        if new_direction:
            if (
                (new_direction == UP and self.direction != DOWN)
                or (new_direction == DOWN and self.direction != UP)
                or (new_direction == LEFT and self.direction != RIGHT)
                or (new_direction == RIGHT and self.direction != LEFT)
            ):
                self.direction = new_direction

    def get_new_head_position(self):
        """Определяет, куда переместится голова змейки."""
        dx, dy = self.direction
        x, y = self.positions[0]

        new_x = (x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_y = (y + dy * GRID_SIZE) % SCREEN_HEIGHT
        return new_x, new_y

    def move(self):
        """Двигает змейку в текущем направлении."""
        self.positions.insert(0, self.get_new_head_position())

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def get_head_rect(self):
        """Возвращает прямоугольник для головы змейки."""
        return pg.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))

    def draw(self):
        """Отрисовывает змейку на экране."""
        for position in self.positions[:-1]:
            rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, self.body_color, rect)
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

        head_rect = self.get_head_rect()
        pg.draw.rect(screen, self.body_color, head_rect)
        pg.draw.rect(screen, BORDER_COLOR, head_rect, 1)

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]


def handle_keys(snake, speed, paused):
    """Обрабатывает нажатия клавиш и обновляет направление змейки."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                raise SystemExit
            elif event.key == pg.K_p:
                paused = not paused
            elif event.key == pg.K_PLUS or event.key == pg.K_EQUALS:
                speed = min(speed + 1, MAX_SPEED)
            elif event.key == pg.K_MINUS:
                speed = max(speed - 1, MIN_SPEED)
            else:
                new_direction = DIRECTION_MAP.get(
                    (snake.direction, event.key), snake.direction
                )
                snake.update_direction(new_direction)
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
    apple = Apple(snake.positions, APPLE_COLOR)
    speed = INITIAL_SPEED
    max_length = 1
    paused = False

    while True:
        if not paused:
            clock.tick(speed)
            speed, paused = handle_keys(snake, speed, paused)
            screen.fill(BOARD_BACKGROUND_COLOR)

            snake.move()
            ate_apple = snake.get_head_position() == apple.position
            if ate_apple:
                snake.length += 1
                if snake.length > max_length:
                    max_length = snake.length
                apple.randomize_position(snake.positions)
            elif snake.get_head_position() in snake.positions[1:]:
                snake.reset()
                apple = Apple(snake.positions)

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
