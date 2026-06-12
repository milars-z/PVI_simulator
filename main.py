# main.py

from pathlib import Path

from agents.ped_agent import PedestrianAgent
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
) -> list[PedestrianAgent]:
    ped_agents = []

    for ped_id in range(ped_num):
        ped = PedestrianAgent(
            ped_id=ped_id,
            seed=seed,
        )

        ped.init_ped(world)
        ped_agents.append(ped)

    return ped_agents


# def main() -> None:
#     world = World()

#     ped_agents = generate_ped_agents(
#         world=world,
#         ped_num=PED_NUM,
#         seed=SEED,
#     )

#     render = Render(world)
#     render.render()

#     save_ped_agents_to_csv(
#         ped_agents=ped_agents,
#         output_path=OUTPUT_PATH,
#     )

#     print(f"Generated {len(ped_agents)} pedestrian agents.")
#     print(f"CSV saved to: {OUTPUT_PATH}")

def main() -> None:
    world = World()

    ped_agents = generate_ped_agents(
        world=world,
        ped_num=1,
        seed=SEED,
    )


    world.register_ped(ped_agents[0])

    print(f"agent_list count: {len(world.agent_list)}")

    render = Render(world)

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        render.render_update()
        clock.tick(60)

    pygame.quit()

    print(f"Generated {len(ped_agents)} pedestrian agent for render test.")


if __name__ == "__main__":
    main()