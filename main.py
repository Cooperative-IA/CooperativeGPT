from dotenv import load_dotenv
import logging

from utils.logging import setup_logging

# load environment variables
load_dotenv()

if __name__ == "__main__":

    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Program started")
    logger.info("Program finished")