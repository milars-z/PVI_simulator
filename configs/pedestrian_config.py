PED_BASIC_CONFIG = {
    "size_x": 0.5,
    "size_y": 0.5,

    "cross_probability": 1.0,
    "focus_probability": 1.0,
    "is_pass": True,

    "type_list": [
        "aggressive_ttc",
        "aggressive_stopping_ratio",
        "caution_stopping",
        "less_interactive",
        "less_attention",
        "less_cross",
    ],
}


PED_DEFAULT_CHARA_CONFIG = {
    "ped_speed": 1.3,

    "acc_ttc_gap": None,
    "acc_stop_ratio": None,
    "acc_speed": None,

    "cross_probability": 1.0,
    "focus_probability": 1.0,
    "is_pass": True,
}


PED_TYPE_CHARA_CONFIG = {
    "aggressive_ttc": {
        "params": {
            "acc_ttc_gap": {
                "values": [0.5, 1.5, 3.0],
                "noise_std": 0.2,
            },
            "ped_speed": {
                "values": [0.85,1.3,1.5],
                "noise_std": 0.05,
            },
        },
    },

    "aggressive_stopping_ratio": {
        "params": {
            "acc_stop_ratio": {
                "values": [0.9, 1.0, 1.1],
                "noise_std": 0.03,
            },
            "ped_speed": {
                "values": [0.85,1.3,1.5],
                "noise_std": 0.05,
            },
        },
    },

    "caution_stopping": {
        "params": {
            "acc_speed": {
                "values": [0.3, 0.5, 0.8],
                "noise_std": 0.05,
            },
            "ped_speed": {
                "values": [0.85,1.3,1.5],
                "noise_std": 0.05,
            },
        },
    },

    "less_interactive": {
        "params": {
            "ped_speed": {
                "values": [0.85,1.3,1.5],
                "noise_std": 0.05,
            },
        },
    },

    "less_attention": {
        "params": {
            "ped_speed": {
                "values": [0.85,1.3,1.5],
                "noise_std": 0.05,
            },
        },
    },

    "less_cross": {
        "params": {
            ## none
        },
    },
}