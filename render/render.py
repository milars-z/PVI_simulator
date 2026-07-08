# render/render.py

import pygame

from agents.agent_enums import AgentType
from agents.ped_agent import PedestrianAgent
from agents.veh_agent import VehicleAgent
from configs.render_config import RENDER_CONFIG
from configs.world_config import CrossRoadConfig
from world.world import SimulationAgent, World


class Render:
    def __init__(self, world: World) -> None:
        pygame.init()

        self.world = world
        self.config = RENDER_CONFIG

        self.pixel_per_meter = self.config["scale"]["pixel_per_meter"]
        self.padding_px = self.config["window"]["padding_px"]

        self.scene_width_px, self.scene_height_px = self._calculate_scene_size()
        self.screen_width, self.screen_height = self._calculate_window_size()

        self.offset_x_px = (self.screen_width - self.scene_width_px) // 2
        self.offset_y_px = (self.screen_height - self.scene_height_px) // 2

        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height)
        )
        pygame.display.set_caption(self.config["window"]["title"])

        self.background_surface = pygame.Surface(
            (self.screen_width, self.screen_height)
        )

        self.render_init()

    # --------------------------------------------------
    # Public interface
    # --------------------------------------------------

    def render_init(self) -> None:
        """
        Render static scene once.

        Static elements:
        - background
        - vehicle lane
        - pedestrian cross road / crosswalk

        This function should be called once after Render is created,
        unless the world map itself changes.
        """
        self.background_surface.fill(self.config["color"]["background"])

        self._render_lane(target_surface=self.background_surface)
        self._render_cross_road(target_surface=self.background_surface)

        self.screen.blit(self.background_surface, (0, 0))
        pygame.display.flip()

    def render_update(self) -> None:
        """
        Render dynamic agents.

        Every frame:
        - restore static background
        - draw agents on top
        """
        self.screen.blit(self.background_surface, (0, 0))
        self._render_agents(target_surface=self.screen)
        pygame.display.flip()

    def render(self) -> None:
        """
        Compatibility wrapper.

        Later main loop should call render_update().
        """
        self.render_update()

    # --------------------------------------------------
    # Private render functions
    # --------------------------------------------------

    def _render_lane(self, target_surface: pygame.Surface) -> None:
        for lane in self.world.lane_list:
            rect = self._world_rect_to_pygame_rect(
                bottom_x=lane["bottom_x"],
                bottom_y=lane["bottom_y"],
                width=lane["length"],
                height=lane["width"],
            )

            pygame.draw.rect(
                target_surface,
                self.config["color"]["lane"],
                rect,
            )

    def _render_cross_road(self, target_surface: pygame.Surface) -> None:
        for cross_road in self.world.cross_road_list:
            self._render_cross_road_blocks(
                target_surface=target_surface,
                cross_road=cross_road,
            )

    def _render_cross_road_blocks(
        self,
        target_surface: pygame.Surface,
        cross_road: CrossRoadConfig,
    ) -> None:
        block_length_m = self.config["cross_road_mark"]["block_length_m"]
        gap_length_m = self.config["cross_road_mark"]["gap_length_m"]

        lane_width = self._get_main_lane_width()

        current_y = cross_road["bottom_y"]
        end_y = cross_road["bottom_y"] + lane_width

        while current_y < end_y:
            block_length = min(block_length_m, end_y - current_y)

            rect = self._world_rect_to_pygame_rect(
                bottom_x=cross_road["bottom_x"],
                bottom_y=current_y,
                width=cross_road["width"],
                height=block_length,
            )

            pygame.draw.rect(
                target_surface,
                self.config["color"]["cross_road"],
                rect,
            )

            current_y += block_length_m + gap_length_m

    def _render_agents(self, target_surface: pygame.Surface) -> None:
        for agent in self.world.agent_list:
            if self._is_ped(agent):
                self._render_ped(target_surface, agent)
            elif self._is_veh(agent):
                self._render_veh(target_surface, agent)

    def _render_ped(self, target_surface: pygame.Surface, ped: PedestrianAgent) -> None:
        pos_x = getattr(ped, "pos_x")
        pos_y = getattr(ped, "pos_y")

        size_x = self._get_valid_size(getattr(ped, "size_x", 0.0), default=0.4)
        size_y = self._get_valid_size(getattr(ped, "size_y", 0.0), default=0.4)

        rect = self._world_rect_to_pygame_rect(
            bottom_x=pos_x - size_x / 2.0,
            bottom_y=pos_y - size_y / 2.0,
            width=size_x,
            height=size_y,
        )

        pygame.draw.rect(
            target_surface,
            self.config["color"]["ped"],
            rect,
        )

        pygame.draw.rect(
            target_surface,
            self.config["color"]["agent_outline"],
            rect,
            width=1,
        )

    def _render_veh(self, target_surface: pygame.Surface, veh: VehicleAgent) -> None:
        pos_x = getattr(veh, "pos_x")
        pos_y = getattr(veh, "pos_y")

        size_x = self._get_valid_size(getattr(veh, "size_x", 0.0), default=1.8)
        size_y = self._get_valid_size(getattr(veh, "size_y", 0.0), default=0.9)

        rect = self._world_rect_to_pygame_rect(
            bottom_x=pos_x - size_x / 2.0,
            bottom_y=pos_y - size_y / 2.0,
            width=size_x,
            height=size_y,
        )

        pygame.draw.rect(
            target_surface,
            self.config["color"]["veh"],
            rect,
        )

        pygame.draw.rect(
            target_surface,
            self.config["color"]["agent_outline"],
            rect,
            width=1,
        )

    # --------------------------------------------------
    # Private helper functions
    # --------------------------------------------------

    def _calculate_scene_size(self) -> tuple[int, int]:
        max_x = 0.0
        max_y = 0.0

        for lane in self.world.lane_list:
            max_x = max(max_x, lane["bottom_x"] + lane["length"])
            max_y = max(max_y, lane["bottom_y"] + lane["width"])

        lane_width = self._get_main_lane_width()

        for cross_road in self.world.cross_road_list:
            max_x = max(max_x, cross_road["bottom_x"] + cross_road["width"])
            max_y = max(max_y, cross_road["bottom_y"] + lane_width)

        scene_width_px = self._meter_to_pixel(max_x)
        scene_height_px = self._meter_to_pixel(max_y)

        return scene_width_px, scene_height_px

    def _calculate_window_size(self) -> tuple[int, int]:
        min_width_px = self.config["window"]["min_width_px"]
        min_height_px = self.config["window"]["min_height_px"]

        width_px = max(
            self.scene_width_px + self.padding_px * 2,
            min_width_px,
        )

        height_px = max(
            self.scene_height_px + self.padding_px * 2,
            min_height_px,
        )

        return width_px, height_px

    def _world_rect_to_pygame_rect(
        self,
        bottom_x: float,
        bottom_y: float,
        width: float,
        height: float,
    ) -> pygame.Rect:
        """
        Convert world coordinate to pygame coordinate.

        Important:
        lane, cross_road, ped, veh must all use this function.
        This keeps the whole world aligned after scene-centering.
        """
        x_px = self._meter_to_pixel(bottom_x)
        y_px = self._meter_to_pixel(bottom_y)
        width_px = self._meter_to_pixel(width)
        height_px = self._meter_to_pixel(height)

        return pygame.Rect(
            self.offset_x_px + x_px,
            self.offset_y_px + y_px,
            width_px,
            height_px,
        )

    def _meter_to_pixel(self, value: float) -> int:
        return int(value * self.pixel_per_meter)

    def _get_main_lane_width(self) -> float:
        if not self.world.lane_list:
            raise ValueError("World has no lane config.")

        return self.world.lane_list[0]["width"]

    def _get_valid_size(self, value: float, default: float) -> float:
        """
        Some agents may still be initialised with size_x = 0.0 / size_y = 0.0.
        A zero-size rect cannot be seen in pygame, so fallback to default.
        """
        if value <= 0.0:
            return default

        return value

    def _is_ped(self, agent: SimulationAgent) -> bool:
        return getattr(agent, "type", None) == AgentType.PEDESTRIAN

    def _is_veh(self, agent: SimulationAgent) -> bool:
        return getattr(agent, "type", None) == AgentType.VEHICLE
