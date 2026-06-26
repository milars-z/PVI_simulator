# configs/recorder_config.py

RECORDER_CONFIG = {
    "csv_path": "records/result/round_result.csv",

    "round_digits": 3,

    "fieldnames": [
        "epoch_id",
        "round_id",

        "veh_id",
        "veh_spawn_x",
        "veh_spawn_y",
        "veh_init_speed",

        "ped_id",
        "ped_type",
        "ped_speed",
        "ped_ttc",

        "is_collision",
        "min_distance",
        "veh_speed_at_min_distance",

        "is_yield_to_ped",
        "veh_final_speed",
    ],
}