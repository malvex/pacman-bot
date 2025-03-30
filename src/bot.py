from my_keyboard import press_key
from helper import calculate_closest_entity, direction_to
from models import BotAction, BotActionType, Entity, EntityClass
from pathfinding import get_path_actions
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

        # todo
        self.blocked_actions = []

    def iterate(self) -> None:
        game_state = self.game_state

        # if we dont see pacman then dont do anything (e.g. dead pacman, game in menu, or not loaded)
        if not game_state.pacman:
            return

        # check cooldown to prevent changing mind too often
        current_time = time()
        if current_time - self.last_move_time < self.move_cooldown:
            return

        # todo - state machine

        game_state.bot_action = self.choose_best_action(game_state)

        pathfinding_actions = get_path_actions(game_state.walls_mapper.map, game_state.pacman, game_state.bot_action)

        if pathfinding_actions:
            if not game_state.bot_pathfinding:
                l.info("Pathfinding successful!")
                print(f"PATH: {str(pathfinding_actions)}")
                game_state.bot_pathfinding = True

            #self.execute_action(pathfinding_actions)
            self.execute_action(game_state.bot_action.action_key)
        else:
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
