import pyglet
import colorsys
from langtons_ant_model import LangtonsAntModel


# noinspection PyAbstractClass
class LangtonsAntView(pyglet.window.Window):
    def __init__(self, model: LangtonsAntModel):
        super().__init__(resizable=True)

        self.model: LangtonsAntModel = model
        self.view_position: tuple[int, int] = (0, 0)
        self.pixel_width: float = 10
        self.speed: int = 1
        self.paused: bool = True

        self.info_label = pyglet.text.Label(
            text=f"Info Text",
            x=10,
            y=self.height - 10,
            anchor_x="left",
            anchor_y="top",
            font_size=16,
        )
        self.mouse_pos_label = pyglet.text.Label(
            text=f"Mouse Pos",
            x=10,
            y=10,
            anchor_x="left",
            anchor_y="bottom",
            font_size=16,
        )

        self.set_caption("Langton's Ant")

    @staticmethod
    def get_help() -> str:
        return (
            "==== Langton's Ant Help ====\n"
            " * Left click to toggle cells\n"
            " * Scroll to zoom\n"
            " * Drag to pan\n"
            " * Space to pause\n"
            " * Right/Left to change speed\n"
            " * S to step once\n"
            " * R to reset\n"
        )

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.pixel_width *= 1 - scroll_y / -10
        self.pixel_width = max(0.1, self.pixel_width)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons & pyglet.window.mouse.LEFT:
            return

        self.view_position = (self.view_position[0] - dx, self.view_position[1] - dy)

    def on_mouse_press(self, x, y, button, modifiers):
        if button != pyglet.window.mouse.LEFT:
            return

        model_pos = self.screen_to_model(x, y)
        self.model.toggle_cell(*model_pos)

    def on_mouse_motion(self, x, y, dx, dy):
        x, y = self.screen_to_model(x, y)
        self.mouse_pos_label.text = f"Mouse Pos: {x:.0f} | {y:.0f}"

    def on_resize(self, width, height):
        super().on_resize(width, height)

        self.info_label.y = self.height - 10

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.SPACE:
            self.paused = not self.paused

        if symbol == pyglet.window.key.RIGHT:
            self.speed += 1
        if symbol == pyglet.window.key.LEFT:
            self.speed -= 1

        if symbol == pyglet.window.key.S:
            self.model.step()
        if symbol == pyglet.window.key.R:
            self.model = LangtonsAntModel()

        self.speed = max(1, self.speed)

    def model_to_screen(self, x: int, y: int) -> tuple[float, float]:
        dx = x * self.pixel_width
        dy = y * self.pixel_width

        return dx - self.view_position[0] + self.width / 2, dy - self.view_position[1] + self.height / 2

    def screen_to_model(self, x: float, y: float) -> tuple[int, int]:
        dx = x + self.view_position[0] - self.width / 2
        dy = y + self.view_position[1] - self.height / 2

        return dx // self.pixel_width, dy // self.pixel_width

    def draw_model(self):
        batch = pyglet.graphics.Batch()
        rects = []

        for x, y in self.model.grid:
            cell = self.model.get_cell(x, y)
            if cell:
                color = tuple(map(lambda v: int(v * 255), colorsys.hsv_to_rgb(cell / 3 % 256 / 255, 0.5, 1)))
            else:
                color = (0, 0, 0)

            screen_x, screen_y = self.model_to_screen(x, y)

            rects.append(
                pyglet.shapes.Rectangle(
                    x=screen_x,
                    y=screen_y,
                    width=self.pixel_width,
                    height=self.pixel_width,
                    color=color,
                    batch=batch,
                )
            )

        batch.draw()

    # noinspection PyMethodOverriding
    def on_draw(self):
        self.clear()

        self.draw_model()

        # draw ant
        screen_x, screen_y = self.model_to_screen(self.model.x, self.model.y)
        pyglet.shapes.Rectangle(
            x=screen_x + self.pixel_width / 4,
            y=screen_y + self.pixel_width / 4,
            width=self.pixel_width / 2,
            height=self.pixel_width / 2,
            color=(255, 0, 0),
        ).draw()
        ant_direction = self.model.direction_xy
        pyglet.shapes.Line(
            x=screen_x + self.pixel_width / 2,
            y=screen_y + self.pixel_width / 2,
            x2=screen_x + self.pixel_width / 2 + ant_direction[0] * self.pixel_width / 2,
            y2=screen_y + self.pixel_width / 2 + ant_direction[1] * self.pixel_width / 2,
            width=2,
            color=(0, 255, 0),
        ).draw()

        # draw info
        self.info_label.text = (
            f"Generation: {self.model.generation:,d} | "
            f"Speed: {self.speed} | "
            f"Pixel Width: {self.pixel_width:.2f} | "
            f"Paused: {self.paused} | "
            f"On cells: {len(self.model.grid)}"
        )
        self.info_label.draw()
        self.mouse_pos_label.draw()

        if not self.paused:
            for _ in range(self.speed): self.model.step()


def main():
    model = LangtonsAntModel()
    view = LangtonsAntView(model)

    print(view.get_help())

    pyglet.app.run()


if __name__ == "__main__":
    main()
