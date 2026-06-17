# scenario/scenario_manager.py

from __future__ import annotations

from enum import Enum
from typing import List

from world.world import World
from agents.ped_agent import PedestrianAgent
from agents.veh_agent import VehicleAgent
from scenario.scenario_config import SCENARIO_CONFIG


class ScenarioState(Enum):
    INIT = "init"
    RUNNING = "running"
    ROUND_FINISHED = "round_finished"
    ALL_FINISHED = "all_finished"


class ScenarioManager:
    """
    管理一组仿真场景的生命周期。

    它只负责：
    1. 生成 agent
    2. 注册 agent 到 world
    3. 判断当前 round 是否结束
    4. 清空当前 round
    5. 推进 round / epoch

    它不负责：
    1. controller 行为
    2. observation 计算
    3. world 物理更新
    4. record 记录
    5. cost / reward / training
    """

    def __init__(self, world: World) -> None:
        self.world = world
        self.config = SCENARIO_CONFIG

        self.total_epoch = self.config["total_epoch"]
        self.rounds_per_epoch = self.config["rounds_per_epoch"]
        self.base_seed = self.config["seed"]
        self.seed = self.base_seed

        self.current_epoch = 0
        self.current_round = 0

        # 全局唯一 id，从 0 开始递增
        self.next_id = 0

        self.state = ScenarioState.INIT

    def update(self) -> None:
        """
        每一帧调用一次。

        管理agent生命周期
        """

        if self.state == ScenarioState.INIT:
            self._start_new_round()
            self.state = ScenarioState.RUNNING
            return

        elif self.state == ScenarioState.RUNNING:
            if self._is_current_round_finished():
                self.state = ScenarioState.ROUND_FINISHED
                
            return

        elif self.state == ScenarioState.ROUND_FINISHED:
            self._finish_current_round()

            if self._has_next_round():
                self._start_new_round()
                self.state = ScenarioState.RUNNING
            else:
                self.state = ScenarioState.ALL_FINISHED

        elif self.state == ScenarioState.ALL_FINISHED:
            pass

        self.world.now_round = self.current_round
        self.world.now_round = self.current_epoch

        return

    def is_finished(self) -> bool:
        return self.state == ScenarioState.ALL_FINISHED

    def get_current_epoch(self) -> int:
        return self.current_epoch

    def get_current_round(self) -> int:
        return self.current_round

    def get_current_seed(self) -> int:
       
        return self.base_seed + self.current_epoch

    def _start_new_round(self) -> None:
        """
        开始一个新的 round：
        1. 生成本轮 ped
        2. 生成本轮 veh
        3. 注册到 world
        """

        ped_agents = self._generate_ped_agents(self.seed)
        veh_agents = self._generate_veh_agents(self.seed)

        self.world.register_ped(ped_agents)
        self.world.register_veh(veh_agents)

        self._print_round_info(self.seed)

        self.next_id += 1

    def _finish_current_round(self) -> None:
        """
        当前 round 结束：
        1. 清空 world agent
        2. 推进 round
        3. 如果 round 达到上限，推进 epoch
        """

        self.current_round += 1

        if self.current_round >= self.rounds_per_epoch:
            self.current_round = 0
            self.current_epoch += 1

        self.seed = self._build_round_seed()

        self.world.clear_agents()

    def _has_next_round(self) -> bool:
        return self.current_epoch < self.total_epoch

    def _is_current_round_finished(self) -> bool:
        """
        判断当前 round 是否结束。

        所有 ped 和所有 veh 都 finish，当前 round 结束。
        """
        flag = True
        
        for agent in self.world.agent_list:

            flag = flag * (agent.is_finished() == True)

        return flag


    def _build_round_seed(self) -> int:
       
        epoch_seed = self.base_seed + self.current_epoch

        return epoch_seed

    def _generate_ped_agents(self, seed: int) -> PedestrianAgent:

        ped = PedestrianAgent(
            ped_id=self.next_id,
            seed=self.seed,
        )

        ped.init_ped(self.world)

        return ped

    def _generate_veh_agents(self, seed: int) -> VehicleAgent:

        veh = VehicleAgent(
            veh_id=self.next_id,
            seed=self.seed,
        )

        veh.init_veh(self.world)

        return veh

    def _print_round_info(self, seed: int) -> None:
        print(
            "[Scenario] "
            f"epoch={self.current_epoch}, "
            f"round={self.current_round}, "
            f"seed={seed}, "
            f"ped={self.next_id}, "
            f"veh={self.next_id}"
        )