from math import ceil, floor, radians, sin, cos, log2
import sys

from pygame._sdl2 import Window
import pygame
import win32api

from data import DataExtractor
from file_watch import StrongholdWatcher
from constants import (
    BACKGROUND_COLOR,
    GRID_COLOR,
    GRID_OPACITY,
    HEIGHT,
    MARKER_RADIUS,
    PLAYER_COLOR,
    RING_WIDTH,
    RINGS,
    RING_CENTER_COLOR,
    RING_COLOR,
    STRONGHOLD_COLOR,
    STRONGHOLD_DATA_PATH,
    WIDTH,
    X_AXIS_COLOR,
    Z_AXIS_COLOR,
)


class App:
    def __init__(self):
        pygame.init()

        self.display = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)

        self.window = Window.from_display_module()
        self.data = DataExtractor()
        self.stronghold_data = StrongholdWatcher(STRONGHOLD_DATA_PATH)
        self.mouse = [0, 0]

    def update(self):
        x, _, z = self.data.position
        if self.data.dimension == "the_nether":
            x *= 8
            z *= 8
        self.position = (x, z)
        angle, _ = self.data.angle
        self.angle = radians(angle + 90)
        self.scale = self.calculate_scale()
        self.center = self.calculate_center()

        self.events()
        self.stronghold_data.poll()
        self.data.capture()
        self.draw()

    def draw(self):
        self.display.fill(BACKGROUND_COLOR)

        self.draw_rings()
        self.draw_grid()

        self.draw_strongholds()
        self.draw_player()

        pygame.display.update()

    def draw_player(self):
        player_pos = self.transformed_position(self.position)
        pygame.draw.circle(
            self.display, PLAYER_COLOR, player_pos, MARKER_RADIUS
        )
        pygame.draw.line(
            self.display,
            PLAYER_COLOR,
            player_pos,
            (
                player_pos[0] + cos(self.angle) * 20,
                player_pos[1] + sin(self.angle) * 20,
            ),
        )

    def draw_rings(self):
        for ring in reversed(RINGS):
            origin = self.transformed_position((0, 0))
            pygame.draw.circle(
                self.display,
                RING_COLOR,
                origin,
                self.scale * (ring + RING_WIDTH / 2),
            )
            pygame.draw.circle(
                self.display,
                BACKGROUND_COLOR,
                origin,
                self.scale * (ring - RING_WIDTH / 2),
            )
            pygame.draw.circle(
                self.display, RING_CENTER_COLOR, origin, self.scale * ring, 1
            )

    def draw_grid(self):
        surface = pygame.Surface(self.display.get_size(), pygame.SRCALPHA)
        surface.set_alpha(round(GRID_OPACITY * 255))

        screen_size = max(self.display.get_size())
        resolution = 2 ** floor(log2((screen_size / self.scale) / 4))

        x, z = self.inverse_transform_position((0, 0))
        x = x // resolution * resolution
        z = z // resolution * resolution
        while True:
            tx, tz = self.transformed_position((x, z))
            if (
                tx > self.display.get_width()
                and tz > self.display.get_height()
            ):
                break
            pygame.draw.line(
                surface,
                GRID_COLOR,
                (tx, 0),
                (tx, self.display.get_width()),
            )
            pygame.draw.line(
                surface,
                GRID_COLOR,
                (0, tz),
                (self.display.get_height(), tz),
            )
            x += resolution
            z += resolution

        origin = self.transformed_position((0, 0))

        pygame.draw.line(
            surface,
            X_AXIS_COLOR,
            (origin[0], 0),
            (origin[0], self.display.get_width()),
            2,
        )
        pygame.draw.line(
            surface,
            Z_AXIS_COLOR,
            (0, origin[1]),
            (self.display.get_height(), origin[1]),
            2,
        )
        self.display.blit(surface, (0, 0))

    def draw_strongholds(self):
        surface = pygame.Surface(
            (MARKER_RADIUS * 2, MARKER_RADIUS * 2), pygame.SRCALPHA
        )
        for stronghold in self.stronghold_data.data:
            surface.fill((0, 0, 0, 0))
            surface.set_alpha(round(stronghold["percentage"] * 255))
            pygame.draw.circle(
                surface,
                STRONGHOLD_COLOR,
                (MARKER_RADIUS, MARKER_RADIUS),
                MARKER_RADIUS,
            )
            pos = self.transformed_position(stronghold["pos"])
            self.display.blit(
                surface, (pos[0] - MARKER_RADIUS, pos[1] - MARKER_RADIUS)
            )

    def calculate_scale(self):
        screen_size = max(self.display.get_size())
        if not self.stronghold_data.data:
            return screen_size / 4000
        delta = max(
            abs(self.position[0] - self.stronghold_data.data[0]["pos"][0]),
            abs(self.position[1] - self.stronghold_data.data[0]["pos"][1]),
        )
        view = 2 ** ceil(log2(delta))
        view *= 2

        return screen_size / (max(view, 64))

    def calculate_center(self):
        if not self.stronghold_data.data:
            return self.position
        return (
            (self.position[0] + self.stronghold_data.data[0]["pos"][0]) / 2,
            (self.position[1] + self.stronghold_data.data[0]["pos"][1]) / 2,
        )
        # Weighted average of stronghold position method
        #
        # avg_stronghold = reduce(
        #     lambda sum, stronghold: (
        #         sum[0] + stronghold["pos"][0] * stronghold["percentage"],
        #         sum[1] + stronghold["pos"][1] * stronghold["percentage"],
        #     ),
        #     self.stronghold_data.data,
        #     (0, 0),
        # )
        # return (
        #     (self.position[0] + avg_stronghold[0]) / 2,
        #     (self.position[1] + avg_stronghold[1]) / 2,
        # )

    def transformed_position(self, pos: tuple[float, float]):
        # transformed = (screen / 2) + scale * (pos - center)
        return (
            self.display.get_width() / 2
            + self.scale * (pos[0] - self.center[0]),
            self.display.get_height() / 2
            + self.scale * (pos[1] - self.center[1]),
        )

    def inverse_transform_position(self, transformed: tuple[float, float]):
        #  pos = (transformed - (screen / 2)) / scale + center
        return (
            transformed[0]
            - (self.display.get_width() / 2) / self.scale
            + self.center[0],
            transformed[1]
            - (self.display.get_width() / 2) / self.scale
            + self.center[1],
        )

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:
                    self.exit()
        x, y = win32api.GetCursorPos()
        if pygame.mouse.get_pressed()[0]:
            window_pos = self.window.position
            if isinstance(window_pos, int):
                return
            window_x, window_y = window_pos
            self.window.position = (
                window_x + x - self.mouse[0],
                window_y + y - self.mouse[1],
            )
        self.mouse[0], self.mouse[1] = x, y
        return

    def exit(self):
        pygame.quit()
        sys.exit()
