# helper reusable functions


def calculate_distance(e1, e2):
    try:
        return ((e1["x"] - e2["x"]) ** 2 + (e1["y"] - e2["y"]) ** 2) ** 0.5
    except Exception as e:
        print(e1, e2)
        raise e


def calculate_closest_entity(pacman, entity_list: list):
    if not pacman or not entity_list:
        return None

    return min(entity_list, key=lambda entity: calculate_distance(pacman, entity), default=None)


def direction_to(pacman, target):
    """Provides rough direction from pacman to the target"""

    dx = target["x"] - pacman["x"]
    dy = target["y"] - pacman["y"]

    if abs(dx) > abs(dy):
        return "right" if dx > 0 else "left"
    else:
        return "down" if dy > 0 else "up"


def direction_away_from(pacman, target):
    dx = pacman["x"] - target["x"]
    dy = pacman["y"] - target["y"]

    if abs(dx) > abs(dy):
        return "right" if dx > 0 else "left"
    else:
        return "down" if dy > 0 else "up"
