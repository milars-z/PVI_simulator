# main.py

from pathlib import Path

from agents.ped_agent import PedestrianAgent
from records.ped_record import save_ped_agents_to_csv
from world.world import World


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


def main() -> None:
    world = World()

    ped_agents = generate_ped_agents(
        world=world,
        ped_num=PED_NUM,
        seed=SEED,
    )

    save_ped_agents_to_csv(
        ped_agents=ped_agents,
        output_path=OUTPUT_PATH,
    )

    print(f"Generated {len(ped_agents)} pedestrian agents.")
    print(f"CSV saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()