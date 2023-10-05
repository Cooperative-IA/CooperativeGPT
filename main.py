import logging
import time
from dotenv import load_dotenv

from utils.logging import setup_logging
from agent.agent import Agent
from game_environment.server import start_server


# load environment variables
load_dotenv(override=True)

if __name__ == "__main__":

    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Program started")

    # juan = Agent(name="Juan", data_folder="data", agent_context_file="juan_context.json", world_context_file="world_context.txt")
    # juan.move("An apple has grown, there are 6 apples nearby in a patch of grass.")
    players = ["Juan", "Laura", "Pedro"]
    env = start_server(players)

    # Game loop
    actions = None
    while True:
        observations = env.step(actions)
        logger.info('Observations: %s', observations)
        # wait for 10 seconds
        time.sleep(10)
        break

    env.end_game()

    logger.info("Program finished")