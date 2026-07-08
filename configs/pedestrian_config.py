from __future__ import annotations

from typing import TypedDict


class PedestrianBasicConfig(TypedDict):
    size_x: float
    size_y: float
    type_list: list[str]


class PedestrianDefaultCharaConfig(TypedDict):
    ped_speed: float


class PedestrianCharaParamConfig(TypedDict):
    values: list[float]
    noise_std: float | None


class PedestrianTypeConfig(TypedDict):
    params: dict[str, PedestrianCharaParamConfig]


# Pedestrian physical parameters used by the simulator.
# Behavior decision thresholds are intentionally not kept here.
PED_BASIC_CONFIG: PedestrianBasicConfig = {
    # Pedestrian rectangle size in world coordinates, meters.
    "size_x": 0.5,
    "size_y": 0.5,

    # Labels for scenario generation and recording. They do not imply any
    # crossing decision logic in the simulator.
    "type_list": [
        "default",
    ],
}


# Default values loaded before profile-specific overrides.
PED_DEFAULT_CHARA_CONFIG: PedestrianDefaultCharaConfig = {
    "ped_speed": 1.3,
}


# Pedestrian profile sweep values.
# The current controller reads ped.ped_speed and returns it as the fixed walking
# command. No TTC, stopping-ratio, attention, or crossing-threshold logic is
# configured here.
PED_TYPE_CHARA_CONFIG: dict[str, PedestrianTypeConfig] = {
    "default": {
        "params": {
            "ped_speed": {
                "values": [0.85, 1.3, 1.5, 2.0],
                "noise_std": 0.05,
            },
        },
    },
}
