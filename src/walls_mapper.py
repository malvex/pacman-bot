"""
WallsMapper

This component maps the environment based on Pacman getting stuck against the wall
and watching path that ghosts take.
I could just OCR walls, but this seems like a fun idea to implement.
"""
from helper import calculate_distance_better
from models import Map, Entity

from logging import getLogger

l = getLogger(__name__)


class WallsMapper:
    def __init__(self):
        self.map = Map()

        self.recent_location = {}
        #self.entity_max_size_px = 0
        self.entity_max_size_px = 75  # temp

        self.bounding_box_tolerance_px = 5

        self.min_distance_px = self.map.grid_resolution_px

    def discover_pixel_size(self, size: int) -> None:
        """determine the path size in pixels based on entity size"""
        return  # temp

        if size > self.entity_max_size_px:
            self.entity_max_size_px = size
            l.info("Entity Max pixel size increased to %s", self.entity_max_size_px)

    def discover_path(self, entity: Entity) -> None:
        """Entities exploring the map will reveal the available paths"""

        # if entity_id != "pacman":
        #     return

        if self.entity_max_size_px <= 0:
            return

        recent_loc = self.recent_location.get(entity.entity_id, None)

        # store point only if entity moved more than min_distance_px (5px) to prevent storing too often
        if not recent_loc or calculate_distance_better(entity.xy, recent_loc) > self.min_distance_px:
            self.recent_location[entity.entity_id] = entity.xy

            grid_resolution_px = self.map.grid_resolution_px

            # resized coordinates
            rx = int(entity.x // grid_resolution_px)
            ry = int(entity.y // grid_resolution_px)

            # half size to get bounding box
            hs = int(self.entity_max_size_px // grid_resolution_px // 2) - self.bounding_box_tolerance_px
            entity_bbox_rx = (rx - hs, rx + hs)
            entity_bbox_ry = (ry - hs, ry + hs)

            # value 1 means there is a path
            self.map.data[entity_bbox_ry[0]:entity_bbox_ry[1],entity_bbox_rx[0]:entity_bbox_rx[1]] = 1
            #l.info("Discovered path point (%s, %s) by %s - in pixels: (%s, %s)", rx, ry, entity_id, x, y)
