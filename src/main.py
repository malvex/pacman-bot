from inference import InferencePipeline

from time import time

from game_state import GameState
from bot import Bot

import config
import logging

# setup logging
logging.basicConfig(filename="out.log", level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class InputDevice:  # not enum on purpose
    WEBCAMERA = 0
    OBS = 2

# global components - fixme
game_state = None
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
    game_state = GameState(debug=config.DEBUG)
    bot = Bot(game_state, debug=config.DEBUG)

    logging.info("Starting...")
    start(config.WORKSPACE_NAME, config.API_KEY, config.WORKFLOW_ID)
