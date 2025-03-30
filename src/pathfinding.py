from helper import calculate_distance_better
from models import Map, Entity, BotAction, BotActionType
import logging

l = logging.getLogger(__name__)


def get_path_actions(map: Map, pacman: Entity, bot_action: BotAction):
    if not pacman or not bot_action or bot_action == BotActionType.WANDER or not bot_action.target:
        return False

    l.debug("Trying to calculate path...")

    p = pacman.scaled_xy(map.grid_resolution_px)
    t = bot_action.target.scaled_xy(map.grid_resolution_px)

    return find_path(map.data, p, t, step_size=25)

def find_path(array, pacman_loc: tuple[int], target_loc: tuple[int], step_size: int = 1) -> list:
    """Simple "flowing water" path finding algorithm. Not the most efficient implementation."""

    max_iter = 5000

    i = 0
    explored_points = []
    possible_paths = [[pacman_loc]]

    print(possible_paths)

    while i < max_iter and possible_paths:
        i += 1

        path = possible_paths.pop()

        loc = path[-1]  # get last path point

        # to make sure we don't "overshoot"
        if calculate_distance_better(loc, target_loc) < step_size:
            return path

        # if the current point was already explored then we disregard it
        if loc in explored_points:
            continue

        explored_points.append(loc)

        go_left = (max(0, loc[1] - step_size), loc[0])
        go_up = (loc[1], max(0, loc[0] - step_size))
        go_right = max(0, loc[1] + step_size), loc[0]
        go_down = (loc[1], max(0, loc[0] + step_size))

        if array[go_left] > 0:
            # print(f"CAN GO LEFT, NEXT POINT IS {go_left}")
            possible_paths.append(path + [go_left])

        if array[go_up] > 0:
            # print(f"CAN GO UP, NEXT POINT IS {go_up}")
            possible_paths.append(path + [go_up])

        if array[go_right] > 0:
            # print(f"CAN GO RIGHT, NEXT POINT IS {go_right}")
            possible_paths.append(path + [go_right])

        if array[go_down] > 0:
            # print(f"CAN GO DOWN, NEXT POINT IS {go_down}")
            possible_paths.append(path + [go_down])

    if i >= max_iter:
        l.warning("Maximum iterations allowance (%s) reached!", max_iter)
    else:
        l.info("Path to the target wasn't discovered yet. (made %s iterations)", i)

    return False
