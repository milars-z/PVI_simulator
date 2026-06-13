# main.py

from pathlib import Path

from agents.ped_agent import PedestrianAgent
from agents.veh_agent import VehicleAgent
from records.ped_record import save_ped_agents_to_csv
from world.world import World
from render.render import Render

import pygame


OUTPUT_PATH = Path("outputs/generated_ped_agents.csv")

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

    ped_agents = generate_ped_agents(
        world=world,
        ped_num=1,
        seed=SEED,
    )

    veh_agents = generate_veh_agents(
        world=world,
        veh_num=1,
        seed=SEED,
    )


    world.register_ped(ped_agents)
    world.register_veh(veh_agents)

    print(f"agent_list count: {len(world.agent_list)}")

    render = Render(world)

    running = True
    clock = pygame.time.Clock()
    dt=clock.get_time() / 1000.0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        ped_agents.update(dt=dt)
        veh_agents.update(dt=dt)

        render.render_update()
        
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()