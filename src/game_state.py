from helper import calculate_closest_entity, calculate_distance
from map import draw_map

from time import time

POWER_UP_DURATION = 8  # seconds


class GameState:
    def __init__(self, debug: bool = True):
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

    def update(self, predictions: list) -> None:
        current_time = time()
        self.frame += 1

        # save previous pacman position
        self.previous_pacman = self.pacman

        # todo - implement memory!

        # temp reset
        self.berries = []
        self.buffs = []
        self.ghosts = {}

        # process predictions
        for entity in predictions:
            class_name = entity["class"]

            if class_name == "pacman":
                self.pacman = entity

            elif class_name.startswith("ghost-"):
                self.ghosts[class_name] = entity

                # if we see vulnerable ghost that means power-up was taken
                if not self.powered_up and class_name == "ghost-vulnerable":
                    self.activate_power_up()

            elif class_name == "berry":
                self.berries.append(entity)

            elif class_name == "buff":
                self.buffs.append(entity)

            # if self.pacman and self.calculate_distance(self.pacman, entity) < 20:
            #     self.activate_power_up()

        # check if power-up has expired
        if self.powered_up and current_time > self.power_up_end_time:
            self.powered_up = False

        if self.debug:
            # print debug info every second
            if current_time - self.last_debug_time >= 1:
                self.print_debug_info()
                self.last_debug_time = current_time

    def activate_power_up(self):
        self.powered_up = True
        self.power_up_end_time = time() + POWER_UP_DURATION
        if self.debug:
            print(f"Power-up activated!")

    def print_debug_info(self):
        print(f"\n--- Frame {self.frame} ---")
        print(f"Pacman detected: {self.pacman is not None}")
        print(f"Ghosts detected: {len(self.ghosts)}")
        print(f"Berries detected: {len(self.berries)}")
        print(f"Buffs detected: {len(self.buffs)}")
        print(f"Powered up: {self.powered_up}")

        # calculate closest ghost
        closest_ghost = calculate_closest_entity(self.pacman, list(self.ghosts.values()))

        if self.pacman and closest_ghost:
            distance = calculate_distance(self.pacman, closest_ghost)
            print(f"Distance to closest ghost: {distance:.2f}")

        draw_map(self)
