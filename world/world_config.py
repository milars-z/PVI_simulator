# world/world_config.py

from agents.agent_enums import Orientation


WORLD_CONFIG = {
    "name": "simple_pvi_world",

    # 车道设计
    # 
    "lane": [
        {
            "id": 0,
            "bottom_x": 0.0, # 车道的左下角坐标_x,对单车道情况一般设计为(0，0) (实际为坐上标系原点)
            "bottom_y": 0.0, # 车道的左下角坐标_x,对单车道情况一般设计为(0，0) (实际为坐上标系原点)
            "width": 4.0, # 车道宽度
            "length": 80.0, # 车道长度
            "direction": Orientation.RIGHT, # 车道行驶方向，咱用作标记或者后期图像渲染
        }
    ],

    # Pedestrian road / sidewalk area.
    # 行人通行或等待的区域。
    "cross_road": [
        {
            "id": 0,
            "bottom_x": 60.0, #人行道的左下角坐标_x, (实际为坐上标系原点)
            "bottom_y": 0.0, #人行道的左下角坐标_y, (实际为坐上标系原点)
            "width": 2.0, #人行道宽度
            "direction": Orientation.UP, #人行道行驶方向，咱用作标记或者后期图像渲染
        }
    ],

    # 行人生成相关信息
    # 每一张地图配置一个行人生成的参考点，后续可以改为dict
    "ped_spawn": {
        "cross_road_id": 0, # 行人生成的道路id
        "bias_x": 1.0, # 行人生成推荐点位x，相较于道路bottom的偏置值，一般设计为1/2的道路宽度
        "bias_y": 7.0, # 行人生成推荐点位y，相较于道路bottom的偏置值，代表行人从6m - 4m(道路宽度)外的地方生成
        "random_radius": 0.0, # 行人随机生成设计，暂时将行人生成点设计为固定点
        "orientation": Orientation.UP, #行人行走方向
    },

    # 车辆生成相关信息
    # 每一张地图配置一个车辆生成的参考点，后续可以改为dict
    "veh_spawn": {
        "lane_id": 0, # 车道id
        "cross_road_id": 0, # 车道绑定的行人道，获取人行道的相关坐标
        "x_bias": 10.0, # 车辆生成推荐点位x，这里记录的是人行道的最左侧，车辆最终生成的位置需要加以处理
        "y_bias": 2.0, # 车辆生成推荐点位y，一般为1/2车道宽度
        "orientation": Orientation.RIGHT, # 车辆行驶方向
    },
}