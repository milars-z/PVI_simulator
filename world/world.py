# world/world.py

from world.world_config import WORLD_CONFIG


class World:
    def __init__(self) -> None:
        self.name = WORLD_CONFIG["name"]
        self.ped_spawn_points = WORLD_CONFIG["ped_spawn_points"]

    def get_ped_spawn_config(self, ped_id: int) -> dict:
        spawn_index = ped_id % len(self.ped_spawn_points)
        return self.ped_spawn_points[spawn_index]