from interaction.PVI_controller import JerkAction

JERK_ACTION_LIST = [
    JerkAction(
        action_id=0,
        name="keep",
        jerk=0.0,
    ),
    JerkAction(
        action_id=1,
        name="comfort",
        jerk=0.45,
    ),
    JerkAction(
        action_id=2,
        name="accept",
        jerk=0.8,
    ),
    JerkAction(
        action_id=3,
        name="normal",
        jerk=1.5,
    ),
    JerkAction(
        action_id=4,
        name="hard",
        jerk=2.0,
    ),
    JerkAction(
        action_id=5,
        name="emergency",
        jerk=2.5,
    ),
]
