"""
Модуль для реализации игры 'Змейка'
с использованием библиотеки pygame.
"""

from random import choice

import pygame as pg

# Константы размеров окна и сетки
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Определение направлений движения змейки
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
# Карта возможных изменений направлений движения змейки
TURNS = {
    (UP, pg.K_LEFT): LEFT,
    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_LEFT): LEFT,
    (DOWN, pg.K_RIGHT): RIGHT,
    (LEFT, pg.K_UP): UP,
    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_UP): UP,
    (RIGHT, pg.K_DOWN): DOWN,
}
# Начальная позиция змейки
START_POSITION = (
    (GRID_WIDTH // 2) * GRID_SIZE,
    (GRID_HEIGHT // 2) * GRID_SIZE
)
# Определение цветов игры
BOARD_BACKGROUND_COLOR = (192, 192, 192)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
BODY_COLOR = (0, 0, 0)

# Настройки скорости игры
INITIAL_SPEED = 10
MIN_SPEED = 5
MAX_SPEED = 20

# Создание множества всех возможных позиций на игровом поле
ALL_CELLS = {
    (x * GRID_SIZE, y * GRID_SIZE)
    for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT)
}

# Настройка игрового окна
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption('Змейка | Скорость: +/- | Пауза: P')
clock = pg.time.Clock()

# Определение противоположных направлений
OPPOSITE_DIRECTION = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, color=None):
        self.position = START_POSITION
        self.body_color = color or BODY_COLOR

    def draw(self):
        """Абстрактный метод для отрисовки объекта."""
        raise NotImplementedError(
            'Метод draw должен быть реализован '
            f'в дочерних классах {type(self).__name__}'
        )

    def draw_cell(self, position, color=None, erase=False):
        """Отрисовывает отдельную ячейку игрового объекта."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color or self.body_color, rect)
        if not erase:
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Класс для яблока."""

    def __init__(self, occupied_positions=None, color=APPLE_COLOR):
        super().__init__(color)
        self.randomize_position(occupied_positions or [])

    def randomize_position(self, occupied_positions):
        """Устанавливает яблоко в случайную свободную позицию."""
        self.position = choice(tuple(ALL_CELLS - set(occupied_positions)))

    def draw(self):
        """Отрисовывает яблоко на экране."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Класс для змейки."""

    def __init__(self, color=SNAKE_COLOR):
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
        if new_direction != OPPOSITE_DIRECTION[self.direction]:
            self.direction = new_direction

    def get_head_position(self):
        """Вычисляет новую позицию головы змейки."""
        head_x, head_y = self.positions[0]
        dir_x, dir_y = self.direction
        return (
            (head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT
        )

    def move(self):
        """Двигает змейку в текущем направлении."""
        self.positions.insert(0, self.get_head_position())
        self.last = (
            self.positions.pop()
            if len(self.positions) > self.length
            else None
        )

    def draw(self):
        """Отрисовывает змейку на экране."""
        self.draw_cell(self.positions[0], self.body_color)
        if self.last:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR, erase=True)

    def check_self_collision(self):
        """Проверяет, столкнулась ли змейка сама с собой."""
        return self.length > 1 and self.positions[0] in self.positions[1:]


def handle_keys(snake, speed, paused):
    """Обрабатывает нажатия клавиш и обновляет направление змейки."""
    for event in pg.event.get():
        if (
            event.type == pg.QUIT
            or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE)
        ):
            pg.quit()
            raise SystemExit
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_p:
                paused = not paused
            elif event.key in [pg.K_PLUS, pg.K_EQUALS]:
                speed = min(speed + 1, MAX_SPEED)
            elif event.key == pg.K_MINUS:
                speed = max(speed - 1, MIN_SPEED)
            else:
                snake.update_direction(
                    TURNS.get(
                        (snake.direction, event.key),
                        snake.direction
                    )
                )
    return speed, paused


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
        speed, paused = handle_keys(snake, speed, paused)
        if not paused:
            clock.tick(speed)
            snake.move()

            if snake.check_self_collision():
                snake.reset()
                apple.randomize_position(snake.positions)
                screen.fill(BOARD_BACKGROUND_COLOR)

            elif snake.positions[0] == apple.position:
                snake.length += 1
                max_length = max(snake.length, max_length)
                apple.randomize_position(snake.positions)

            snake.draw()
            apple.draw()
        pg.display.update()
        if paused:
            pg.time.wait(100)


if __name__ == '__main__':
    main()
