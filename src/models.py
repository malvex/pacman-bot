import numpy as np


class Map:
    def __init__(self, width: int = 2000, height: int = 1200, grid_resolution_px: int = 2):
        self.width = width // grid_resolution_px
        self.height = height // grid_resolution_px
        self.grid_resolution_px = grid_resolution_px

        # Initialize 2D grid for discovered paths
        self.data = np.zeros((self.height, self.width), dtype=np.uint8)

class Memory:
    power_ups = {}
    ghosts = {}

    # @property
    # def ghosts(self):
    #     ghosts = [self.ghost_red, self.ghost_yellow, self.ghost_green, self.ghost_orange]
    #     return [g for g in ghosts if g is not None]