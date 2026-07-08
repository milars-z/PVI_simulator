from __future__ import annotations

from typing import TypedDict


class ScenarioConfig(TypedDict):
    total_epoch: int
    rounds_per_epoch: int
    seed: int


# Scenario loop settings.
# One round spawns one vehicle and one pedestrian. The simulator advances to
# the next round after both agents reach their configured finish conditions.
SCENARIO_CONFIG: ScenarioConfig = {
    # Number of epochs to run.
    "total_epoch": 1,

    # Number of rounds per epoch. Current vehicle combos contain 35 cases.
    "rounds_per_epoch": 20 * 35,

    # Base seed for deterministic pedestrian profile noise.
    "seed": 42,
}
