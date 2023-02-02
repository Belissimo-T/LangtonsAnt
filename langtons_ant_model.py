import colorsys
import math
import typing


class LangtonsAntModel:
    def __init__(self, grid_changed_callback: typing.Callable[[tuple[int, int], int], None] = lambda pos, state: None):
        self.grid: dict[tuple[int, int], int] = {}
        self.x = 0
        self.y = 0

        self.direction = 0  # 0 = up, 1 = right, 2 = down, 3 = left
        self.generation = 1

        self.grid_changed_callback = grid_changed_callback

    def turn_right(self) -> None:
        self.direction = (self.direction + 1) % 4

    def turn_left(self) -> None:
        self.direction = (self.direction - 1) % 4

    def get_cell(self, x: int, y: int) -> int:
        return self.grid.get((x, y), False)

    def set_cell(self, x: int, y: int, value: bool) -> None:
        if value:
            self.grid.update({(x, y): self.generation})
            self.grid_changed_callback((x, y), self.generation)
        else:
            self.grid.pop((x, y), None)
            self.grid_changed_callback((x, y), False)

    def toggle_cell(self, x: int, y: int) -> None:
        self.set_cell(x, y, not self.get_cell(x, y))

    @property
    def direction_xy(self) -> tuple[typing.Literal[0, 1, -1], typing.Literal[0, 1, -1]]:
        if self.direction == 0:
            return 0, 1  # up
        elif self.direction == 1:
            return 1, 0  # right
        elif self.direction == 2:
            return 0, -1  # down
        elif self.direction == 3:
            return -1, 0  # left

    def move(self) -> None:
        dx, dy = self.direction_xy
        self.x += dx
        self.y += dy

    def step(self) -> None:
        curr_cell = self.get_cell(self.x, self.y)

        # turn
        if curr_cell:
            self.turn_right()
        else:
            self.turn_left()

        # flip
        self.toggle_cell(self.x, self.y)

        # move
        self.move()

        self.generation += 1


class LangtonsAntModelViewBase:
    width: float
    height: float

    def __init__(self, model: LangtonsAntModel):
        self.model: LangtonsAntModel = model
        self.view_position: tuple[int, int] = (0, 0)  # model coordinates
        self.curr_mouse_pos: tuple[float, float] = (0, 0)
        self.pixel_width: float = 40
        self.speed: int = 1
        self.paused: bool = True

    def model_to_screen(self, x: int, y: int) -> tuple[int, int]:
        return (
            math.floor((x + self.view_position[0]) * self.pixel_width + self.width / 2),
            math.floor((y + self.view_position[1]) * self.pixel_width + self.height / 2)
        )

    def screen_to_model(self, x: float, y: float) -> tuple[int, int]:
        return (
            math.floor((x - self.width / 2) / self.pixel_width - self.view_position[0]),
            math.floor((y - self.height / 2) / self.pixel_width - self.view_position[1])
        )

    def pan(self, dx: float, dy: float) -> None:
        self.view_position = (
            self.view_position[0] + dx / self.pixel_width,
            self.view_position[1] + dy / self.pixel_width
        )

    def zoom(self, scroll_y: float) -> None:
        self.pixel_width *= 1 - scroll_y / -10
        self.pixel_width = max(0.1, self.pixel_width)

    @staticmethod
    def time_to_color(time: float) -> tuple[int, int, int]:
        return tuple[int, int, int](map(lambda v: int(v * 255), colorsys.hsv_to_rgb(time / 20 % 256 / 255, 0.5, 1)))

    def get_info_text(self) -> str:
        return (
            f"Generation: {self.model.generation:,d} | "
            f"Speed: {self.speed} | "
            f"Pixel Width: {self.pixel_width:.2f} | "
            f"Paused: {self.paused} | "
            f"Active Cells: {len(self.model.grid)}"
        )