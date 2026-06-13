# configs/veh_config.py

VEH_BASIC_CONFIG = {
    "size_x": 4.5,
    "size_y": 2.0,

    # 车辆物理约束
    "max_jerk": 4.0,              # m/s^3
    "max_deceleration": 6.0,      # m/s^2
    "max_acceleration": 2.0,      # m/s^2，暂时保留，后续 controller 可能会用

    # 默认初始控制量
    "init_acceleration": 0.0,
    "init_jerk": 0.0,
}


VEH_COMBO_CONFIG = {
    # 每一个 combo 代表一组实验条件：
    # 车辆距离 crossroad 的初始距离 + 初始速度
    #
    # distance_to_crossroad_m:
    #   表示车辆生成时距离 crossroad 的距离
    #
    # init_speed_kmh:
    #   表示车辆初始速度
    "combo_list": [
        
        # dis = 50.0
        {
            "combo_name": "d50_v60",
            "distance_to_crossroad_m": 50.0,
            "init_speed_kmh": 60.0,
        },
        {
            "combo_name": "d50_v55",
            "distance_to_crossroad_m": 50.0,
            "init_speed_kmh": 55.0,
        },
        {
            "combo_name": "d50_v50",
            "distance_to_crossroad_m": 50.0,
            "init_speed_kmh": 50.0,
        },
        {
            "combo_name": "d50_v45",
            "distance_to_crossroad_m": 50.0,
            "init_speed_kmh": 45.0,
        },
        {
            "combo_name": "d50_v40",
            "distance_to_crossroad_m": 50.0,
            "init_speed_kmh": 40.0,
        },
        {
            "combo_name": "d50_v35",
            "distance_to_crossroad_m": 50.0,
            "init_speed_kmh": 35.0,
        },
        {
            "combo_name": "d50_v30",
            "distance_to_crossroad_m": 50.0,
            "init_speed_kmh": 30.0,
        },

        # dis = 45.0
        {
            "combo_name": "d45_v60",
            "distance_to_crossroad_m": 45.0,
            "init_speed_kmh": 60.0,
        },
        {
            "combo_name": "d45_v55",
            "distance_to_crossroad_m": 45.0,
            "init_speed_kmh": 55.0,
        },
        {
            "combo_name": "d45_v50",
            "distance_to_crossroad_m": 45.0,
            "init_speed_kmh": 50.0,
        },
        {
            "combo_name": "d45_v45",
            "distance_to_crossroad_m": 45.0,
            "init_speed_kmh": 45.0,
        },
        {
            "combo_name": "d45_v40",
            "distance_to_crossroad_m": 45.0,
            "init_speed_kmh": 40.0,
        },
        {
            "combo_name": "d45_v35",
            "distance_to_crossroad_m": 45.0,
            "init_speed_kmh": 35.0,
        },
        {
            "combo_name": "d45_v30",
            "distance_to_crossroad_m": 45.0,
            "init_speed_kmh": 30.0,
        },

        # dis = 40.0
        {
            "combo_name": "d40_v60",
            "distance_to_crossroad_m": 40.0,
            "init_speed_kmh": 60.0,
        },
        {
            "combo_name": "d40_v55",
            "distance_to_crossroad_m": 40.0,
            "init_speed_kmh": 55.0,
        },
        {
            "combo_name": "d40_v50",
            "distance_to_crossroad_m": 40.0,
            "init_speed_kmh": 50.0,
        },
        {
            "combo_name": "d40_v45",
            "distance_to_crossroad_m": 40.0,
            "init_speed_kmh": 45.0,
        },
        {
            "combo_name": "d40_v40",
            "distance_to_crossroad_m": 40.0,
            "init_speed_kmh": 40.0,
        },
        {
            "combo_name": "d40_v35",
            "distance_to_crossroad_m": 40.0,
            "init_speed_kmh": 35.0,
        },
        {
            "combo_name": "d40_v30",
            "distance_to_crossroad_m": 40.0,
            "init_speed_kmh": 30.0,
        },

        # dis = 35.0
        {
            "combo_name": "d35_v60",
            "distance_to_crossroad_m": 35.0,
            "init_speed_kmh": 60.0,
        },
        {
            "combo_name": "d35_v55",
            "distance_to_crossroad_m": 35.0,
            "init_speed_kmh": 55.0,
        },
        {
            "combo_name": "d35_v50",
            "distance_to_crossroad_m": 35.0,
            "init_speed_kmh": 50.0,
        },
        {
            "combo_name": "d35_v45",
            "distance_to_crossroad_m": 35.0,
            "init_speed_kmh": 45.0,
        },
        {
            "combo_name": "d35_v40",
            "distance_to_crossroad_m": 35.0,
            "init_speed_kmh": 40.0,
        },
        {
            "combo_name": "d35_v35",
            "distance_to_crossroad_m": 35.0,
            "init_speed_kmh": 35.0,
        },
        {
            "combo_name": "d35_v30",
            "distance_to_crossroad_m": 35.0,
            "init_speed_kmh": 30.0,
        },

        # dis = 30.0
        {
            "combo_name": "d30_v60",
            "distance_to_crossroad_m": 30.0,
            "init_speed_kmh": 60.0,
        },
        {
            "combo_name": "d30_v55",
            "distance_to_crossroad_m": 30.0,
            "init_speed_kmh": 55.0,
        },
        {
            "combo_name": "d30_v50",
            "distance_to_crossroad_m": 30.0,
            "init_speed_kmh": 50.0,
        },
        {
            "combo_name": "d30_v45",
            "distance_to_crossroad_m": 30.0,
            "init_speed_kmh": 45.0,
        },
        {
            "combo_name": "d30_v40",
            "distance_to_crossroad_m": 30.0,
            "init_speed_kmh": 40.0,
        },
        {
            "combo_name": "d30_v35",
            "distance_to_crossroad_m": 30.0,
            "init_speed_kmh": 35.0,
        },
        {
            "combo_name": "d30_v30",
            "distance_to_crossroad_m": 30.0,
            "init_speed_kmh": 30.0,
        },

        
       
    ],
}