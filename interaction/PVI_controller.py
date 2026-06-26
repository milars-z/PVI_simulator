'''

该类用来处于人车交互逻辑

输入车辆当前状态，车量观测器状态
处理状态信息
训练阶段更新状态矩阵
根据状态信息返回action
action仅改变jerk的值,间接控制车辆运动本身

车辆观测器中部分内容由CV方面提供结果,暂不处理

处理步骤
0- 离散化状态,初始化Q-table(所有项cost均为0)

  P  初始化P为0,P的绝对值值越高证明行人的行为超出预期越多。值大于0则行人的行为更危险,小于0则更安全
1- P  如果交互已经开始一个周期,则开始判断当前状态与过去预估状态的差异性,并更新P值
2- C  状态中随机选择一种action或者寻找cost最小的action执行,并计算当前节点的cost更新,输出的action受到P的影响,但是P差异性不直接影响cost的更新?
3- F  以当前状态运行k个时间点后,所有的action会给我带来多大的cost(在k个时间点后还有没有可以接受的cost)

4- Q-table更新,C的值更新为[min(未来的n个action所带来的cost) - 当前action的cost] * lr + 当前action的cost

状态转移
主要处理jerk
状态的改变会影响speed,dis_x,dis_y,dis,进一步影响TTC


now_state = discretize_bin(veh_obs,veh) --状态离散化

P_error = get_P(now_state,future_state) -- 根据未来的state和过去求出的state判断状态是否有变化
action = get_C(now_state) -- 根据现在的状态求出应该执行的action
real_action = get_real(P_error,action)  -- 根据P和action求出需要返回的真实action
future_state = state_trans(action,veh_obs,veh,dt) -- 根据选择好的action和现在的状态,获取未来的state,state为真实数据用来计算cost
min_future_cost = get_F(future_state) -- 根据未来的state计算未来最小的cost
update_c_table(now_state,action,min_future_cost) -- 更新table
propagate_monotonic_cost(now_state,min_future_cost) -- 更新所有表格,情况越危险,cost越大


'''

# interaction/PVI_controller.py

from __future__ import annotations

import copy
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from observations.veh_observation import ObservedPedestrianResult
from agents.veh_agent import VehicleAgent


@dataclass(frozen=True)
class JerkAction:
    """
    车辆离散动作。

    action 本身不直接改变车辆位置，也不直接改变速度，
    只返回一个 jerk 档位。
    后续由 VehicleController 根据 jerk 更新 acceleration / speed / position。
    """

    action_id: int
    name: str
    jerk: float


