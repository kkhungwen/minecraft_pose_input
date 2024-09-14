from typing import Literal
from .utils import compare_nums, in_range

default_movements_config = dict(
    # if active, keep active for this duration, all checkpoints except the last one must have this field to keep track of states; used to track movements with long duration
    DEFAULT_CHECKPOINT_ACTIVE_DURATION=300,  # ms
    JUMP_CHECKPOINT_ACTIVE_DURATION=800,  # ms

    ELBOW_CROSS_MAX_ANGLE=100,  # cross_hands
    SQUAT_KNEE_MAX_ANGLE=120,  # squat

    WALK_KNEE_MAX_ANGLE=105,  # walk
    STRAIGHT_ELBOW_MAX_ANGLE=140,  # straight arm
    UP_SHOULDERS_MAX_ANGLE=45,  # up arm


    DIRECTION_FRONT_LEFT_FOOT_ANGLE_MIN = 0,
    DIRECTION_FRONT_LEFT_FOOT_ANGLE_MAX = 80,
    DIRECTION_FRONT_RIGHT_FOOT_ANGLE_MIN = 90,
    DIRECTION_FRONT_RIGHT_FOOT_ANGLE_MAX = 150,

    DIRECTION_RIGHT_FOOT_ANGLE_MIN = 90,
    DIRECTION_RIGHT_FOOT_ANGLE_MAX = 180,
    DIRECTION_LEFT_FOOT_ANGLE_MIN = 0,
    DIRECTION_LEFT_FOOT_ANGLE_MAX = 90,

    FACE_LEFT_MIN=9,
    FACE_RIGHT_MIN=9,
    FACE_UP_MIN=13,
    FACE_DOWN_MIN=3,
)


def is_direction_left(state, face_left_foot_angle_min, face_left_foot_angle_max):
    return (
        (
        in_range(state["ANGLE2D_LEFT_FOOT"],face_left_foot_angle_min,face_left_foot_angle_max)
        )
        and
        (
        in_range(state["ANGLE2D_RIGHT_FOOT"],face_left_foot_angle_min,face_left_foot_angle_max)
        )
    )

def is_direction_right(state, face_right_foot_angle_min, face_right_foot_angle_max):
    return (
        (
        in_range(state["ANGLE2D_LEFT_FOOT"],face_right_foot_angle_min,face_right_foot_angle_max)
        )
        and
        (
        in_range(state["ANGLE2D_RIGHT_FOOT"],face_right_foot_angle_min,face_right_foot_angle_max)
        )
    )

def is_walking(state, walk_knee_max_angle: int):
    return (
        (
            compare_nums(state["ANGLE_LEFT_KNEE"], walk_knee_max_angle, "lt")
            or compare_nums(state["ANGLE_RIGHT_KNEE"], walk_knee_max_angle, "lt")
        )
        and compare_nums(
            state["LEFT_KNEE"]["pose"][1], state["LEFT_HIP"]["pose"][1], "gt"
        )
        and compare_nums(
            state["RIGHT_KNEE"]["pose"][1], state["RIGHT_HIP"]["pose"][1], "gt"
        )
    )


def is_arm_straight(
    state, side: Literal["left", "right"], straight_elbow_max_angle: int
):
    return compare_nums(
        state[f"ANGLE_{side.upper()}_ELBOW"],
        straight_elbow_max_angle,
        "gt",
    )


def is_arm_up(state, side: Literal["left", "right"], up_shoulders_max_angle: int):
    return compare_nums(
        state[f"ANGLE_{side.upper()}_SHOULDER"],
        up_shoulders_max_angle,
        "gt",
    )




