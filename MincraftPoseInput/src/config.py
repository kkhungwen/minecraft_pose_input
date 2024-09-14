import mediapipe as mp
import json
import os

window_title = "MotionMap"
window_icon_path = "src/assets/icon.png"
# Window dimensions: x, y, width, height
window_geometry = (100, 100, 660, 680)

IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480

auto_start_camera = False

# Config for mediapipe pose solution
default_mp_config = dict(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    model_complexity=2,  # 0: Lite 1: Full 2: Heavy
    enable_segmentation=False,
)

# Config for body processor
default_body_config = dict(
    draw_angles=True,  # Show calculated angles on camera
)

default_pressing_timer_interval = dict(
    click=0.3,  # key pressed interval
    hold=1.0,  # key pressed interval for walking commands
    hand_swing = 0.8,
    face_direction = 0.2,
    scroll = 0,
)

default_controls_list = dict(
    command_key_mappings=dict(
        jump={
            "modifier": "space",
        },
        cross_hands={
            "key": "e",
        },
        left_swing={
            "mouse_button": "right",
        },
        right_swing={
            "mouse_button": "left",
        },
        left_hand_right={
            "mouse_scroll": -1,
        },
        right_hand_left={
            "mouse_scroll": 1,
        },
        walk_forward={
            "key": "w",
        },
        walk_left={
            "key": "a",
        },
        walk_right={
            "key": "d",
        },
        walk_backward={
            "key": "s",
        },
        face_left={
            "mouse_move": (-1,0)
        },
        face_right={
            "mouse_move": (1,0)
        },
        face_up={
            "mouse_move": (0,-1)
        },
        face_down={
            "mouse_move": (0,1)
        }

    ),
    pressing_timer_interval=default_pressing_timer_interval,
)


default_events_config = dict(
    keyboard_enabled=True,  # toggle keyboard events
    command_key_mappings=default_controls_list["command_key_mappings"],
    pressing_timer_interval=default_pressing_timer_interval,
)


class AppConfig:

    def __init__(self):
        self.mp_config = default_mp_config
        self.body_config = default_body_config
        self.events_config = default_events_config
        self.controls_list = default_controls_list

    def get_config_fields(self):
        fields = [
            dict(
                name="Enable keyboard events",
                key="keyboard_enabled",
                type="events",
                input="checkbox",
            ),
            dict(
                name="Show body angles",
                key="draw_angles",
                type="body",
                input="checkbox",
                description="Show calculated angles on camera",
            ),
            dict(
                name="Advanced settings (require restart the camera to apply, hover for more info)",
                input="label",
            ),
            dict(
                name="Show segmentation mask (blur background)",
                key="enable_segmentation",
                type="mp",
                input="checkbox",
                description="Whether showing a segmentation mask for the detected pose.",
            ),
            dict(
                name="Min detection confidence",
                key="min_detection_confidence",
                type="mp",
                input="slider_percentage",
                min=0,
                max=100,
                value=self.mp_config["min_detection_confidence"] * 100,
                description="The minimum confidence score for the pose detection to be considered successful.",
            ),
            dict(
                name="Min detection confidence",
                key="min_tracking_confidence",
                type="mp",
                input="slider_percentage",
                min=0,
                max=100,
                value=self.mp_config["min_tracking_confidence"] * 100,
                description="The minimum confidence score for the pose tracking to be considered successful.	",
            ),
            dict(
                name="Mediapipe Model complexity",
                key="model_complexity",
                type="mp",
                input="slider",
                min=0,
                max=2,
                value=self.mp_config["model_complexity"],
                description="The model complexity to be used for pose detection: 0: Lite 1: Full 2: Heavy",
            ),
        ]
        return fields
