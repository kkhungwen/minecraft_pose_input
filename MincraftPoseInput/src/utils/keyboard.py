from pynput.keyboard import Key
from pynput.mouse import Button

keyboard_mappings = (
    (Key.space, "space"),
    (Key.shift, "shift"),
    (Key.ctrl, "ctrl"),
    (Key.tab, "tab"),
    (Key.enter, "enter"),
    (Key.esc, "esc"),
    (Key.up, "up"),
    (Key.down, "down"),
    (Key.left, "left"),
    (Key.right, "right"),
)

keyboard_special_key_names = [v for k, v in keyboard_mappings]


def keyboard_to_str(key):
    for k, v in keyboard_mappings:
        if key == k:
            return v
    return str(key)


def str_to_keyboard(value):
    for k, v in keyboard_mappings:
        if value == v:
            return k
    return value

mouse_button_mappings = (
    (Button.left, "left"),
    (Button.right, "right"),
    (Button.middle, "middle"),
    (Button.x1, "x1"),
    (Button.x2, "x2"),
)

mouse_button_names = [v for k, v in mouse_button_mappings]

def mouse_button_to_str(button):
    for k, v in mouse_button_mappings:
        if button == k:
            return v
    return str(button)

def str_to_mouse_button(value):
    for k, v in mouse_button_mappings:
        if value == v:
            return k
    return value