class PCF:
    """
    该类用来处理人车交互逻辑。

    输入:
        - 车辆当前状态 veh
        - 车辆观测器状态 veh_obs

    输出:
        - JerkAction

    当前版本:
        - 只处理 C-F
        - 暂不处理 P
        - 外部只调用 get_action()

    主要流程:
        0. 离散化当前状态，初始化 Q-table
        1. 根据当前 state 搜索 action
        2. 根据 action 预测下一帧状态
        3. 根据 action 预测 K 帧后的状态
        4. 在 K 帧后的状态上遍历所有 action，计算 future min cost
        5. 更新 Q-table
        6. 返回 action
    """

    def __init__(
        self,
        dis: Any,
        calculator: Any,
        actions: list[JerkAction],
        lr: float = 0.1,
        gamma: float = 0.9,
        epsilon: float = 0.2,
        init_cost: float = 0.0,
        train: bool = True,
        q_table_path: str | Path | None = None,
    ) -> None:
        """
        参数:
            dis:
                状态离散化器。
                要求提供:
                    dis.discretize(veh_obs=veh_obs, veh=veh)

            calculator:
                cost 计算器。
                要求提供:
                    calculator.calculate(veh, veh_obs)

            actions:
                jerk 动作列表。

            lr:
                Q-table 更新学习率。

            gamma:
                future cost 折扣系数。

            epsilon:
                随机探索概率。

            init_cost:
                Q-table 初始化 cost。

            train:
                是否处于训练阶段。
                True  表示会随机探索并更新 Q-table。
                False 表示只选择当前 cost 最小的 action，不更新。
        """

        self.dis = dis
        self.calculator = calculator
        self.actions = actions

        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
        self.init_cost = init_cost
        self.train = train
        self.q_table_path = Path(q_table_path) if q_table_path is not None else None

        # Q-table:
        #
        # {
        #     state: {
        #         action_id: cost
        #     }
        # }
        #
        # state 是离散化后的 tuple[int, ...]
        # action_id 是 jerk action 的 id
        # cost 是该 state-action 对应的估计代价
        self.q_table: dict[tuple[int, ...], dict[int, float]] = {}
        self.training_steps = 0

        # 预留给 P 模块，当前版本暂不使用
        self.p_error: float = 0.0

        # 记录上一次预测的 future_state
        # 后续做 P 的时候可以用:
        #     P_error = get_P(now_state, last_future_state)
        self.last_future_state: tuple[int, ...] | None = None

        if self.q_table_path is not None:
            self.load_q_table(self.q_table_path)

        #记录本轮变更的值
        self.change_value = 0.0


    # ==================================================
    # 外部唯一接口
    # ==================================================

    def get_action(
        self,
        veh: VehicleAgent,
        veh_obs: ObservedPedestrianResult,
        dt: float,
        k: int,
    ) -> JerkAction:
        """
        外部唯一调用接口。

        输入:
            veh:
                当前真实车辆对象。

            veh_obs:
                当前真实车辆观测结果。

            dt:
                当前仿真步长。

            k:
                future state 的预测帧数。

        输出:
            JerkAction:
                当前应该执行的 jerk action。

        流程:
            1. now_state = discretize_state(veh_obs, veh)
            2. 初始化 now_state
            3. action = search_action(now_state)
            4. current_cost = calculate_current_cost(veh, veh_obs)
            5. next_state = predict_one_step_state(action, veh, veh_obs, dt)
            6. future_state = predict_k_step_state(action, veh, veh_obs, dt, k)
            7. min_future_cost = get_future_min_cost(future_veh, future_veh_obs, dt)
            8. update_q_table(now_state, action, current_cost, min_future_cost)
            9. 返回 action

        """

        # 1. 当前状态离散化
        now_state = self.discretize_state(
            veh_obs=veh_obs,
            veh=veh,
        )

        # 2. 初始化当前 state
        self.init_state_if_needed(now_state)

        # 3. 搜索 action
        action = self.search_action(
            state=now_state,
        )

        # 推理阶段只返回 action，不更新 Q-table
        if not self.train:
            return action

        # 4. 当前真实 cost
        current_cost = self.calculate_current_cost(
            veh=veh,
            veh_obs=veh_obs,
        )

        # 5. 预测当前 action 执行 1 帧后的状态
        next_state, _, _ = self.predict_one_step_state(
            action=action,
            veh=veh,
            veh_obs=veh_obs,
            dt=dt,
        )

        # 6. 预测当前 action 持续执行 K 帧后的状态
        future_state, future_veh, future_veh_obs = self.predict_k_step_state(
            action=action,
            veh=veh,
            veh_obs=veh_obs,
            dt=dt,
            k_times=k,
        )

        self.init_state_if_needed(next_state)
        self.init_state_if_needed(future_state)

        # 7. 在 K 帧后的状态上，遍历所有 action，求最小 future cost
        min_future_cost = self.get_future_min_cost(
            veh=future_veh,
            veh_obs=future_veh_obs,
            dt=dt,
        )

        # 8. 更新 Q-table
        self.update_q_table(
            now_state=now_state,
            action=action,
            current_cost=current_cost,
            min_future_cost=min_future_cost,
        )

        # 9. 预留: 单调传播更新
        self.propagate_monotonic_cost(
            now_state=now_state,
            min_future_cost=min_future_cost,
        )

        # 10. 记录 future_state，后续 P 模块使用
        self.last_future_state = future_state

        # 11. 返回 action
        return action

    # ==================================================
    # 0. 初始化 Q-table
    # ==================================================

    def init_state_if_needed(
        self,
        state: tuple[int, ...],
    ) -> None:
        """
        如果 Q-table 中没有当前 state，则初始化。

        每个 state 下包含所有 action。
        每个 action 初始 cost 为 self.init_cost。
        """

        if state not in self.q_table:
            self.q_table[state] = {}

            for action in self.actions:
                self.q_table[state][action.action_id] = self.init_cost

    # ==================================================
    # 1. 状态离散化
    # ==================================================

    def discretize_state(
        self,
        veh_obs: ObservedPedestrianResult,
        veh: VehicleAgent,
    ) -> tuple[int, ...]:
        """
        状态离散化接口。

        当前调用:
            self.dis.discretize(veh_obs=veh_obs, veh=veh)

        返回:
            tuple[int, ...]

        注意:
            Q-table 的 key 必须是可哈希对象，
            所以 list 需要转成 tuple。
        """

        state = self.dis.discretize(
            veh_obs=veh_obs,
            veh=veh,
        )

        return tuple(state)

    # ==================================================
    # 2. 搜索 action
    # ==================================================

    def search_action(
        self,
        state: tuple[int, ...],
    ) -> JerkAction:
        """
        根据当前 state 搜索 action。

        训练阶段:
            epsilon 概率随机探索。
            其余情况选择 cost 最小的 action。

        推理阶段:
            直接选择 cost 最小的 action。

        由于当前 Q-table 存的是 cost，
        所以这里选择 min，而不是 max。
        """

        self.init_state_if_needed(state)

        if self.train and random.random() < self.epsilon:
            return random.choice(self.actions)

        best_action_id = min(
            self.q_table[state],
            key=lambda action_id: self.q_table[state][action_id],
        )

        return self.get_action_by_id(best_action_id)

    def get_action_by_id(
        self,
        action_id: int,
    ) -> JerkAction:
        """
        根据 action_id 找到 JerkAction。
        """

        for action in self.actions:
            if action.action_id == action_id:
                return action

        raise KeyError(f"Unknown action_id: {action_id}")

    # ==================================================
    # 3. 当前 cost 判断
    # ==================================================

    def calculate_current_cost(
        self,
        veh: VehicleAgent,
        veh_obs: ObservedPedestrianResult,
    ) -> float:
        """
        计算当前状态下的真实 cost。

        当前调用:
            self.calculator.calculate(veh, veh_obs)
        """

        total_cost = self.calculator.calculate(
            veh,
            veh_obs,
        )

        return float(total_cost)

    # ==================================================
    # 4. 状态预测
    # ==================================================

    def copy_sim_state(
        self,
        veh: VehicleAgent,
        veh_obs: ObservedPedestrianResult,
    ) -> tuple[VehicleAgent, ObservedPedestrianResult]:
        """
        复制车辆和观测结果，避免预测时修改真实环境。

        Python 中对象作为参数传入函数时，函数内部拿到的是对象引用。
        如果直接写 veh.speed = ...，会修改外部真实 veh。
        所以这里统一使用 deepcopy。
        """

        sim_veh = copy.deepcopy(veh)
        sim_veh_obs = copy.deepcopy(veh_obs)

        return sim_veh, sim_veh_obs

    def predict_one_step_state(
        self,
        action: JerkAction,
        veh: VehicleAgent,
        veh_obs: ObservedPedestrianResult,
        dt: float,
    ) -> tuple[
        tuple[int, ...],
        VehicleAgent,
        ObservedPedestrianResult,
    ]:
        """
        预测执行 action 一帧后的状态。

        返回:
            next_state:
                一帧后的离散状态。

            sim_veh:
                一帧后的模拟车辆对象。

            sim_veh_obs:
                一帧后的模拟车辆观测结果。

        注意:
            当前版本假设:
                - 行人向上走，所以 ped_pos_y 减小。
                - 车辆向左走，所以 veh.pos_x 减小。
            如果后续支持其他方向，需要根据 orientation 扩展。
        """

        sim_veh, sim_veh_obs = self.copy_sim_state(
            veh=veh,
            veh_obs=veh_obs,
        )

        self.apply_prediction_step(
            action=action,
            veh=sim_veh,
            veh_obs=sim_veh_obs,
            dt=dt,
            k_times=1,
        )

        next_state = self.discretize_state(
            veh_obs=sim_veh_obs,
            veh=sim_veh,
        )

        return next_state, sim_veh, sim_veh_obs

    def predict_k_step_state(
        self,
        action: JerkAction,
        veh: VehicleAgent,
        veh_obs: ObservedPedestrianResult,
        dt: float,
        k_times: int,
    ) -> tuple[
        tuple[int, ...],
        VehicleAgent,
        ObservedPedestrianResult,
    ]:
        """
        预测执行 action 持续 k_times 帧后的状态。

        返回:
            future_state:
                K 帧后的离散状态。

            sim_veh:
                K 帧后的模拟车辆对象。

            sim_veh_obs:
                K 帧后的模拟车辆观测结果。

        注意:
            该函数内部会 deepcopy，不会修改真实 veh / veh_obs。
        """

        sim_veh, sim_veh_obs = self.copy_sim_state(
            veh=veh,
            veh_obs=veh_obs,
        )

        self.apply_prediction_step(
            action=action,
            veh=sim_veh,
            veh_obs=sim_veh_obs,
            dt=dt,
            k_times=k_times,
        )

        future_state = self.discretize_state(
            veh_obs=sim_veh_obs,
            veh=sim_veh,
        )

        return future_state, sim_veh, sim_veh_obs

    def apply_prediction_step(
        self,
        action: JerkAction,
        veh: VehicleAgent,
        veh_obs: ObservedPedestrianResult,
        dt: float,
        k_times: int,
    ) -> None:
        """
        在模拟对象上执行预测，不返回值，直接修改 sim_veh 和 sim_veh_obs。

        这里传入的 veh / veh_obs 必须是 deepcopy 后的模拟对象，
        不应该是真实环境中的对象。

        预测内容:
            - ped_pos_y
            - veh.jerk
            - veh.acceleration
            - veh.speed
            - veh.pos_x
        """

        if dt <= 0.0 or k_times <= 0:
            return

        ped_pos_y = veh_obs.ped_pos_y
        ped_speed = veh_obs.ped_speed

        jerk = action.jerk

        veh_acc = veh.acceleration
        veh_speed = veh.speed
        veh_pos_x = veh.pos_x

        total_t = dt * k_times

        veh_distance = self.calc_distance_with_jerk(
            speed=veh_speed,
            acc=veh_acc,
            jerk=jerk,
            dt=dt,
            k=k_times,
        )

        # 行人向上走，所以 y 减小。
        # 当前版本只兼容行人向上走。
        veh_obs.ped_pos_y = ped_pos_y - ped_speed * total_t

        # 车辆 jerk / acceleration / speed 更新。
        veh.jerk = jerk
        veh.acceleration = veh_acc + jerk * total_t

        # v = v0 + a0 * t + 0.5 * j * t^2
        veh.speed = max(
            1e-6,
            veh_speed
            + veh_acc * total_t
            + 0.5 * jerk * total_t * total_t,
        )

        # 车辆向左走，所以 x 减小。
        # 如果 calc_distance_with_jerk 返回负数，这里会自然变成 pos_x - negative。
        veh.pos_x = veh_pos_x - veh_distance

    def state_transition(
        self,
        now_state: tuple[int, ...],
        action: JerkAction,
        veh: VehicleAgent,
        veh_obs: ObservedPedestrianResult,
        dt: float,
        k_times: int,
    ) -> dict[str, tuple[int, ...]]:
        """
        状态转移包装函数。

        这个函数保留是为了兼容你之前的调用方式。
        内部已经拆成:
            - predict_one_step_state()
            - predict_k_step_state()

        返回:
            {
                "next_state": 下一帧离散状态,
                "future_state": K 帧后的离散状态,
            }
        """

        next_state, _, _ = self.predict_one_step_state(
            action=action,
            veh=veh,
            veh_obs=veh_obs,
            dt=dt,
        )

        future_state, _, _ = self.predict_k_step_state(
            action=action,
            veh=veh,
            veh_obs=veh_obs,
            dt=dt,
            k_times=k_times,
        )

        return {
            "next_state": next_state,
            "future_state": future_state,
        }

    # ==================================================
    # 5. Future cost 判断
    # ==================================================

    def get_future_min_cost(
        self,
        veh: VehicleAgent,
        veh_obs: ObservedPedestrianResult,
        dt: float,
    ) -> float:
        """
        在某个 future 状态下，遍历所有 action，计算下一帧 cost。
        F = min_a cost(one_step(future_state, a))
        """

        min_future_cost = float("inf")

        for action in self.actions:
            _, sim_veh, sim_veh_obs = self.predict_one_step_state(
                action=action,
                veh=veh,
                veh_obs=veh_obs,
                dt=dt,
            )

            future_cost = self.calculate_current_cost(
                veh=sim_veh,
                veh_obs=sim_veh_obs,
            )

            min_future_cost = min(
                min_future_cost,
                future_cost,
            )

        return float(min_future_cost)

    # ==================================================
    # 6. Q-table 更新
    # ==================================================

    def update_q_table(
        self,
        now_state: tuple[int, ...],
        action: JerkAction,
        current_cost: float,
        min_future_cost: float,
    ) -> None:
        """
        更新 Q-table。
        """

        self.init_state_if_needed(now_state)

        old_cost = self.q_table[now_state][action.action_id]

        target_cost = current_cost + self.gamma * min_future_cost

        new_cost = old_cost + self.lr * (
            target_cost - old_cost
        )

        change = abs(new_cost - old_cost)

        self.q_table[now_state][action.action_id] = new_cost
        
        self.change_value += change 

    # ==================================================
    # 7. 单调 cost 传播，暂时留接口
    # ==================================================

    def load_q_table(
        self,
        path: str | Path | None = None,
    ) -> None:
        """
        Load Q-table values from JSON.

        Runtime:
            self.q_table[state_tuple][action_id] = cost

        JSON:
            {
                "state": [..],
                "costs": {
                    "0": 1.2,
                    "1": 0.8
                }
            }
        """

        q_table_path = Path(path) if path is not None else self.q_table_path

        if q_table_path is None or not q_table_path.exists():
            return

        with q_table_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        rows = payload.get("q_table", [])
        loaded_table: dict[tuple[int, ...], dict[int, float]] = {}

        for row in rows:
            raw_state = row.get("state", [])
            saved_costs = row.get("costs", {})

            try:
                state = tuple(int(value) for value in raw_state)
            except (TypeError, ValueError):
                continue

            if not state:
                continue

            action_costs: dict[int, float] = {}

            for action in self.actions:
                raw_cost = saved_costs.get(
                    str(action.action_id),
                    self.init_cost,
                )

                try:
                    action_costs[action.action_id] = float(raw_cost)
                except (TypeError, ValueError):
                    action_costs[action.action_id] = float(self.init_cost)

            loaded_table[state] = action_costs

        self.q_table = loaded_table
        # self.training_steps = int(payload.get("training_steps", 0))

    def save_q_table(
        self,
        path: str | Path | None = None,
    ) -> None:
        """
        Save Q-table values to JSON so the next training run can continue.
        """

        q_table_path = Path(path) if path is not None else self.q_table_path

        if q_table_path is None:
            return

        q_table_path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "state_count": len(self.q_table),
            "q_table": [
                {
                    "state": list(state),
                    "costs": {
                        str(action_id): float(cost)
                        for action_id, cost in sorted(costs.items())
                    },
                }
                for state, costs in sorted(self.q_table.items())
            ],
        }

        with q_table_path.open("w", encoding="utf-8") as file:
            json.dump(
                payload,
                file,
                ensure_ascii=False,
                indent=2,
            )

        print("loss:", self.change_value)

    def propagate_monotonic_cost(
        self,
        now_state: tuple[int, ...],
        min_future_cost: float,
    ) -> None:
        """
        单调 cost 传播接口。
        当前版本先不实现。

        """

        pass

    # ==================================================
    # 8. 预留 P 模块接口
    # ==================================================

    def get_p_error(
        self,
        now_state: tuple[int, ...],
        last_future_state: tuple[int, ...] | None,
    ) -> float:
        """
        P 模块接口，当前不使用。
        """

        return 0.0

    def get_real_action(
        self,
        p_error: float,
        action: JerkAction,
    ) -> JerkAction:
        """
        P 修正 action 接口，当前不使用。

        后续含义:
            根据 P_error 修正原本 action。

        例如:
            如果 P_error > 0，选择更强 jerk。
            如果 P_error < 0，选择更弱 jerk。
        """

        return action

    # ==================================================
    # 9. 运动学计算
    # ==================================================

    def calc_distance_with_jerk(
        self,
        speed: float,
        acc: float,
        jerk: float,
        dt: float,
        k: int,
    ) -> float:
        """
        计算车辆在同一个 jerk 下连续运行 k 个 dt 后的位移。
        """

        if dt <= 0.0 or k <= 0:
            return 0.0

        eps = 1e-9
        total_t = dt * k

        def displacement(t: float) -> float:
            return (
                speed * t
                + 0.5 * acc * t ** 2
                + (1.0 / 6.0) * jerk * t ** 3
            )

        def velocity(t: float) -> float:
            return (
                speed
                + acc * t
                + 0.5 * jerk * t ** 2
            )

        if abs(speed) < eps:
            return displacement(total_t)

        direction = 1.0 if speed > 0.0 else -1.0

        v_end = velocity(total_t)

        if v_end * direction >= 0.0:
            return displacement(total_t)

        stop_times: list[float] = []

        if abs(jerk) < eps:
            if abs(acc) > eps:
                t_stop = -speed / acc

                if 0.0 <= t_stop <= total_t:
                    stop_times.append(t_stop)
        else:
            a = 0.5 * jerk
            b = acc
            c = speed

            discriminant = b ** 2 - 4.0 * a * c

            if discriminant >= 0.0:
                sqrt_d = math.sqrt(discriminant)

                t1 = (-b - sqrt_d) / (2.0 * a)
                t2 = (-b + sqrt_d) / (2.0 * a)

                if 0.0 <= t1 <= total_t:
                    stop_times.append(t1)

                if 0.0 <= t2 <= total_t:
                    stop_times.append(t2)

        if not stop_times:
            return displacement(total_t)

        t_stop = min(stop_times)

        return displacement(t_stop)
