from my_keyboard import press_key
from helper import calculate_distance, calculate_closest_entity, direction_to, direction_away_from
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
        # if we dont see pacman then dont do anything (e.g. dead pacman, game in menu, or not loaded)
        if not self.game_state.pacman:
            return

        # check cooldown to prevent changing mind too often
        current_time = time()
        if current_time - self.last_move_time < self.move_cooldown:
            return

        # todo - state machine

        action = self.choose_best_action(self.game_state)
        self.execute_action(action)

    def choose_best_action(self, game_state: GameState) -> str:
        """decide the best action to take"""

        pacman = game_state.pacman
        closest_ghost = calculate_closest_entity(pacman, list(game_state.ghosts.values()))

        # powered up - chase ghosts
        if game_state.powered_up:
            if closest_ghost:
                direction = direction_to(pacman, closest_ghost)
                return direction

        # avoid nearby ghosts
        if closest_ghost and calculate_distance(pacman, closest_ghost) < 100:
            direction = direction_away_from(pacman, closest_ghost)
            return direction

        # go for power-up buff
        closest_buff = calculate_closest_entity(pacman, game_state.buffs)
        if closest_buff:
            direction = direction_to(pacman, closest_buff)
            return direction

        # go for berry
        closest_berry = calculate_closest_entity(pacman, game_state.berries)
        if closest_berry:
            direction = direction_to(pacman, closest_berry)
            return direction

        # default action - if nothing goes right, go left :)
        return self.last_key or "left"

    def execute_action(self, action: str) -> None:
        # execute the action
        if action != self.last_key or True:  # temp bypass

            self.last_key = action
            self.last_move_time = time()

            if self.debug:
                pass
                #print(f"Would press {action} (debug mode on)")
            else:
                press_key(action)