class Movements:

    def __init__(self, movements_config: dict):
        self.movements_config = movements_config
        self.movements = []

    def get_current_list(self):
        if not self.movements:
            self.movements = [
                # arm movements
                {
                    "name": "jump",
                    "description": "Raise both hands up, higher than the head.",
                    "type": "click",
                    "checkpoints": [
                        {
                            "condition": lambda state: compare_nums(
                                state["LEFT_WRIST"]["pose"][1],
                                state["LEFT_SHOULDER"]["pose"][1],
                                "gt",
                            )
                            and compare_nums(
                                state["RIGHT_WRIST"]["pose"][1],
                                state["RIGHT_SHOULDER"]["pose"][1],
                                "gt",
                            ),
                            "active_duration": self.movements_config[
                                "JUMP_CHECKPOINT_ACTIVE_DURATION"
                            ],
                        },
                        {
                            
                            "condition": lambda state: compare_nums(
                                state["LEFT_WRIST"]["pose"][1],
                                state["NOSE"]["pose"][1],
                                "lt",
                            )
                            and compare_nums(
                                state["RIGHT_WRIST"]["pose"][1],
                                state["NOSE"]["pose"][1],
                                "lt",
                            )
                        },
                    ],
                },
                {
                    "name": "cross_hands",
                    "description": "Cross both hands in front of the body.",
                    "type": "click",
                    "checkpoints": [
                        {
                            "condition": lambda state: compare_nums(
                                state["LEFT_WRIST"]["pose"][0],
                                state["RIGHT_WRIST"]["pose"][0],
                                "lt",
                            )
                            and compare_nums(
                                state["ANGLE_LEFT_ELBOW"],
                                self.movements_config["ELBOW_CROSS_MAX_ANGLE"],
                                "lt",
                            )
                            and compare_nums(
                                state["ANGLE_RIGHT_ELBOW"],
                                self.movements_config["ELBOW_CROSS_MAX_ANGLE"],
                                "lt",
                            ),
                        },
                    ],
                },
                {
                    "name": "left_swing",
                    "description": "Swing the right hand from top of the head to the left side.",
                    "type": "hand_swing",

                    "checkpoints": [
                        {
                            "condition": lambda state: 
                            compare_nums(
                                state["LEFT_WRIST"]["pose"][1],
                                state["LEFT_SHOULDER"]["pose"][1],
                                "lt",
                            )
                            and 
                            compare_nums(
                                state["LEFT_WRIST"]["pose"][0],
                                state["LEFT_SHOULDER"]["pose"][0],
                                "gt",
                            )
                            and 
                            compare_nums(
                                state["RIGHT_WRIST"]["pose"][1],
                                state["RIGHT_SHOULDER"]["pose"][1],
                                "gt",
                            ),
                            "active_duration": self.movements_config[
                                "DEFAULT_CHECKPOINT_ACTIVE_DURATION"
                            ],
                        },
                        {
                            "condition": lambda state: compare_nums(
                                state["LEFT_WRIST"]["pose"][1],
                                state["LEFT_SHOULDER"]["pose"][1],
                                "gt",
                            )
                            and 
                            compare_nums(
                                state["RIGHT_WRIST"]["pose"][1],
                                state["RIGHT_SHOULDER"]["pose"][1],
                                "gt",
                            ),
                        },
                    ],
                },
                {
                    "name": "right_swing",
                    "description": "Swing the right hand from top of the head to the left side.",
                    "type": "hand_swing",

                    "checkpoints": [
                        {
                            "condition": lambda state: 
                            compare_nums(
                                state["RIGHT_WRIST"]["pose"][1],
                                state["RIGHT_SHOULDER"]["pose"][1],
                                "lt",
                            )
                            and 
                            compare_nums(
                                state["RIGHT_WRIST"]["pose"][0],
                                state["RIGHT_SHOULDER"]["pose"][0],
                                "lt",
                            )
                            and 
                            compare_nums(
                                state["LEFT_WRIST"]["pose"][1],
                                state["LEFT_SHOULDER"]["pose"][1],
                                "gt",
                            ),
                            "active_duration": self.movements_config[
                                "DEFAULT_CHECKPOINT_ACTIVE_DURATION"
                            ],
                        },
                        {
                            "condition": lambda state: compare_nums(
                                state["RIGHT_WRIST"]["pose"][1],
                                state["RIGHT_SHOULDER"]["pose"][1],
                                "gt",
                            )
                            and 
                            compare_nums(
                                state["LEFT_WRIST"]["pose"][1],
                                state["LEFT_SHOULDER"]["pose"][1],
                                "gt",
                            ),
                        },
                    ],
                },
                {
                    "name": "left_hand_right",
                    "description": "Swing the left hand from the left side to the right side.",
                    "type": "scroll",
                    "checkpoints": [
                        {
                            "condition": lambda state: compare_nums(
                                state["LEFT_WRIST"]["pose"][0],
                                state["RIGHT_SHOULDER"]["pose"][0],
                                "lt",
                            ),
                        },
                    ],
                },
                {
                    "name": "right_hand_left",
                    "description": "Swing the right hand from the right side to the left side.",
                    "type": "scroll",
                    "checkpoints": [
                        {
                            "condition": lambda state: compare_nums(
                                state["RIGHT_WRIST"]["pose"][0],
                                state["LEFT_SHOULDER"]["pose"][0],
                                "gt",
                            ),
                        },
                    ],
                },
                {
                    "name": "face_left",
                    "description": "Face your head to left",
                    "type": "face_direction",
                    "checkpoints": [
                        {
                            "condition": lambda state: compare_nums(
                                state["FACE_DIRECTION_Y"],
                                default_movements_config["FACE_LEFT_MIN"],
                                "gt",
                            ),
                        },
                    ],
                },
                {
                    "name": "face_right",
                    "description": "Face your head to right",
                    "type": "face_direction",
                    "checkpoints": [
                        {
                            "condition": lambda state: compare_nums(
                                state["FACE_DIRECTION_Y"],
                                -default_movements_config["FACE_RIGHT_MIN"],
                                "lt",
                            ),
                        },
                    ],
                },
                {
                    "name": "face_up",
                    "description": "Face your head up",
                    "type": "face_direction",
                    "checkpoints": [
                        {
                            "condition": lambda state: compare_nums(
                                state["FACE_DIRECTION_X"],
                                default_movements_config["FACE_UP_MIN"],
                                "gt",
                            ),
                        },
                    ],
                },
                {
                    "name": "face_down",
                    "description": "Face your head down",
                    "type": "face_direction",
                    "checkpoints": [
                        {
                            "condition": lambda state: compare_nums(
                                state["FACE_DIRECTION_X"],
                                -default_movements_config["FACE_DOWN_MIN"],
                                "lt",
                            ),
                        },
                    ],
                },
                # walking
                {
                    "name": "walk_left",
                    "description": "Walk with the left hand up and straight on the side.",
                    "type": "hold",
                    "checkpoints": [
                        {
                            "condition": lambda state: is_walking(
                                state, self.movements_config["WALK_KNEE_MAX_ANGLE"]
                            )
                            and is_direction_left(
                                state, 
                                self.movements_config["DIRECTION_LEFT_FOOT_ANGLE_MIN"],
                                self.movements_config["DIRECTION_LEFT_FOOT_ANGLE_MAX"],
                                )
                        },
                    ],
                },
                {
                    "name": "walk_right",
                    "description": "Walk with the right hand up and straight on the side.",
                    "type": "hold",
                    "checkpoints": [
                        {
                            "condition": lambda state: is_walking(
                                state, self.movements_config["WALK_KNEE_MAX_ANGLE"]
                            )
                            and is_direction_right(
                                state, 
                                self.movements_config["DIRECTION_RIGHT_FOOT_ANGLE_MIN"],
                                self.movements_config["DIRECTION_RIGHT_FOOT_ANGLE_MAX"],
                                )
                            
                        },
                    ],
                },
                {
                    "name": "walk_backward",
                    "description": "Walk with both hands down.",
                    "type": "hold",
                    "checkpoints": [
                        {
                            "condition": lambda state: is_walking(
                                state, self.movements_config["WALK_KNEE_MAX_ANGLE"]
                            )
                            and compare_nums(
                                state["LEFT_ANKLE"]["pose"][0],
                                state["LEFT_SHOULDER"]["pose"][0],
                                "gt",
                            )
                            and compare_nums(
                                state["RIGHT_ANKLE"]["pose"][0],
                                state["RIGHT_SHOULDER"]["pose"][0],
                                "lt",
                            )
                        },
                    ],
                },
                {
                    "name": "walk_forward",
                    "description": "Walk with both hands up and straight above the head.",
                    "type": "hold",
                    "checkpoints": [
                        {
                            "condition": lambda state: is_walking(
                                state, self.movements_config["WALK_KNEE_MAX_ANGLE"]
                            )
                        },
                    ],
                },
            ]

        return self.movements


SEPARATED_MOVEMENTS_NAMES = (
    {
        "group": (
            "left_hand_right",
            "right_hand_left",
        ),
        "duration": 1000,  # ms, ignore if the same movement is detected within 100ms
    },
    {
        "group": (
            "jump",
            "cross_hands",
        ),
        "duration": 200,  # ms, ignore if the same movement is detected within 100ms
    },
    {
        "group": (
            "left_swing",
            "right_swing",
        ),
        "duration": 200,  # ms, ignore if the same movement is detected within 100ms
    },
    {
        "group": (
            "face_left",
            "face_right",
            "face_up",
            "face_down",
        ),
    },
    {
        "group": (
            "squat",
            "walk_forward",
            "walk_left",
            "walk_right",
            "walk_backward",
        ),
    },
)


def get_separated_movements_by_name(name):
    for movements in SEPARATED_MOVEMENTS_NAMES:
        if name in movements["group"]:
            return movements
    return None




