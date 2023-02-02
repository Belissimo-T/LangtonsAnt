import pyglet
import colorsys
from langtons_ant_model import *


# noinspection PyAbstractClass
class LangtonsAntView(pyglet.window.Window, LangtonsAntModelViewBase):
    def __init__(self, model: LangtonsAntModel):
        pyglet.window.Window.__init__(self, resizable=True)
        LangtonsAntModelViewBase.__init__(self, model)

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
            " * Right click drag to pan\n"
            " * Space to pause\n"
            " * Right/Left to change speed\n"
            " * S to step once\n"
            " * R to reset\n"
        )

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.zoom(scroll_y)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.curr_mouse_pos = x, y
        if buttons & pyglet.window.mouse.LEFT:
            return

        self.pan(dx, dy)

    def on_mouse_press(self, x, y, button, modifiers):
        if button != pyglet.window.mouse.LEFT:
            return

        model_pos = self.screen_to_model(x, y)
        self.model.toggle_cell(*model_pos)

    def on_mouse_motion(self, _x, _y, dx, dy):
        self.curr_mouse_pos = _x, _y
        x, y = self.screen_to_model(_x, _y)
        self.mouse_pos_label.text = f"Mouse Pos: {x:.1f} | {y:.1f}"

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

    def draw_model(self):
        batch = pyglet.graphics.Batch()
        rects = []

        for x, y in self.model.grid:
            cell = self.model.get_cell(x, y)
            if cell:
                color = self.time_to_color(cell)
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

        # draw mouse
        curr_mouse_screen_pos = self.model_to_screen(*self.screen_to_model(*self.curr_mouse_pos))
        pyglet.shapes.Rectangle(
            x=curr_mouse_screen_pos[0],
            y=curr_mouse_screen_pos[1],
            width=self.pixel_width,
            height=self.pixel_width,
            color=(255, 255, 255, 100),
        ).draw()

        # draw info
        self.info_label.text = self.get_info_text()
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
