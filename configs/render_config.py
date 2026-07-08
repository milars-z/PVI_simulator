from __future__ import annotations

from typing import TypedDict


Color = tuple[int, int, int]


class RenderWindowConfig(TypedDict):
    title: str
    padding_px: int
    min_width_px: int
    min_height_px: int


class RenderScaleConfig(TypedDict):
    pixel_per_meter: int


class RenderColorConfig(TypedDict):
    background: Color
    lane: Color
    cross_road: Color
    ped: Color
    veh: Color
    agent_outline: Color


class CrossRoadMarkConfig(TypedDict):
    block_length_m: float
    gap_length_m: float


class RenderConfig(TypedDict):
    window: RenderWindowConfig
    scale: RenderScaleConfig
    color: RenderColorConfig
    cross_road_mark: CrossRoadMarkConfig


# Pygame render settings for the simulator view.
RENDER_CONFIG: RenderConfig = {
    "window": {
        "title": "Traffic Interaction Simulator",
        "padding_px": 40,
        "min_width_px": 1200,
        "min_height_px": 500,
    },

    # World meter to screen pixel conversion.
    "scale": {
        "pixel_per_meter": 20,
    },

    "color": {
        "background": (80, 80, 80),
        "lane": (130, 130, 130),
        "cross_road": (255, 255, 255),
        "ped": (255, 165, 0),
        "veh": (0, 180, 0),
        "agent_outline": (30, 30, 30),
    },

    "cross_road_mark": {
        "block_length_m": 0.2,
        "gap_length_m": 0.2,
    },
}
