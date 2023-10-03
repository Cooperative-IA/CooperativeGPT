from dotenv import load_dotenv
import logging
from llm import LLMModels

from utils.logging import setup_logging


# load environment variables
load_dotenv(override=True)

if __name__ == "__main__":

    setup_logging()
    logger = logging.getLogger(__name__)

    llm = LLMModels().get_main_model()
    response = llm.completion('testing.txt', inputs=['Manuel'])


    logger.info("Program started")
    logger.info("Program finished")