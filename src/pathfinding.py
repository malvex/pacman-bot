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
    Simple "flowing water" path finding algorithm.
    """
    # get array dimensions
    array_height, array_width = array.shape

    # flip xy coordinates because numpy uses height/width (= y/x)
    pacman_loc = (pacman_loc[1], pacman_loc[0])
    target_loc = (target_loc[1], target_loc[0])

    max_iter = 500

    i = 0
    explored_points = set()
    possible_paths = [[pacman_loc]]

    while i < max_iter and possible_paths:
        i += 1

        # sort paths by distance to search paths closer to the target first
        possible_paths.sort(key=lambda p: calculate_distance(p[-1], target_loc))
        path = possible_paths.pop(0)

        loc = path[-1]  # get last path point

        # calculate distance to make sure we don't "overshoot"
        if calculate_distance(loc, target_loc) < step_size:
            l.debug(f"FOUND, BUT {len(possible_paths)} PATHS LEFT TO CHECK")
            path.pop(0)  # remove point of origin (already reached point)
            path.append(target_loc)  # append target point
            # flip xy on each step again
            return [(p[1], p[0]) for p in path]

        # if the current point was already explored then we disregard it
        if loc in explored_points:
            continue

        explored_points.add(loc)

        # min() and max() are used for bounds checking
        directions = [
            (max(0, min(array_height-1, loc[0] - step_size)), loc[1]),  # go left
            (loc[0], max(0, min(array_width-1, loc[1] - step_size))),   # go up
            (max(0, min(array_height-1, loc[0] + step_size)), loc[1]),  # go right
            (loc[0], max(0, min(array_width-1, loc[1] + step_size))),   # go down
        ]

        for next_loc in directions:
            # skip if we havent moved - can happen when we reached boundary
            if next_loc == loc:
                continue

            # check if the next point is a path (1) or a wall (0)
            if array[next_loc] > 0:
                possible_paths.append(path + [next_loc])

    if i >= max_iter:
        l.warning("Maximum iterations allowance (%s) reached!", max_iter)
    else:
        l.info("Path to the target wasn't discovered yet. (made %s iterations)", i)

    return False

def generate_path_navigation(origin: tuple[int], path: list[tuple[int]]) -> list[NavigationStep]:
    """Generate navigation steps from a path"""
    if not path:
        return []

    previous_point = origin
    previous_direction = None
    steps = []

    for next_point in path:
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

        previous_point = next_point

    return steps
