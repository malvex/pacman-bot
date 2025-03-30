from models import Map

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


def draw_map(game_state, map: Map, entity_max_size_px: int):

    resolution = map.grid_resolution_px

    frame = np.zeros((map.height, map.width, 3), dtype=np.uint8)

    # set discovered paths as white
    frame[map.data == 1] = COLOR["WHITE"]

    entities = [] \
        + [game_state.pacman] \
        + (list(game_state.ghosts.values())) \
        + (game_state.berries or []) \
        + (game_state.buffs or [])

    # draw entities
    for entity in entities:
        if not entity:
            continue

        # resized coordinates
        rx = int(entity["x"] // resolution)
        ry = int(entity["y"] // resolution)

        # half size to get bounding box
        hs = int(entity_max_size_px // resolution // 2)
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
        }.get(entity["class"])

        # draw box where entity is found
        frame[entity_bbox_ry[0]:entity_bbox_ry[1],entity_bbox_rx[0]:entity_bbox_rx[1]] = color

    resized_frame = cv2.resize(frame, (map.width * resolution, map.height * resolution),
                       interpolation=cv2.INTER_NEAREST)

    # render the final image
    cv2.imshow('Map', resized_frame)
    cv2.waitKey(1)

# todo: cv2.destroyAllWindows()
