# main.py

import pygame

from world.world import World
from render.render import Render

from observations.ped_observation import PedestrianObservation
from observations.veh_observation import VehicleObservation

from controllers.controller_manager import ControllerManager
from scenario.scenario_manager import ScenarioManager
from records.recorder import Recorder


# ==================================================
# Run Config
# ==================================================

FPS = 25
TRAIN_DT = 1.0 / FPS

ENABLE_RECORD = False


def build_simulation():
    """
    构建仿真所需对象。

    注意：
    - world / controller / observer / scenario / recorder
      在 train 和 render 模式下完全一致
    - render 只在可视化模式下创建
    """

    world = World()
    recorder = Recorder()

    controller = ControllerManager()
    scenario_manager = ScenarioManager(world)

    ped_observer = PedestrianObservation()
    veh_observer = VehicleObservation()

    return {
        "world": world,
        "recorder": recorder,
        "controller": controller,
        "scenario_manager": scenario_manager,
        "ped_observer": ped_observer,
        "veh_observer": veh_observer,
    }


def simulation_step(
    dt: float,
    world: World,
    controller: ControllerManager,
    scenario_manager: ScenarioManager,
    ped_observer: PedestrianObservation,
    veh_observer: VehicleObservation,
    recorder: Recorder,
) -> bool:
    """
    执行一帧仿真逻辑。

    返回：
        True  : 继续运行
        False : 仿真结束
    """

    scenario_manager.update()

    if scenario_manager.is_finished():
        controller.save_q_table()
        return False

    ped_obs_list = ped_observer.update(world)
    veh_obs_list = veh_observer.update(world)

    observations = {
        "pedestrian": ped_obs_list,
        "vehicle": veh_obs_list,
    }

    controller.update(
        dt=dt,
        world=world,
        observations=observations,
    )

    if ENABLE_RECORD:
        recorder.record(world)

    return True


def run_with_render() -> None:
    """
    可视化运行模式。

    特点：
    - 创建 pygame 窗口
    - 渲染场景
    - 使用 clock.tick(FPS) 限制帧率
    """

    pygame.init()

    sim = build_simulation()

    world = sim["world"]
    controller = sim["controller"]
    scenario_manager = sim["scenario_manager"]
    ped_observer = sim["ped_observer"]
    veh_observer = sim["veh_observer"]
    recorder = sim["recorder"]

    render = Render(world)
    clock = pygame.time.Clock()

    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        should_continue = simulation_step(
            dt=dt,
            world=world,
            controller=controller,
            scenario_manager=scenario_manager,
            ped_observer=ped_observer,
            veh_observer=veh_observer,
            recorder=recorder,
        )

        if not should_continue:
            break

        render.render_update()

    pygame.quit()


def run_training() -> None:
    """
    训练模式。

    特点：
    - 不创建 pygame 窗口
    - 不渲染
    - 不使用 clock.tick 限帧
    - 使用固定 dt，保证仿真逻辑稳定
    """

    sim = build_simulation()

    world = sim["world"]
    controller = sim["controller"]
    scenario_manager = sim["scenario_manager"]
    ped_observer = sim["ped_observer"]
    veh_observer = sim["veh_observer"]
    recorder = sim["recorder"]

    while True:
        should_continue = simulation_step(
            dt=TRAIN_DT,
            world=world,
            controller=controller,
            scenario_manager=scenario_manager,
            ped_observer=ped_observer,
            veh_observer=veh_observer,
            recorder=recorder,
        )

        if not should_continue:
            break


