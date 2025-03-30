from inference import InferencePipeline

from game_state import GameState
from walls_mapper import WallsMapper
from bot import Bot

import config
import logging


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
        bot.iterate()


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
    walls_mapper = WallsMapper()
    game_state = GameState(walls_mapper, debug=config.DEBUG)
    bot = Bot(game_state, debug=config.DEBUG)

    logging.info("Starting...")
    start(config.WORKSPACE_NAME, config.API_KEY, config.WORKFLOW_ID)
