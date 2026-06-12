# records/ped_record.py

import csv
from pathlib import Path

from agents.ped_agent import PedestrianAgent
from configs.pedestrian_config import PED_TYPE_CHARA_CONFIG

def round_float(value, digits: int = 3):
    if isinstance(value, float):
        return round(value, digits)
    return value

def build_ped_record_row(ped: PedestrianAgent) -> dict:
    active_params = list(
        PED_TYPE_CHARA_CONFIG[ped.ped_type]["params"].keys()
    )

    return {
        "ped_id": ped.ped_id,
        "seed": ped.seed,

        "agent_type": ped.type.value,
        "ped_type_id": ped.ped_type_id,
        "ped_type": ped.ped_type,
        "chara_index": ped.chara_index,
        "active_params": ",".join(active_params),

        "spawn_x": round_float(ped.spawn_x),
        "spawn_y": round_float(ped.spawn_y),
        "pos_x": round_float(ped.pos_x),
        "pos_y": round_float(ped.pos_y),

        "size_x": round_float(ped.size_x),
        "size_y": round_float(ped.size_y),

        "orientation": ped.orientation.value,

        "speed": round_float(ped.speed),
        "ped_speed": round_float(ped.ped_speed),

        "wait_time": round_float(ped.wait_time),

        "acc_ttc_gap": round_float(ped.acc_ttc_gap),
        "acc_stop_ratio": round_float(ped.acc_stop_ratio),
        "acc_speed": round_float(ped.acc_speed),

        "cross_probability": round_float(ped.cross_probability),
        "focus_probability": round_float(ped.focus_probability),
        "is_pass": ped.is_pass,

        "stage": ped.stage.value,
    }


def save_ped_agents_to_csv(
    ped_agents: list[PedestrianAgent],
    output_path: str | Path,
) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = [build_ped_record_row(ped) for ped in ped_agents]

    if not rows:
        return

    fieldnames = list(rows[0].keys())

    with output_path.open(
        mode="w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)