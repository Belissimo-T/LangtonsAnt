from langtons_ant_model import *

import pygame


class LangtonsAntView(LangtonsAntModelViewBase):
    def __init__(self):
        self.window = pygame.display.set_mode((800, 450), pygame.RESIZABLE)
        pygame.display.set_caption("Langton's Ant")
        self.single_surface_dimension = 15
        self.surfaces: dict[tuple[int, int], pygame.Surface] = {}
        self.mouse_button_down = False
        self.curr_mouse_pos: tuple[int, int] = (0, 0)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(["Cascadia Code", "Fira Code", "Consolas", "Monospace"], 16, bold=True)

        model = LangtonsAntModel(
            grid_changed_callback=self.set_surface_pixel
        )

        super().__init__(model)

    @property
    def width(self) -> int:
        return self.window.get_width()

    @property
    def height(self) -> int:
        return self.window.get_height()

    @staticmethod
    def init():
        pygame.init()

    def mainloop(self):
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEWHEEL:
                    self.zoom(event.y)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_button_down = True
                    if event.button == 1:
                        self.model.toggle_cell(*self.screen_to_model(*event.pos))
                if event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_button_down = False
                if event.type == pygame.MOUSEMOTION:
                    self.curr_mouse_pos = event.pos
                    if self.mouse_button_down and event.buttons[2]:
                        self.pan(*event.rel)
                    if pygame.mouse.get_pressed()[0]:
                        self.model.set_cell(*self.screen_to_model(*event.pos), self.model.generation)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    if event.key == pygame.K_r:
                        self.model = LangtonsAntModel(grid_changed_callback=self.set_surface_pixel)
                        self.surfaces = {}
                    if event.key == pygame.K_RIGHT:
                        self.speed += 1
                    if event.key == pygame.K_LEFT:
                        self.speed -= 1
                        self.speed = max(self.speed, 1)
                    if event.key == pygame.K_x:
                        self.model.step()
            # pygame.key.set_repeat(0, 1)
            pressed_keys = pygame.key.get_pressed()
            if pressed_keys[pygame.K_w]:
                self.pan(0, 10)
            if pressed_keys[pygame.K_s]:
                self.pan(0, -10)
            if pressed_keys[pygame.K_d]:
                self.pan(-10, 0)
            if pressed_keys[pygame.K_a]:
                self.pan(10, 0)

            if not self.paused:
                for _ in range(self.speed):
                    self.model.step()

            self.window.fill((0, 0, 0))

            # draw ant track
            self.blit_surfaces()

            # draw ant
            ant_pos = self.model_to_screen(self.model.x, self.model.y)
            pygame.draw.rect(
                self.window, (255, 0, 0),
                (ant_pos[0] + self.pixel_width / 4 + 1, ant_pos[1] + self.pixel_width / 4 + 1,
                 self.pixel_width // 2, self.pixel_width // 2)
            )
            ant_dir = self.model.direction_xy
            ant_tip_pos = self.model_to_screen(self.model.x + ant_dir[0] / 2, self.model.y + ant_dir[1] / 2)
            pygame.draw.line(
                self.window, (0, 255, 0),
                tuple(map(lambda v: v + self.pixel_width / 2, ant_pos)),
                tuple(map(lambda v: v + self.pixel_width / 2, ant_tip_pos)),
                width=2
            )

            # draw mouse pos
            mouse_pos = self.model_to_screen(*self.screen_to_model(*self.curr_mouse_pos))
            selection_surf = pygame.Surface((self.pixel_width,) * 2, pygame.SRCALPHA)
            selection_surf.fill((255, 255, 255, 127))
            self.window.blit(selection_surf, mouse_pos)

            # draw info
            info_text = self.font.render(
                self.get_info_text() + f" | Pages: {len(self.surfaces):,d}",
                True, (255, 255, 255)
            )
            self.window.blit(info_text, (5, 5))

            curr_model_mouse_pos = self.screen_to_model(*self.curr_mouse_pos)
            info_text2 = self.font.render(
                f"Mouse pos: {curr_model_mouse_pos[0]:.0f} | {curr_model_mouse_pos[1]:.0f}",
                True, (255, 255, 255)
            )
            self.window.blit(info_text2, (5, self.height - 5 - info_text2.get_height()))

            pygame.display.flip()
            self.clock.tick(120)

    def set_surface_pixel(self, model_pos: tuple[int, int], state: int):
        # self.view_position = -self.model.x, -self.model.y

        surface_pos = (model_pos[0] // self.single_surface_dimension,
                       model_pos[1] // self.single_surface_dimension)

        if surface_pos not in self.surfaces:
            self.surfaces[surface_pos] = pygame.Surface((self.single_surface_dimension,) * 2)
            self.surfaces[surface_pos].fill((0, 0, 20))

        surface = self.surfaces[surface_pos]

        pixel_pos = (model_pos[0] % self.single_surface_dimension,
                     model_pos[1] % self.single_surface_dimension)

        surface.set_at(pixel_pos, self.time_to_color(state) if state else (0, 0, 0))

    def blit_surfaces(self):
        for coords, surface in self.surfaces.items():
            coords = coords[0] * self.single_surface_dimension, coords[1] * self.single_surface_dimension
            screen_coords = self.model_to_screen(*coords)
            if screen_coords[0] + self.single_surface_dimension * self.pixel_width < 0:
                continue
            if screen_coords[1] + self.single_surface_dimension * self.pixel_width < 0:
                continue
            if screen_coords[0] > self.width or screen_coords[1] > self.height:
                continue

            out_surface = pygame.Surface((int(self.single_surface_dimension * self.pixel_width + 1),) * 2)
            pygame.transform.scale(surface, out_surface.get_size(), out_surface)
            self.window.blit(out_surface, screen_coords)

    @staticmethod
    def get_help() -> str:
        return (
            "==== Langton's Ant Help ====\n"
            " * Left click to toggle cells\n"
            " * Left click drag to turn on cells\n"
            " * Scroll to zoom\n"
            " * Right click drag or W/A/S/D to pan\n"
            " * Space to pause\n"
            " * Right/Left to change speed\n"
            " * X to step once\n"
            " * R to reset\n"
        )


def main():
    LangtonsAntView.init()
    print(LangtonsAntView.get_help())

    view = LangtonsAntView()
    view.mainloop()


if __name__ == '__main__':
    main()
