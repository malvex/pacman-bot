from my_keyboard import press_key
from helper import calculate_closest_entity, direction_to
from models import BotAction, BotActionType, Entity, EntityClass, NavigationStep
from pathfinding import get_path_actions, generate_path_navigation
from game_state import GameState

from time import time
from logging import getLogger

l = getLogger(__name__)


class Bot:
    def __init__(self, enable_navigation: bool = True):
        self.enable_navigation = enable_navigation

        # data for bot operation
        self.current_action: BotAction = None
        self.current_navigation: list[NavigationStep] = []
        self.last_decision_time: float = 0.0

        # bot actions
        self.last_pressed_key = None
        self.last_move_time = 0
        self.move_cooldown = 0.1  # seconds between key changes
        self.last_pathfinding_time: float = 0.0

    def iterate(self, game_state: GameState) -> None:
        """
        Evaluate current game state and decide action based on that.
        Todo: This should be split to smaller parts.
        """

        # if we dont see pacman then dont do anything (e.g. dead pacman, game in menu, or not loaded)
        if not game_state.pacman:
            return

        # check cooldown to prevent changing mind too often
        current_time = time()

        # if current_time > self.next_action_time:
        #     self.next_action_time = current_time + 0.1

        if current_time - self.last_move_time < self.move_cooldown:
            return

        next_best_action = self.choose_best_action(game_state)

        # reset navigation if we changed our objective
        if self.current_action and self.current_action.action_type != next_best_action.action_type:
            l.info("Objective changed, reseting navigation")
            self.current_navigation = []

        self.current_action = next_best_action

        l.info(f"next_best_action: {next_best_action.action_type}")
        reason = ""

        # pathfinding navigation
        if self.current_navigation:
            # if we should be running away then interrupt navigation
            if self.current_action.action_type == BotActionType.RUN_AWAY:
                l.info("Getting chased, resetting navigation")
                self.current_navigation = []  # interrupt navigation
                reason = " getting chased (navigation interrupted)"
                return self.execute_action(self.current_action.action_key[0], reason)

            # if stuck during navigating, then reset navigation (temp, before bugs resolved)
            if game_state.stuck >= 5:
                l.warning("Stuck during navigation, resetting navigation steps")
                self.current_navigation = []
                reason = " stuck during navigation (navigation reset)"
                return self.execute_action(self.current_action.action_key[0], reason)

            __endless_loop_protection = 0
            while self.current_navigation and __endless_loop_protection < 20:
                __endless_loop_protection += 1
                next_point = self.current_navigation[0].model_copy()
                next_point.x = int(next_point.x * 2)
                next_point.y = int(next_point.y * 2)

                if game_state.pacman.distance_to(next_point) < 150:
                    l.info(f"point ({str(next_point)}) reached! pacman = {game_state.pacman.xy}")
                    self.current_navigation.pop(0)
                    continue
                else:
                    reason = f"{self.current_action.action_type.name} (navigating)"
                    return self.execute_action(next_point.direction, reason)

        if self.current_action.action_type != BotActionType.RUN_AWAY \
            and self.enable_navigation \
            and current_time > self.last_pathfinding_time + 1.0 \
            and self.current_action.target \
            and game_state.pacman.distance_to(self.current_action.target) > 250:
            # no navigation yet, lets try pathfinding, but only if we arent chased

            # pathfinding cooldown to reduce system load
            self.last_pathfinding_time = current_time

            found_path = get_path_actions(game_state.walls_mapper.map, game_state.pacman, self.current_action)

            if found_path:
                l.info(f"Found path to {self.current_action.target.class_name}!")

                pxy = game_state.pacman.scaled_xy(game_state.walls_mapper.map.grid_resolution_px)
                self.current_navigation = generate_path_navigation(pxy, found_path)
                l.info(f"Navigation: {[str(s) for s in self.current_navigation]}")

                reason = f"{self.current_action.action_type.name} (new navigation)"
                return self.execute_action(self.current_navigation[0].direction, reason)

        primary, secondary, tertiary = self.current_action.action_key

        if game_state.stuck < 2:
            action = primary
        elif game_state.stuck < 5:
            action = secondary
        else:
            action = tertiary

        reason = f"{self.current_action.action_type.name}[{game_state.stuck}]"
        return self.execute_action(action, reason)


    def choose_best_action(self, game_state: GameState) -> BotAction:
        """decide the best action to take"""

        pacman = game_state.pacman
        closest_ghost = calculate_closest_entity(pacman, list(game_state.memory.ghosts.values()))

        # powered up - chase ghosts - but only if we have at least 3s left on the powerup timer
        if game_state.powered_up and (game_state.power_up_end_time - time()) > 3:
            if closest_ghost:
                return self.eat(pacman, closest_ghost)

        # avoid nearby ghosts
        if closest_ghost and pacman.distance_to(closest_ghost) < 200:
            return self.run_away_from(pacman, closest_ghost)

        # go for berry
        closest_berry = calculate_closest_entity(pacman, game_state.berries)
        if closest_berry:
            return self.eat(pacman, closest_berry)

        # go for power-up buff
        closest_powerup = calculate_closest_entity(pacman, list(game_state.memory.power_ups.values()))
        if closest_powerup:
            return self.eat(pacman, closest_powerup)

        # default action
        return self.wander()

    def execute_action(self, action: str, reason: str = None) -> None:
        # execute the action

        if action != self.last_pressed_key or True:  # todo - temp bypass

            self.last_pressed_key = action
            self.last_move_time = time()

            reason_s = "" if not reason else f" - reason: {reason}"
            print(f"pressed {action}{reason_s}")
            press_key(action)

    ###########
    # helper functions to simplify the code
    ###########

    @staticmethod
    def run_away_from(pacman: Entity, target: Entity):
        """Helper function that sets up run away bot action"""
        return BotAction(
            target=target,
            action_key=pacman.direction_away_from(target),
            action_type=BotActionType.RUN_AWAY
        )

    @staticmethod
    def eat(pacman: Entity, target: Entity):
        """Helper function that sets up eat bot action"""

        if target.is_ghost:
            action_type = BotActionType.EAT_GHOST
        elif target.class_name == EntityClass.buff:
            action_type = BotActionType.EAT_POWERUP
        elif target.class_name == EntityClass.berry:
            action_type = BotActionType.EAT_BERRY
        else:
            l.warning("Undefined eat handler for %s", target.class_name)
            action_type = None

        return BotAction(
            target=target,
            action_key=pacman.direction_to(target),
            action_type=action_type
        )

    @staticmethod
    def wander():
        """Helper function that sets up default wandering action (no clear goal defined)"""
        return BotAction(
            action_type=BotActionType.WANDER,
            target=None,
            action_key=("left", "up", "down")  # default directions
        )
