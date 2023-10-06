import logging
import time
from dotenv import load_dotenv

from utils.logging import setup_logging
from utils.game_actions_handler import *
from agent.agent import Agent
from game_environment.server import start_server

# load environment variables
load_dotenv(override=True)

if __name__ == "__main__":
    # TODO delete this
    map_info = {}
    map_info['initial_pos'] = (0,0) # TODO delete this


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
        observations, scene_descriptions = env.step(actions)
        input("Press Enter to continue...") # TODO: Remove this, just for testing one step

        scene_descriptions = {players[i] : scene_descriptions[i] for i in range(len(players))}
        logger.info('Observations: %s', observations, 'Scene descriptions: %s', scene_descriptions)

        # Get the actions of the agents
        agents_map_actions = {}
        for agent in agents:
            agent_position, agent_orientation = scene_descriptions[agent.name]['global_position'], scene_descriptions[agent.name]['orientation']
            step_action = agent.move(observations[agent.name], agent_position, agent_orientation)
            agents_map_actions[agent.name] = generate_agent_actions_map(step_action)
            logger.info('Agent %s action map: %s', agent.name, agents_map_actions[agent.name] )

            break # TODO: Remove this, just for testing one agent
        for agent in agents[1:]:
            agents_map_actions[agent.name] = default_agent_actions_map()

        logger.info('Calculated all Agents actions for this step: %s', agents_map_actions)
        actions = agents_map_actions

    env.end_game()

    logger.info("Program finished")