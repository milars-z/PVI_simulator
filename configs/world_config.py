from __future__ import annotations

from typing import TypedDict

from agents.agent_enums import Orientation


class LaneConfig(TypedDict):
    id: int
    bottom_x: float
    bottom_y: float
    width: float
    length: float


class CrossRoadConfig(TypedDict):
    id: int
    bottom_x: float
    bottom_y: float
    width: float


class PedSpawnConfig(TypedDict):
    cross_road_id: int
    bias_x: float
    bias_y: float
    orientation: Orientation


class VehSpawnConfig(TypedDict):
    lane_id: int
    cross_road_id: int
    x_bias: float
    y_bias: float
    orientation: Orientation


class WorldConfig(TypedDict):
    lane: list[LaneConfig]
    cross_road: list[CrossRoadConfig]
    ped_spawn: PedSpawnConfig
    veh_spawn: VehSpawnConfig


# Static world geometry and spawn references.
# Coordinates are in meters in the simulator world coordinate system.
WORLD_CONFIG: WorldConfig = {
    # Vehicle lanes. The current simulator uses one straight lane.
    "lane": [
        {
            "id": 0,
            "bottom_x": 0.0,
            "bottom_y": 0.0,
            "width": 6.0,
            "length": 80.0,
        }
    ],

    # Crosswalk geometry bound to the lane above.
    "cross_road": [
        {
            "id": 0,
            "bottom_x": 60.0,
            "bottom_y": 0.0,
            "width": 2.0,
        }
    ],

    # Pedestrian spawn reference.
    # bias_x/bias_y are offsets from the selected crosswalk bottom-left corner.
    "ped_spawn": {
        "cross_road_id": 0,
        "bias_x": 1.0,
        "bias_y": 7.0,
        "orientation": Orientation.UP,
    },

    # Vehicle spawn reference.
    # x_bias shifts the target crosswalk reference point left before applying
    # each vehicle combo's distance_to_crossroad_m.
    "veh_spawn": {
        "lane_id": 0,
        "cross_road_id": 0,
        "x_bias": 10.0,
        "y_bias": 2.0,
        "orientation": Orientation.RIGHT,
    },
}
