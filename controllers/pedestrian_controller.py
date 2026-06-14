# controllers/pedestrian_controller.py

from __future__ import annotations

from typing import Any

from agents.agent_enums import PedStage,Orientation


class PedestrianController:
    """
    行人控制器。

    负责根据行人观测结果，更新每个行人的行为状态。
    例如：
    - INIT -> WAITING
    - WAITING -> CROSSING
    - CROSSING -> DANGEROUS
    - CROSSING -> FINISHED
    """

    def update(
        self,
        dt: float,
        ped_list: list[Any],
        ped_obs_list: list[Any],
    ) -> None:
        obs_map = self._build_obs_map(ped_obs_list)

        for ped in ped_list:
            ped_obs = obs_map.get(ped.ped_id)

            if ped_obs is None:
                self._update_without_observation(dt, ped)
            else:
                self._update_with_observation(dt, ped, ped_obs)

    def _build_obs_map(self, ped_obs_list: list[Any]) -> dict[int, Any]:
        """
        将 observation list 转成 dict，方便通过 ped_id 查找。
        """
        obs_map: dict[int, Any] = {}

        for obs in ped_obs_list:
            obs_map[obs.ped_id] = obs

        return obs_map

    def _update_without_observation(
        self,
        dt: float,
        ped: Any,
    ) -> None:
        """
        没有观测结果时的默认更新逻辑。
        """
        self._update_state(dt, ped, None)
        self._update_motion(dt, ped)

    def _update_with_observation(
        self,
        dt: float,
        ped: Any,
        ped_obs: Any,
    ) -> None:
        """
        有观测结果时，根据 observation 更新行人状态。
        """
        self._update_state(dt, ped, ped_obs)
        self._update_motion(dt, ped)

    def _update_state(
        self,
        dt: float,
        ped: Any,
        ped_obs: Any | None,
    ) -> None:
        """
        
        """

        if ped.stage == PedStage.INIT:
            self._handle_init_stage(dt, ped)

        elif ped.stage == PedStage.WAIT:
            self._handle_waiting_stage(dt, ped, ped_obs)

        elif ped.stage == PedStage.CROSS:
            self._handle_crossing_stage(dt, ped, ped_obs)

        elif ped.stage == PedStage.DANGEROUS:
            self._handle_dangerous_stage(dt, ped, ped_obs)

        elif ped.stage == PedStage.FINISH:
            self._handle_finish_stage(dt, ped, ped_obs)

    def _update_motion(
        self,
        dt: float,
        ped: Any,
    ) -> None:
        """
        根据当前状态更新行人位置。
        """

        if ped.stage == PedStage.WAIT:
            ped.speed = 0.0

        else :
            ped.speed = ped.ped_speed

        ped.update(dt)

        # if ped.state.value == "init":
        #     ped.pos_y += ped.speed * dt

        # elif ped.state.value == "crossing":
        #     ped.pos_y += ped.speed * dt

        # elif ped.state.value == "waiting":
        #     ped.wait_time += dt

        # elif ped.state.value == "dangerous":
        #     ped.wait_time += dt

    def _handle_init_stage(
        self,
        dt: float,
        ped: Any,
    ) -> None:
        """
        行人从生成点走向路边。
        这一段没有逻辑,模仿行人走到路边
        """

        if ped.orientation == Orientation.UP:
            if ped.pos_y <= ped.wait_line:
                ped.stage = PedStage.WAIT
        elif ped.orientation == Orientation.DOWN:
            if ped.pos_y >= ped.wait_line:
                ped.stage = PedStage.WAIT

    def _handle_waiting_stage(
        self,
        dt: float,
        ped: Any,
        ped_obs: Any | None,
    ) -> None:
        """
        行人在路边等待，根据风险判断是否开始过马路。
        行人开始观察是否过马路
        不同的行人有不同的判断依据

        行人type:ped_type string 后续做成enum
        "type_list": [     --configs.pedestrain_config.py
            "aggressive_ttc",
            "aggressive_stopping_ratio",
            "caution_stopping",
            "less_interactive",
            "less_attention",
            "less_cross",
    ],

        veh_id: int
        has_vehicle: bool
        distance: float
        ttc_gap: float
        stopping_ratio: float
        car_speed_view: float
        car_pos_x: float
        car_pos_y: float

        """

        if ped.ped_type == "aggressive_ttc":
            '''
            该类型的行人通过判断车辆的ttc_gap来决定是否过马路
            两者的ttc_gap在observation中被计算,不同的行人有不同的可接受程度
            '''
            if ped_obs.has_vehicle == True:

                for obs in ped_obs.observed_vehicles:
                    if abs(obs.ttc_gap) >= ped.acc_ttc_gap :

                        ped.stage = PedStage.CROSS

                    else:
                        ped.stage = PedStage.WAIT
            else:
                ped.stage = PedStage.CROSS


        elif ped.ped_type == "aggressive_stopping_ratio":
            '''
            该类型人倾向于判断车是否能够停在自己前方，有没有一个明显的减速倾向
            stopping_ratio 越小越安全
            '''
            if ped_obs.has_vehicle == True:
                for obs in ped_obs.observed_vehicles: 
                    if obs.stopping_ratio <= ped.acc_stop_ratio:

                        ped.stage = PedStage.CROSS
                    
                    else:
                        ped.stage = PedStage.WAIT
            else:
                ped.stage = PedStage.CROSS
        
        elif ped.ped_type == "caution_stopping":
            '''
            该类型人倾向于判断车是否在自己前方且停住
            暂时不考虑距离，只判断车的速度
            '''
            if ped_obs.has_vehicle == True:
                for obs in ped_obs.observed_vehicles: 
                    if obs.car_speed_view <= ped.acc_speed:

                        ped.stage = PedStage.CROSS
                    
                    else:
                        ped.stage = PedStage.WAIT
            else:
                ped.stage = PedStage.CROSS

        elif ped.ped_type == "less_interactive":
            '''
            该类行人拒绝与车辆交互，只有车完全驶离时才走
            '''
            if ped_obs.has_vehicle == True:
                ped.stage = PedStage.WAIT
            else:
                ped.stage = PedStage.CROSS

            if ped_obs is None:
                return
            
        elif ped.ped_type == "less_cross":
            '''
            不过马路，纯折磨
            '''
            ped.stage = PedStage.FINISH

        else:
            print(ped.ped_type)
            ped.stage = PedStage.FINISH


    def _handle_crossing_stage(
        self,
        dt: float,
        ped: Any,
        ped_obs: Any | None,
    ) -> None:
        """
        行人正在过马路。
        """

        # if ped_obs is not None and ped_obs.max_risk > 0.8:
        #     ped.stage = PedStage.DANGEROUS
        #     return

        if ped.orientation == Orientation.UP:

            if ped.pos_y <= ped.finish_line:
                ped.stage = PedStage.FINISH

        if ped.orientation == Orientation.DOWN:

            if ped.pos_y >= ped.finish_line:
                ped.stage = PedStage.FINISH

    def _handle_dangerous_stage(
        self,
        dt: float,
        ped: Any,
        ped_obs: Any | None,
    ) -> None:
        """
        危险状态下的处理。
        """

        if ped_obs is None:
            return

        if ped_obs.max_risk < ped.risk_tolerance:
            ped.stage = PedStage.CROSS

    def _handle_finish_stage(
        self,
        dt: float,
        ped: Any,
        ped_obs: Any | None,
    ) -> None:
        """
        结束状态下的处理。
        """

        pass