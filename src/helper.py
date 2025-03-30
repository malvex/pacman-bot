# helper reusable functions


# def calculate_distance(e1, e2) -> float:
#     try:
#         return ((e1["x"] - e2["x"]) ** 2 + (e1["y"] - e2["y"]) ** 2) ** 0.5
#     except Exception as e:
#         print(e1, e2)
#         raise e

def calculate_distance_better(x: tuple, y: tuple) -> float:
    return ((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2) ** 0.5


def calculate_closest_entity(pacman, entity_list: list):
    if not pacman or not entity_list:
        return None

    return min(entity_list, key=lambda entity: calculate_distance_better(pacman.xy, entity.xy), default=None)


def direction_to(pacman: tuple, target: tuple) -> tuple[str]:
    """Provides rough direction from pacman to the target"""

    dx = target[0] - pacman[0]
    dy = target[1] - pacman[1]

    if abs(dx) > abs(dy):
        primary = "right" if dx > 0 else "left"
        secondary = "down" if dy > 0 else "up"
        tertiary = "up" if dy > 0 else "down"
    else:
        primary = "down" if dy > 0 else "up"
        secondary = "right" if dx > 0 else "left"
        tertiary = "left" if dx > 0 else "right"

    return primary, secondary, tertiary


# def direction_away_from(pacman, target):
#     dx = pacman["x"] - target["x"]
#     dy = pacman["y"] - target["y"]

#     if abs(dx) > abs(dy):
#         primary = "right" if dx > 0 else "left"
#         secondary = "down" if dy > 0 else "up"
#         tertiary = "up" if dy > 0 else "down"
#     else:
#         primary = "down" if dy > 0 else "up"
#         secondary = "right" if dx > 0 else "left"
#         tertiary = "left" if dx > 0 else "right"

#     return primary, secondary, tertiary
