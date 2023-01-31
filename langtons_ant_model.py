import typing


class LangtonsAntModel:
    def __init__(self):
        self.grid: dict[tuple[int, int], int] = {}
        self.x = 0
        self.y = 0

        self.direction = 0  # 0 = up, 1 = right, 2 = down, 3 = left
        self.generation = 1

    def turn_right(self) -> None:
        self.direction = (self.direction + 1) % 4

    def turn_left(self) -> None:
        self.direction = (self.direction - 1) % 4

    def get_cell(self, x: int, y: int) -> int:
        return self.grid.get((x, y), False)

    def set_cell(self, x: int, y: int, value: bool) -> None:
        if value:
            self.grid.update({(x, y): self.generation})
        else:
            self.grid.pop((x, y), None)

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
