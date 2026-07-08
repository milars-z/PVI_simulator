from __future__ import annotations

from typing import TypedDict


class RecorderConfig(TypedDict):
    enabled: bool
    output_dir: str
    csv_filename: str
    round_digits: int


# Recorder settings.
# - enabled: turn CSV recording on/off without changing the simulation loop.
# - output_dir: folder created by Recorder during initialization. A relative
#   path is resolved from the project root.
# - csv_filename: result file created inside output_dir.
# - round_digits: decimal places used when formatting float fields.
RECORDER_CONFIG: RecorderConfig = {
    "enabled": True,
    "output_dir": "records/result",
    "csv_filename": "round_result.csv",
    "round_digits": 3,
}
