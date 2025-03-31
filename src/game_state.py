from helper import calculate_closest_entity, calculate_distance
from walls_mapper import WallsMapper
from models import Memory, Prediction, Entity, EntityClass, BotAction, NavigationStep
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

        self.memory = Memory()
        self.stuck = 0

    def update(self, predictions: list[Prediction]) -> None:
        current_time = time()
        self.frame += 1

        # temp reset
        self.berries = []
        self.buffs = []
        self.ghosts = {}

        vuln_ghost_i = 0
        buff_i = 0

        # process predictions
        for _prediction in predictions:
            # validate input by parsing it into Prediction (python) model (pydantic)
            prediction = Prediction.model_validate(_prediction)

            # create Entity from Prediction
            class_name = prediction.class_name
            if class_name in ["pacman", "berry"] or class_name.startswith("ghost-"):
                entity_id = class_name
            elif class_name == "vulnerable-ghost":
                vuln_ghost_i += 1  # purposely here so we name entities starting with 1
                entity_id = f"vulnerable-ghost{vuln_ghost_i}"
            elif class_name == "buff":
                buff_i += 1
                entity_id = f"buff{buff_i}"
            else:
                l.warning('Unknown class "%s", ignoring', class_name)
                continue

            entity = Entity.from_prediction(entity_id, prediction)

            # auto-discover path from pacman and ghosts - (entities that can move)
            if entity.is_alive:
                self.walls_mapper.discover_pixel_size(entity.size)
                self.walls_mapper.discover_path(entity)

            # handle pacman logic
            if entity.is_pacman:
                # save previous pacman position
                self.previous_pacman = self.pacman

                self.pacman = entity

                if self.pacman and self.previous_pacman:
                    self.check_if_stuck()

            # handle ghost logic
            elif entity.is_ghost:
                self.ghosts[entity.entity_id] = entity

                if self.previous_pacman and self.previous_pacman.distance_to(entity) < 100:
                    # if we are too close to a vulnerable ghost, clean it up from memory (was eaten)
                    if entity.entity_id in self.memory.ghosts and entity_id.startswith("vuln"):
                        self.memory.ghosts.pop(entity.entity_id)
                else:
                    self.memory.ghosts[entity.entity_id] = entity

                # if we see vulnerable ghost that means power-up was taken
                if not self.powered_up and entity.class_name == EntityClass.vulnerable_ghost:
                    self.activate_power_up()
                    self.memory.power_ups = {}  # forget all power_ups to reset it
                    self.memory.ghosts = {}

            # handle berry logic
            elif entity.class_name == EntityClass.berry:
                self.berries.append(entity)

            # handle power pill logic
            elif entity.class_name == EntityClass.buff:
                self.buffs.append(entity)
                key = (entity.x // 10, entity.y // 10)

                if key not in self.memory.power_ups:
                    self.memory.power_ups[key] = entity

            # if self.pacman and self.calculate_distance(self.pacman, entity) < 20:
            #     self.activate_power_up()

        # check if power-up has expired
        if self.powered_up and current_time > self.power_up_end_time:
            self.powered_up = False
            self.memory.ghosts = {}

    def activate_power_up(self) -> None:
        self.powered_up = True
        self.power_up_end_time = time() + POWER_UP_DURATION
        if self.debug:
            l.info(f"Power-up activated!\n")

    def check_if_stuck(self) -> int:
        """Check if pacman is stuck (not moving)."""

        dist = calculate_distance(self.pacman.xy, self.previous_pacman.xy)
        l.debug("Pacman distance travelled: %s", dist)

        # reset stuck counter to not get stuck on alternative direction
        if dist < 3 and self.stuck < 7:
            self.stuck += 1
        else:
            self.stuck = 0

        return self.stuck

    # def print_debug_info(self) -> None:
    #     print(f"\n--- Frame {self.frame} ---")
    #     print(f"Pacman detected: {self.pacman is not None}")
    #     print(f"Ghosts detected: {len(self.ghosts)}")
    #     print(f"Berries detected: {len(self.berries)}")
    #     print(f"Buffs detected: {len(self.buffs)}")
    #     print(f"Powered up: {self.powered_up}")
    #     print(f"Stuck: {self.stuck}")

    #     # calculate closest ghost
    #     closest_ghost = calculate_closest_entity(self.pacman, list(self.ghosts.values()))

    #     if self.pacman and closest_ghost:
    #         distance = calculate_distance(self.pacman.xy, closest_ghost.xy)
    #         print(f"Distance to closest ghost: {distance:.2f}")
