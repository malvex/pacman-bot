"""
WallsMapper

This component maps the environment based on Pacman getting stuck against the wall
and watching path that ghosts take.
I could just OCR walls, but this seems like a fun idea to implement.
"""
from helper import calculate_distance
from models import Map

from logging import getLogger

l = getLogger(__name__)


class WallsMapper:
    def __init__(self):
        self.map = Map()

        self.recent_location = {}
        self.entity_max_size_px = 0


        self.min_distance_px = self.map.grid_resolution_px

    def discover_pixel_size(self, width: float, height: float) -> None:
        """determine the path size in pixels based on entity size"""

        changed = False

        if width > self.entity_max_size_px:
            self.entity_max_size_px = width
            changed = True

        if height > self.entity_max_size_px:
            self.entity_max_size_px = height
            changed = True

        # re-render path if we have change in size
        if changed:
            l.info("Entity Max pixel size increased to %s", self.entity_max_size_px)
            pass

    def discover_path(self, entity_id: str, x: float, y: float):
        """Entities exploring the map will reveal the available paths"""

        # if entity_id != "pacman":
        #     return

        if self.entity_max_size_px <= 0:
            return

        loc = {"x": x, "y": y}  # temporary

        # store point only if entity moved more than min_distance_px (5px) to prevent storing too often
        if entity_id not in self.recent_location or calculate_distance(self.recent_location[entity_id], loc) > self.min_distance_px:
            self.recent_location[entity_id] = loc

            grid_resolution_px = self.map.grid_resolution_px

            # resized coordinates
            rx = int(x // grid_resolution_px)
            ry = int(y // grid_resolution_px)

            # half size to get bounding box
            hs = int(self.entity_max_size_px // grid_resolution_px // 2)
            entity_bbox_rx = (rx - hs, rx + hs)
            entity_bbox_ry = (ry - hs, ry + hs)

            self.map.data[entity_bbox_ry[0]:entity_bbox_ry[1],entity_bbox_rx[0]:entity_bbox_rx[1]] = 1
            #l.info("Discovered path point (%s, %s) by %s - in pixels: (%s, %s)", rx, ry, entity_id, x, y)
