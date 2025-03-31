from helper import calculate_distance, direction_to
from models import Map, Entity, BotAction, BotActionType, NavigationStep
import logging

l = logging.getLogger(__name__)


def get_path_actions(map: Map, pacman: Entity, bot_action: BotAction):
    if not pacman or not bot_action or bot_action == BotActionType.WANDER or not bot_action.target:
        return False

    if pacman.distance_to(bot_action.target) < 100:
        l.warning("too close to target, skipping path finding")
        return False

    l.debug("Trying to calculate path...")

    p = pacman.scaled_xy(map.grid_resolution_px)
    t = bot_action.target.scaled_xy(map.grid_resolution_px)

    #l.info(f"\nMAP_SIZE: {map.data.shape} | PACMAN: {p} | TARGET: {t}")

    return find_path(map.data, p, t, step_size=15)

def find_path(array, pacman_loc: tuple[int], target_loc: tuple[int], step_size: int = 1) -> list:
    """
    Simple "flowing water" path finding algorithm. Not the most efficient implementation.
    Could be optimized by preferring checking paths in the right direction to the target.
    """

    # flip xy coordinates because numpy uses height/width (= y/x)
    pacman_loc = (pacman_loc[1], pacman_loc[0])
    target_loc = (target_loc[1], target_loc[0])

    max_iter = 500

    i = 0
    explored_points = []
    possible_paths = [[pacman_loc]]
    shortest_path_found = False

    while i < max_iter and possible_paths:
        i += 1

        path = possible_paths.pop(0)

        loc = path[-1]  # get last path point

        # calculate distance to make sure we don't "overshoot"
        if calculate_distance(loc, target_loc) < step_size:
            l.warning(f"FOUND, BUT {len(possible_paths)} PATHS LEFT TO CHECK")
            path.pop(0)  # remove point of origin (already reached point)
            path.append(target_loc)  # append target point
            # flip xy on each step again
            return [(p[1], p[0]) for p in path]

        # if the current point was already explored then we disregard it
        if loc in explored_points:
            continue

        explored_points.append(loc)

        go_left = (max(0, loc[0] - step_size), loc[1])
        go_up = (loc[0], max(0, loc[1] - step_size))
        go_right = max(0, loc[0] + step_size), loc[1]
        go_down = (loc[0], max(0, loc[1] + step_size))

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

def generate_path_navigation(origin: list[tuple[int]], path: list[tuple[int]]):
    if not path:
        return False

    previous_point = origin
    previous_direction = None
    steps = []

    while path:
        next_point = path.pop(0)

        # get the direction to the next point
        next_direction = direction_to(previous_point, next_point)[0]

        # save next direction change only if it differs
        if next_direction != previous_direction:
            steps.append(NavigationStep(
                x=next_point[0],
                y=next_point[1],
                direction=next_direction
            ))
            previous_direction = next_direction

    return steps
