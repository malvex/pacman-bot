import keyboard
import os


def press_key(key: str):
    if key not in ["space", "up", "down", "left", "right"]:
        raise Exception(f"input {key} not allowed")

    # pacman goes to direction of the press, so we dont need to hold it
    keyboard.press(key)
    keyboard.release(key)


def press_key_mac(key: str):
    """keyboard library doesn't work on MacOS :("""

    if key not in ["space", "up", "down", "left", "right"]:
        raise Exception(f"input {key} not allowed")

    key_code = {
        "space": 49,
        "up": 126,
        "down": 125,
        "left": 123,
        "right": 124,
    }.get(key)

    os.system(f"osascript -e 'tell application \"System Events\" to key code {int(key_code)}'")
