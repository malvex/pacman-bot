from helper import calculate_closest_entity, calculate_distance
from walls_mapper import WallsMapper
from models import Memory
from minimap import draw_map

from time import time
from logging import getLogger

l = getLogger(__name__)

POWER_UP_DURATION = 7  # seconds


class GameState:
    def __init__(self, walls_mapper: WallsMapper, debug: bool = True):
        self.walls_mapper = walls_mapper

        # game entities
        self.pacman = None
        self.previous_pacman = None
        self.ghosts = {}
        self.berries = []
        self.buffs = []

        # power-up
        self.powered_up = False
        self.power_up_end_time = 0

        # debugging
        self.debug = debug
        self.frame = 0
        self.last_debug_time = time()
        self.bot_action = "-"
        self.bot_move = "-"

        self.memory = Memory()
        self.stuck = 0

    def update(self, predictions: list) -> None:
        current_time = time()
        self.frame += 1

        # todo - implement memory!

        # temp reset
        self.berries = []
        self.buffs = []
        self.ghosts = {}

        # process predictions
        for entity in predictions:
            class_name = entity["class"]

            if class_name == "pacman" or class_name.startswith("ghost-"):
                self.walls_mapper.discover_pixel_size(entity["width"], entity["height"])
                self.walls_mapper.discover_path(class_name, entity["x"], entity["y"])

            if class_name == "pacman":
                # save previous pacman position
                self.previous_pacman = self.pacman

                self.pacman = entity

                if self.pacman and self.previous_pacman:
                    self.check_if_stuck()

            elif class_name.startswith("ghost-") or class_name == "vulnerable-ghost":
                self.ghosts[class_name] = entity

                self.memory.ghosts[class_name] = entity

                # if we see vulnerable ghost that means power-up was taken
                if not self.powered_up and class_name == "vulnerable-ghost":
                    self.activate_power_up()
                    self.memory.power_ups = {}  # forget all power_ups to reset it
                    self.memory.ghosts = {}

            elif class_name == "berry":
                self.berries.append(entity)

            elif class_name == "buff":
                self.buffs.append(entity)
                key = (entity["x"] // 10, entity["y"] // 10)
                if key not in self.memory.power_ups:
                    self.memory.power_ups[key] = entity

            # if self.pacman and self.calculate_distance(self.pacman, entity) < 20:
            #     self.activate_power_up()

        # check if power-up has expired
        if self.powered_up and current_time > self.power_up_end_time:
            self.powered_up = False

        draw_map(self, self.walls_mapper.map, self.walls_mapper.entity_max_size_px)

        power_timer = f" Power up! ({ self.power_up_end_time - time():.2f})" if self.powered_up else ""

        print(f"P/G/P/B: {self.pacman is not None}/{len(self.ghosts)}/{len(self.buffs)}/{len(self.berries)}"
            + f" | Stuck: {self.stuck} | {self.bot_action} ({self.bot_move}) {power_timer}"
            + " " * 20, end="\r")

        if self.debug and False:
            # print debug info every second
            if current_time - self.last_debug_time >= 1:
                self.print_debug_info()
                self.last_debug_time = current_time

    def activate_power_up(self):
        self.powered_up = True
        self.power_up_end_time = time() + POWER_UP_DURATION
        if self.debug:
            print(f"Power-up activated!\n")

    def check_if_stuck(self):
        """Check if pacman is stuck (not moving)."""

        dist = calculate_distance(self.pacman, self.previous_pacman)
        l.info("Pacman distance travelled: %s", dist)
        if dist < 3:
            self.stuck += 1
        else:
            self.stuck = 0

        return self.stuck

    def print_debug_info(self):
        print(f"\n--- Frame {self.frame} ---")
        print(f"Pacman detected: {self.pacman is not None}")
        print(f"Ghosts detected: {len(self.ghosts)}")
        print(f"Berries detected: {len(self.berries)}")
        print(f"Buffs detected: {len(self.buffs)}")
        print(f"Powered up: {self.powered_up}")
        print(f"Stuck: {self.stuck}")

        # calculate closest ghost
        closest_ghost = calculate_closest_entity(self.pacman, list(self.ghosts.values()))

        if self.pacman and closest_ghost:
            distance = calculate_distance(self.pacman, closest_ghost)
            print(f"Distance to closest ghost: {distance:.2f}")
