from my_keyboard import press_key
from helper import calculate_closest_entity, direction_to
from models import BotAction, BotActionType, Entity, EntityClass, NavigationStep
from pathfinding import get_path_actions, generate_path_navigation
from game_state import GameState

from time import time
from logging import getLogger

l = getLogger(__name__)


class Bot:
    def __init__(self, game_state: GameState, debug: bool = True):
        # game components
        self.game_state = game_state
        self.debug = debug

        # bot actions
        self.last_key = None
        self.last_move_time = 0
        self.move_cooldown = 0.1  # seconds between key changes

        self.current_action: BotAction = None
        self.current_navigation: list[NavigationStep] = []
        self.next_action_time: float = 0.0

    def iterate(self) -> None:
        game_state = self.game_state

        # if we dont see pacman then dont do anything (e.g. dead pacman, game in menu, or not loaded)
        if not game_state.pacman:
            return

        # check cooldown to prevent changing mind too often
        current_time = time()

        # if current_time > self.next_action_time:
        #     self.next_action_time = current_time + 0.1

        if current_time - self.last_move_time < self.move_cooldown:
            return

        # todo - state machine

        game_state.bot_action = self.choose_best_action(game_state)

        # if we should run away then interrupt everything we are doing
        if game_state.bot_action.action_type != BotActionType.RUN_AWAY:
            # we have currently set navigation
            while self.current_navigation:
                next_point = self.current_navigation[0].model_copy()
                next_point.x = int(next_point.x * 2)
                next_point.y = int(next_point.y * 2)

                l.info(f"pacman = {game_state.pacman.xy} next_point = {next_point.xy}")
                if game_state.pacman.distance_to(next_point) < 250:
                    l.info(f"point ({str(next_point)}) reached! pacman = {game_state.pacman.xy}")
                    self.current_navigation.pop(0)
                    continue
                else:
                    return self.execute_action((next_point.direction,)*3)

        self.current_navigation = []

        found_path = get_path_actions(game_state.walls_mapper.map, game_state.pacman, game_state.bot_action)

        if found_path:
            if not game_state.bot_pathfinding:
                l.info("Pathfinding successful!")
                game_state.bot_pathfinding = True

            navigation_steps = generate_path_navigation(game_state.pacman.scaled_xy(game_state.walls_mapper.map.grid_resolution_px), found_path)
            #print(f"PATH: {str(found_path)}")
            print(f"NAVIGATION: {[str(step) for step in navigation_steps]}")
            self.game_state.bot_navigation = navigation_steps
            self.current_navigation = navigation_steps

            #self.execute_action(pathfinding_actions)
            self.execute_action(game_state.bot_action.action_key)
        else:
            self.game_state.bot_navigation = []
            self.execute_action(game_state.bot_action.action_key)

    def choose_best_action(self, game_state: GameState) -> str:
        """decide the best action to take"""

        pacman = game_state.pacman
        closest_ghost = calculate_closest_entity(pacman, list(game_state.memory.ghosts.values()))

        # powered up - chase ghosts - but only if we have at least 2s left on the powerup timer
        if game_state.powered_up and (game_state.power_up_end_time - time()) > 2:
            if closest_ghost:
                return self.eat(pacman, closest_ghost)

        # avoid nearby ghosts
        if closest_ghost and pacman.distance_to(closest_ghost) < 200:
            return self.run_away_from(pacman, closest_ghost)

        # go for power-up buff
        closest_powerup = calculate_closest_entity(pacman, list(game_state.memory.power_ups.values()))
        if closest_powerup:
            return self.eat(pacman, closest_powerup)

        # go for berry
        closest_berry = calculate_closest_entity(pacman, game_state.berries)
        if closest_berry:
            return self.eat(pacman, closest_berry)

        return self.wander()

    def execute_action(self, action: tuple[str]) -> None:
        # execute the action

        stuck_counter = self.game_state.stuck

        if stuck_counter > 3 and self.current_navigation:
            self.current_navigation = []
            return

        primary, secondary, tertiary = action

        if stuck_counter == 0:
            action = primary
        elif stuck_counter < 2:
            action = secondary
        else:
            action = tertiary

        self.game_state.bot_move = action

        if action != self.last_key or True:  # temp bypass

            self.last_key = action
            self.last_move_time = time()

            # if self.debug:
            #     pass
            #     #print(f"Would press {action} (debug mode on)")
            # else:
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
