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
from controllers.pedestrian_controller import PedestrianController
from controllers.vehicle_controller import VehicleController

# from records.record import Record
# from configs.record_config import RecordLogType

import pygame

PED_NUM = 100
SEED = 42


def generate_ped_agents(
    world: World,
    ped_num: int,
    seed: int,
) -> PedestrianAgent:

    for ped_id in range(ped_num):
        ped = PedestrianAgent(
            ped_id=ped_id,
            seed=seed,
        )

        ped.init_ped(world)

    return ped

def generate_veh_agents(
    world: World,
    veh_num: int,
    seed: int,
) -> VehicleAgent:

    for veh_id in range(veh_num):
        veh = VehicleAgent(
            veh_id=veh_id,
            seed=seed,
        )

        veh.init_veh(world)

    return veh

def main() -> None:
    world = World()
    # record = Record()
    # record.record_logs(RecordLogType.PED_INFORMATION)
    # record.record_logs(RecordLogType.PED_OBSERVATION)


    controller = ControllerManager()


    ped_agents = generate_ped_agents(
        world=world,
        ped_num=1,
        seed=SEED,
    )

    ped_agents_2 = generate_ped_agents(
        world=world,
        ped_num=2,
        seed=SEED,
    )

    veh_agents = generate_veh_agents(
        world=world,
        veh_num=1,
        seed=SEED,
    )

    veh_agents_2 = generate_veh_agents(
        world=world,
        veh_num=2,
        seed=SEED,
    )


    world.register_ped(ped_agents)
    world.register_ped(ped_agents_2)
    world.register_veh(veh_agents)
    world.register_veh(veh_agents_2)

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