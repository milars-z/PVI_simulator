# render/render_config.py

RENDER_CONFIG = {
    "window": {
        "title": "PVI Simulation",
        "padding_px": 40,


        "min_width_px": 1200,
        "min_height_px": 500,
    },

    # meter -> pixel
    "scale": {
        "pixel_per_meter": 20,
    },

    "color": {
        "background": (80, 80, 80),
        "lane": (130, 130, 130),
        "cross_road": (255, 255, 255),

        # pedestrian: orange
        "ped": (255, 165, 0),

        # vehicle: green
        "veh": (0, 180, 0),

        "agent_outline": (30, 30, 30),
    },

    "cross_road_mark": {
        "block_length_m": 0.2,
        "gap_length_m": 0.2,
    },
}