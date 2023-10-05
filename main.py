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

    # Define players
    players = ["Juan", "Laura", "Pedro"]
    players_context = ["juan_context.json", "laura_context.json", "pedro_context.json"]
    # Create agents
    agents = [Agent(name=player, data_folder="data", agent_context_file=player_context, world_context_file="world_context.txt") for player, player_context in zip(players, players_context)]

    # Start the game server
    env = start_server(players)

    # Game loop
    actions = None
    while True:
        observations = env.step(actions)
        logger.info('Observations: %s', observations)

        # Get the actions of the agents
        for agent in agents:
            agent.move(observations[agent.name])
            break # TODO: Remove this break, just for testing one agent

        # wait for 10 seconds
        time.sleep(10) # TODO: Remove this, just for testing one step
        break

    env.end_game()

    logger.info("Program finished")