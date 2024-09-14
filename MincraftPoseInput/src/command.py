from datetime import datetime
from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController
from threading import Timer
from .utils.keyboard import str_to_keyboard, str_to_mouse_button


class CommandProcessor:
    def __init__(self, mouse_thread):
        self.keyboard = KeyboardController()
        self.mouse = MouseController()
        self.commands = []
        self.pressing_key = None
        self.pressing_timer = None
        self.mouse_thread = mouse_thread

    def release_previous_key(self):
        if self.pressing_key:
            previous_key = self.pressing_key.get("key", None)
            if previous_key:
                print(f"releasing {previous_key}")
                self.keyboard.release(previous_key)

            previous_key_modifier = self.pressing_key.get("modifier", None)
            if previous_key_modifier:
                print(f"releasing {previous_key_modifier}")
                self.keyboard.release(previous_key_modifier)

            previous_mouse_button = self.pressing_key.get("mouse_button", None)
            if previous_mouse_button:
                print(f"releasing {previous_mouse_button}")
                self.mouse.release(previous_mouse_button)
            
            previous_mouse_move = self.pressing_key.get("mouse_move", None)
            if previous_mouse_move:
                print(f"releasing {previous_mouse_move}")
                self.mouse_thread.set_direction(0,0)

            self.pressing_key = None

    # Clear log commands
    def limit_commands(self):
        if len(self.commands) > 900:
            self.commands = self.commands[-10:]

    def add_command(
        self,
        command_name: str,
        keyboard_enabled: bool,
        command_key_mappings: dict,
        pressing_timer_interval: float,
    ):
        self.limit_commands()

        now = datetime.now()
        self.commands.insert(0, dict(command=command_name, time=now))

        if keyboard_enabled:
            if command_name in command_key_mappings:
                command_config = command_key_mappings[command_name]
                key = command_config.get("key", None)
                modifier = str_to_keyboard(command_config.get("modifier", None))
                mouse_button = str_to_mouse_button(command_config.get("mouse_button", None))
                mouse_move = command_config.get("mouse_move",None)
                mouse_scroll = command_config.get("mouse_scroll",None)
                
                if not key and not modifier and not mouse_button and not mouse_move and not mouse_scroll:
                    return

                # get current pressing key
                previous_key = None
                previous_key_modifier = None
                previous_mouse_button = None
                previous_mouse_move = None
                if self.pressing_key:
                    previous_key = self.pressing_key.get("key", None)
                    previous_key_modifier = self.pressing_key.get("modifier", None)
                    previous_mouse_button = self.pressing_key.get("mouse_button", None)
                    previous_mouse_move = self.pressing_key.get("mouse_move", None)
                
                
                # mouse scroll wont hold 
                if mouse_scroll:
                    self.mouse.scroll(0,mouse_scroll)
                
                    
                # clear old timer
                if self.pressing_timer and self.pressing_timer.is_alive():
                    # print("cancel timer")
                    self.pressing_timer.cancel()

                # new action
                if previous_key != key or previous_key_modifier != modifier or previous_mouse_button != mouse_button or previous_mouse_move != mouse_move:
                    print(previous_mouse_button ,"and",mouse_button,"not the same")
                    self.release_previous_key()
                    if key:
                        print("pressing", key, type(key))
                        self.keyboard.press(key)
                    if modifier:
                        print("pressing", modifier, type(modifier))
                        self.keyboard.press(modifier)
                    if mouse_button:
                        print("pressing", mouse_button, type(mouse_button))
                        self.mouse.press(mouse_button)
                    if mouse_move:
                        print("pressing", mouse_move, type(mouse_move))
                        self.mouse_thread.set_direction(mouse_move[0],mouse_move[1])


                if key or modifier or mouse_button or mouse_move:
                    # create new timer
                    self.pressing_timer = Timer(
                        pressing_timer_interval,
                        self.release_previous_key,
                    )
                    self.pressing_timer.start()

                    self.pressing_key = dict(key=key, modifier=modifier, mouse_button=mouse_button, mouse_move=mouse_move, time=now)

    def __str__(self):
        commands_list = list(map(lambda c: c["command"], self.commands))
        if not commands_list:
            return ""
        return commands_list[0] + "\n" + " | ".join(commands_list[1:10])
