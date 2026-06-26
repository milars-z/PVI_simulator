from __future__ import annotations

from configs.pvi_config import PVI_JERK_ACTION_CONFIG
from interaction.PVI_controller import JerkAction


JERK_ACTION_LIST = [
    JerkAction(
        action_id=int(action_config["action_id"]),
        name=str(action_config["name"]),
        jerk=float(action_config["jerk"]),
    )
    for action_config in PVI_JERK_ACTION_CONFIG
]
