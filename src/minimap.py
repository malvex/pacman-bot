from models import Map, Entity, BotAction, BotActionType

import cv2
import numpy as np


COLOR = {
    "BLACK": (0, 0, 0),
    "WHITE": (255, 255, 255),
    "GREEN": (0, 255, 0),
    "RED": (0, 0, 255),
    "BLUE": (255, 0, 0),
}

cv2.namedWindow('Map', cv2.WINDOW_NORMAL)


def draw_bot_action_line(img, resolution: int, pacman: Entity, bot_action: BotAction):
    """Draw a line to the current target. Blue line is eating the target, Red line is for running away from the target."""

    # don't draw anything if there is no target
    if not pacman or not bot_action or bot_action.action_type == BotActionType.WANDER or not bot_action.target:
        return img

    # get resized coordinates
    pacman_loc = (int(pacman.x // resolution), int(pacman.y // resolution))
    target_loc = (int(bot_action.target.x // resolution), int(bot_action.target.y // resolution))

    color = "RED" if bot_action.action_type == BotActionType.RUN_AWAY else "BLUE"

    return cv2.line(img, pacman_loc, target_loc, COLOR[color], 3)


def draw_map(game_state, map: Map, entity_max_size_px: int, bot_action: BotAction):

    resolution = map.grid_resolution_px

    frame = np.zeros((map.height, map.width, 3), dtype=np.uint8)

    # set discovered paths as white
    frame[map.data == 1] = COLOR["WHITE"]

    entities = [] \
        + [game_state.pacman] \
        + (list(game_state.memory.ghosts.values())) \
        + (game_state.berries or []) \
        + (list(game_state.memory.power_ups.values()))  # type: list[Entity]

    # draw entities
    for entity in entities:
        if not entity:
            continue

        # resized coordinates
        rx = int(entity.x // resolution)
        ry = int(entity.y // resolution)

        # half size to get bounding box
        hs = int(entity_max_size_px // resolution // 2) - 10
        entity_bbox_rx = (rx - hs, rx + hs)
        entity_bbox_ry = (ry - hs, ry + hs)

        # set entity color based on its class
        color = {
            "pacman": COLOR["GREEN"],
            "ghost-red": COLOR["RED"],
            "ghost-green": COLOR["RED"],
            "ghost-orange": COLOR["RED"],
            "ghost-yellow": COLOR["RED"],
            "vulnerable-ghost": COLOR["BLUE"],
            "berry": COLOR["BLUE"],
            "buff": COLOR["BLUE"]
        }.get(entity.class_name.value)

        # draw box where entity is found
        frame[entity_bbox_ry[0]:entity_bbox_ry[1],entity_bbox_rx[0]:entity_bbox_rx[1]] = color

    # draw line to the current target
    frame = draw_bot_action_line(frame, resolution, game_state.pacman, bot_action)

    # # draw pathfinding line
    # prev_point = None
    # for point in game_state.pathfinding:
    #     if not prev_point:
    #         prev_point = point
    #         continue

    #     draw_line(frame, prev_point, point, "")

    resized_frame = cv2.resize(frame, (map.width * resolution, map.height * resolution),
                       interpolation=cv2.INTER_NEAREST)


    # render the final image
    cv2.imshow('Map', resized_frame)
    cv2.waitKey(1)

# todo: cv2.destroyAllWindows()
