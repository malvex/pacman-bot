from helper import calculate_distance_better


def find_path(array, pacman_loc: tuple[int], target_loc: tuple[int], step_size: int = 1) -> list:
    """Simple "flowing water" path finding algorithm. Not the most efficient implementation."""

    max_iter = 500

    i = 0
    explored_points = []
    possible_paths = [[pacman_loc]]

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

        #print(f"[Iter {i}] Current possible_paths count list: {len(possible_paths)}")
