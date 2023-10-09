import logging
from dotenv import load_dotenv

from utils.logging import setup_logging
from game_environment.utils import generate_agent_actions_map,  default_agent_actions_map
from agent.agent import Agent
from game_environment.server import start_server, get_scenario_map


# load environment variables
load_dotenv(override=True)

if __name__ == "__main__":


    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Program started")

    # Define players
    players = ["Juan", "Laura", "Pedro"]
    players_context = ["juan_context.json", "laura_context.json", "pedro_context.json"]
    valid_actions = ['grab apple (x,y)', 'attack player (player_name)', 'go to the tree (treeId) at (x,y)','explore'] # TODO : Change this.
    scenario_obstacles  = ['W', '$'] # TODO : Change this.
    scenario_info = {'scenario_map': get_scenario_map(), 'valid_actions': valid_actions, 'scenario_obstacles': scenario_obstacles}
    # Create agents
    agents = [Agent(name=player, data_folder="data", agent_context_file=player_context, world_context_file="world_context.txt", scenario_info=scenario_info) for player, player_context in zip(players, players_context)]

    # Start the game server
    env = start_server(players)

    # Game loop
    actions = None
    step_count, max_steps = 0, 100

    while step_count < max_steps:
        
        observations, scene_descriptions = env.step(actions)
        input("Press Enter to continue...") # TODO: Remove this, just for testing one step

        scene_descriptions = {players[i] : scene_descriptions[i] for i in range(len(players))}
        logger.info('Observations: %s', observations, 'Scene descriptions: %s', scene_descriptions)

        game_time = env.get_time()

        # Get the actions of the agents
        agents_map_actions = {}
        for agent in agents:
            agent_position, agent_orientation = scene_descriptions[agent.name]['global_position'], scene_descriptions[agent.name]['orientation']
            agent_current_scene = scene_descriptions[agent.name]
            step_action = agent.move(observations[agent.name], agent_current_scene, game_time)
            agents_map_actions[agent.name] = generate_agent_actions_map(step_action)
            logger.info('Agent %s action map: %s', agent.name, agents_map_actions[agent.name] )

            break # TODO: Remove this, just for testing one agent
        for agent in agents[1:]:
            agents_map_actions[agent.name] = default_agent_actions_map()

        logger.info('Calculated all Agents actions for this step: %s', agents_map_actions)
        actions = agents_map_actions
        step_count += 1
    env.end_game()

    logger.info("Program finished")