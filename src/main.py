from inference import InferencePipeline

from game_state import GameState
from walls_mapper import WallsMapper
from bot import Bot
from minimap import draw_map

import config
import logging
import argparse


# setup logging
logging.basicConfig(
    filename="out.log",
    level=logging.INFO,
    format='%(asctime)s [%(levelname).1s] <%(name)s> %(message)s',  # %(funcName)s
    datefmt='%H:%M:%S')


class InputDevice:  # not enum on purpose
    WEBCAMERA = 0
    OBS = 2

# global components - fixme
game_state = None
walls_mapper = None
bot = None


def my_sink(result, video_frame):
    if "predictions" in result:

        # update game state with new predictions
        game_state.update(result["predictions"]["predictions"])

        # take action based on the game state
        bot.iterate(game_state)

        # draw minimap window
        draw_map(game_state, walls_mapper.map, walls_mapper.entity_max_size_px, bot.current_action, bot.current_navigation)

        # report current action
        # self.
        # action_name = self.bot_action.action_type.name if self.bot_action else "(no action)"
        # power_timer = f" Power up! ({ self.power_up_end_time - time():.2f})" if self.powered_up else ""

        # print(f"P/G/P/B: {self.pacman is not None}/{len(self.ghosts)}/{len(self.buffs)}/{len(self.berries)}"
        #     + f" | Stuck: {self.stuck} | {action_name} ({self.bot_move}) {power_timer}"
        #     + " " * 20, end="\r")



def start(workspace_name: str, api_key: str, workflow_id: str, device_id: int = InputDevice.OBS) -> None:

    pipeline = InferencePipeline.init_with_workflow(
        api_key=api_key,
        workspace_name=workspace_name,
        workflow_id=workflow_id,
        video_reference=device_id,
        max_fps=30,
        on_prediction=my_sink,
        serialize_results=True
    )

    pipeline.start()
    pipeline.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help="Enable debug mode", action="store_true")
    parser.add_argument("--disable-pathfinding", help="Disable pathfinding", action="store_true")
    args = parser.parse_args()

    walls_mapper = WallsMapper()
    game_state = GameState(walls_mapper, debug=config.DEBUG)
    bot = Bot(enable_navigation=not args.disable_pathfinding)

    logging.info("Starting...")
    start(config.WORKSPACE_NAME, config.API_KEY, config.WORKFLOW_ID)
