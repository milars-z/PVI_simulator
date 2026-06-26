# interaction/vehicle_state_bin_config.py

from __future__ import annotations

from interaction.bin_cutter import BinRule


VEHICLE_STATE_BIN_RULES = [
    BinRule(
        key="distance_x",
        bins=[
            -5.0,
            0.0,
            5.0,
            10.0,
            20.0,
            35.0,
            50.0,
            float("inf"),
        ],
    ),

    BinRule(
        key="distance_y",
        bins=[
            -1.5,
            -1,
            0.0,
            0.5,
            1.0,
            1.5,
            2.0,
            float("inf"),
        ],
    ),

    # 注意：这里默认 veh.speed 单位是 m/s
    # 60 km/h ≈ 16.67 m/s
    BinRule(
        key="veh_speed",
        bins=[
            0.0,
            2.0,
            5.0,
            8.0,
            11.0,
            14.0,
            16.67,
            float("inf"),
        ],
    ),

    BinRule(
        key="ped_speed",
        bins=[
            0.0,
            0.5,
            0.9,
            1.2,
            1.5,
            2.0,
            2.5,
            float("inf"),
        ],
    ),

    # ped_persona 本身就是离散值
    # 这里用 bin 模拟离散化：
    # [0,1)->0, [1,2)->1, ..., [6,7)->6
    BinRule(
        key="ped_persona",
        bins=[
            0.0,
            1.0,
            2.0,
            3.0,
            4.0,
            5.0,
            6.0,
            7.0,
        ],
    ),

    # veh_acc:
    # 减速为负，加速为正
    # 范围 [-5, 2+]
    BinRule(
        key="veh_acc",
        bins=[
            -5.0,
            -3.0,
            -2.0,
            -1.0,
            -0.3,
            0.0,
            1.0,
            2.0,
            float("inf"),
        ],
    ),

    # stopping_ratio:
    BinRule(
        key="stopping_ratio",
        bins=[
            0.0,
            0.3,
            0.6,
            1.0,
            1.2,
        ],
    ),
]