# world/world.py
from typing import Any

from world.world_config import WORLD_CONFIG
from agents.agent_enums import AgentType
from agents.ped_agent import PedestrianAgent
from agents.veh_agent import VehicleAgent

class World:
    def __init__(self) -> None:
        self.name = WORLD_CONFIG["name"]

        self.lane_list = WORLD_CONFIG["lane"]
        self.cross_road_list = WORLD_CONFIG["cross_road"]

        self.ped_spawn = WORLD_CONFIG["ped_spawn"]
        self.veh_spawn = WORLD_CONFIG["veh_spawn"]

        self.agent_list: list[Any] = []


    def get_ped_init_config(self) -> dict:
        lane = self._get_lane_by_id(self.veh_spawn["lane_id"])
        cross_road = self._get_cross_road_by_id(self.ped_spawn["cross_road_id"])

        return {
            "spawn_x": cross_road["bottom_x"] + self.ped_spawn["bias_x"],
            "spawn_y": cross_road["bottom_y"] + self.ped_spawn["bias_y"],
            "random_radius": self.ped_spawn["random_radius"],
            "orientation": self.ped_spawn["orientation"],
            "wait_line": cross_road["bottom_y"] + lane["width"],
            "finish_line": cross_road["bottom_y"] 
        }

    def register_ped(self, ped_agent: Any) -> None:
        self.agent_list.append(ped_agent)

    def get_veh_init_config(self) -> dict:
        lane = self._get_lane_by_id(self.veh_spawn["lane_id"])
        cross_road = self._get_cross_road_by_id(self.veh_spawn["cross_road_id"])

        return {
            # "lane_id": lane["id"],
            "veh_cross_x": cross_road["bottom_x"] - self.veh_spawn["x_bias"],
            "veh_cross_y": lane["bottom_y"] + self.veh_spawn["y_bias"],
            "orientation": self.veh_spawn["orientation"],
        }

    def register_veh(self, veh_agent: Any) -> None:
        self.agent_list.append(veh_agent)


    def _get_lane_by_id(self, lane_id: int) -> dict:
        for lane in self.lane_list:
            if lane["id"] == lane_id:
                return lane

        raise ValueError(f"Lane id {lane_id} not found.")

    def _get_cross_road_by_id(self, cross_road_id: int) -> dict:
        for cross_road in self.cross_road_list:
            if cross_road["id"] == cross_road_id:
                return cross_road

        raise ValueError(f"Cross road id {cross_road_id} not found.")