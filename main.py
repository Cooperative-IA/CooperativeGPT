import logging
import time
from dotenv import load_dotenv

from utils.logging import setup_logging
from agent.agent import Agent
from game_environment.server import start_server

# TODO delete  this
current_observations = [
        'Observed an apple at position [1, 15]. This apple belongs to tree 3',
        'Observed an apple at position [2, 14]. This apple belongs to tree 3',
        'Observed an apple at position [2, 15]. This apple belongs to tree 3',
        'Observed an apple at position [2, 16]. This apple belongs to tree 3',
        'Observed an apple at position [3, 13]. This apple belongs to tree 3',
        'Observed an apple at position [3, 14]. This apple belongs to tree 3',
        'Observed an apple at position [3, 15]. This apple belongs to tree 3',
        'Observed an apple at position [3, 16]. This apple belongs to tree 3',
        'Observed an apple at position [3, 17]. This apple belongs to tree 3',
        'Observed an apple at position [4, 14]. This apple belongs to tree 3',
        'Observed an apple at position [4, 15]. This apple belongs to tree 3',
        'Observed an apple at position [4, 16]. This apple belongs to tree 3',
        'Observed an apple at position [5, 15]. This apple belongs to tree 3',
        'Observed tree 3 at position [3, 15]. This tree has 13 apples remaining and 0 grass for apples growing',
        'Observed an apple at position [1, 20]. This apple belongs to tree 4',
        'Observed an apple at position [1, 21]. This apple belongs to tree 4',
        'Observed an apple at position [2, 21]. This apple belongs to tree 4',
        'Observed tree 4 at position [1, 20]. This tree has 3 apples remaining and 0 grass for apples growing'
    ]

# load environment variables
load_dotenv(override=True)

if __name__ == "__main__":
    # TODO delete this
    map_info = {}
    map_info['initial_pos'] = (8,8) # TODO delete this


    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Program started")

    # Define players
    players = ["Juan", "Laura", "Pedro"]
    players_context = ["juan_context.json", "laura_context.json", "pedro_context.json"]
    # Create agents
    agents = [Agent(name=player, data_folder="data", agent_context_file=player_context, world_context_file="world_context.txt", map_info=map_info) for player, player_context in zip(players, players_context)]

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