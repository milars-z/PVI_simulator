# world/world_config.py

from agents.agent_enums import Orientation


WORLD_CONFIG = {
    "name": "simple_pvi_world",

    "ped_spawn_points": [
        {
            "spawn_x": 0.0,
            "spawn_y": 8.0,
            "orientation": Orientation.UP,
        },
        {
            "spawn_x": 1.0,
            "spawn_y": 8.0,
            "orientation": Orientation.UP,
        },
        {
            "spawn_x": -1.0,
            "spawn_y": 8.0,
            "orientation": Orientation.UP,
        },
    ],
}