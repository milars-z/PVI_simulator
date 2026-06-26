from __future__ import annotations


PVI_CONFIG = {
    # Q-table persistence.
    "q_table_path": "records/q_table/pvi_q_table.json",

    # Q-table update parameters.
    "lr": 0.1,
    "gamma": 0.9,
    "epsilon_train": 0.2,
    "epsilon_eval": 0.0,
    "init_cost": 0.0,

    # Number of steps used by PCF future-state prediction.
    "future_step_k": 5,

    # Optional state debugging output.
    "record_discrete_states": False,
    "discrete_state_csv_path": "records/discrete_state.csv",

    "train_mode" :True,
}


PVI_JERK_ACTION_CONFIG = [
    {
        "action_id": 0,
        "name": "keep",
        "jerk": 0.0,
    },
    {
        "action_id": 1,
        "name": "recover",
        "jerk": 0.8,
    },
    {
        "action_id": 2,
        "name": "comfort_brake",
        "jerk": -0.45,
    },
    {
        "action_id": 3,
        "name": "accept_brake",
        "jerk": -0.8,
    },
    {
        "action_id": 4,
        "name": "normal_brake",
        "jerk": -1.5,
    },
    {
        "action_id": 5,
        "name": "hard_brake",
        "jerk": -2.0,
    },
    {
        "action_id": 6,
        "name": "emergency_brake",
        "jerk": -2.5,
    },
]
