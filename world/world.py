# world/world.py
from __future__ import annotations

from typing import TypedDict

from configs.world_config import (
    CrossRoadConfig,
    LaneConfig,
    PedSpawnConfig,
    VehSpawnConfig,
    WORLD_CONFIG,
)
from agents.agent_enums import Orientation
from agents.ped_agent import PedestrianAgent
from agents.veh_agent import VehicleAgent


class PedInitConfig(TypedDict):
    spawn_x: float
    spawn_y: float
    orientation: Orientation
    finish_line: float


class VehInitConfig(TypedDict):
    veh_cross_x: float
    veh_cross_y: float
    finish_x: float
    orientation: Orientation


SimulationAgent = PedestrianAgent | VehicleAgent


class World:
    def __init__(self) -> None:
        self.lane_list: list[LaneConfig] = WORLD_CONFIG["lane"]
        self.cross_road_list: list[CrossRoadConfig] = WORLD_CONFIG["cross_road"]

        self.ped_spawn: PedSpawnConfig = WORLD_CONFIG["ped_spawn"]
        self.veh_spawn: VehSpawnConfig = WORLD_CONFIG["veh_spawn"]

        self.agent_list: list[SimulationAgent] = []

        self.now_epoch = 0
        self.now_round = 0
        self.round_finished = False

    def set_round_progress(self, epoch_id: int, round_id: int) -> None:
        self.now_epoch = epoch_id
        self.now_round = round_id

    def mark_round_running(self) -> None:
        self.round_finished = False

    def mark_round_finished(self) -> None:
        self.round_finished = True

    def is_round_finished(self) -> bool:
        return self.round_finished

    def get_ped_init_config(self) -> PedInitConfig:
        cross_road = self._get_cross_road_by_id(self.ped_spawn["cross_road_id"])

        return {
            "spawn_x": cross_road["bottom_x"] + self.ped_spawn["bias_x"],
            "spawn_y": cross_road["bottom_y"] + self.ped_spawn["bias_y"],
            "orientation": self.ped_spawn["orientation"],
            "finish_line": cross_road["bottom_y"],
        }

    def register_ped(self, ped_agent: PedestrianAgent) -> None:
        self.agent_list.append(ped_agent)

    def get_veh_init_config(self) -> VehInitConfig:
        lane = self._get_lane_by_id(self.veh_spawn["lane_id"])
        cross_road = self._get_cross_road_by_id(self.veh_spawn["cross_road_id"])

        return {
            "veh_cross_x": cross_road["bottom_x"] - self.veh_spawn["x_bias"],
            "veh_cross_y": lane["bottom_y"] + self.veh_spawn["y_bias"],
            "finish_x": lane["bottom_x"] + lane["length"],
            "orientation": self.veh_spawn["orientation"],
        }

    def register_veh(self, veh_agent: VehicleAgent) -> None:
        self.agent_list.append(veh_agent)

    def get_ped_list(self) -> list[PedestrianAgent]:
        ped_list: list[PedestrianAgent] = []
        for agent in self.agent_list:
            if isinstance(agent, PedestrianAgent):
                ped_list.append(agent)
        return ped_list

    def get_veh_list(self) -> list[VehicleAgent]:
        veh_list: list[VehicleAgent] = []
        for agent in self.agent_list:
            if isinstance(agent, VehicleAgent):
                veh_list.append(agent)
        return veh_list

    def clear_agents(self) -> None:
        self.agent_list.clear()

    def _get_lane_by_id(self, lane_id: int) -> LaneConfig:
        for lane in self.lane_list:
            if lane["id"] == lane_id:
                return lane

        raise ValueError(f"Lane id {lane_id} not found.")

    def _get_cross_road_by_id(self, cross_road_id: int) -> CrossRoadConfig:
        for cross_road in self.cross_road_list:
            if cross_road["id"] == cross_road_id:
                return cross_road

        raise ValueError(f"Cross road id {cross_road_id} not found.")
