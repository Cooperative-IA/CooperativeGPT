from dotenv import load_dotenv
import logging

from utils.logging import setup_logging
from agent.agent import Agent


# load environment variables
load_dotenv(override=True)

if __name__ == "__main__":

    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Program started")

    juan = Agent(name="Juan", data_folder="data", agent_context_file="juan_context.json", world_context_file="world_context.txt")
    juan.move("An apple has grown, there are 6 apples nearby in a patch of grass.")

    logger.info("Program finished")