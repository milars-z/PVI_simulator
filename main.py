# main.py

from pathlib import Path

from agents.ped_agent import PedestrianAgent
from agents.veh_agent import VehicleAgent
from world.world import World
from render.render import Render

import csv
from pathlib import Path

# from observations.observation import AgentObservation
from observations.ped_observation import PedestrianObservation
from observations.veh_observation import VehicleObservation

from controllers.controller_manager import ControllerManager

from scenario.scenario_manager import ScenarioManager

# from records.record import Record
# from configs.record_config import RecordLogType

import pygame

PED_NUM = 100
SEED = 42



def main() -> None:
    world = World()
    # record = Record()
    # record.record_logs(RecordLogType.PED_INFORMATION)
    # record.record_logs(RecordLogType.PED_OBSERVATION)

    controller = ControllerManager()

    scenario_manager = ScenarioManager(world)

    ped_observer = PedestrianObservation()
    veh_observer = VehicleObservation()

    render = Render(world)

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        dt=clock.get_time() / 1000.0

        scenario_manager.update()

        if scenario_manager.is_finished():
            break

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

        render.render_update()
        
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()