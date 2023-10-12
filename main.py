import asyncio
import logging
from dotenv import load_dotenv
import time
from utils.logger_singleton import LoggerSingleton

from game_environment.utils import generate_agent_actions_map,  default_agent_actions_map
from agent.agent import Agent
from game_environment.server import start_server, get_scenario_map
from llm import LLMModels


# load environment variables
load_dotenv(override=True)
logger_instance = LoggerSingleton()
logger = logging.getLogger(__name__)

step_count = 0

async def agent_loop(agent: Agent, observations: list[str], scene_descriptions: list[str], game_time: int) -> tuple[str, str]:
    """
    Description: Returns the actions that the agent should perform given its name, the world context, the current plan, the memory statements and the current observations

    Args:
        agent (Agent): Agent
        observations (list[str]): Current observations
        scene_descriptions (list[str]): Scene descriptions
        game_time (int): Game time

    Returns:
        tuple[str, str]: Actions that the agent should perform
    """

    scene_descriptions = {agents[i].name : scene_descriptions[i] for i in range(len(agents))}
    agent_current_scene = scene_descriptions[agent.name]
    logger.info('%s Observations: %s, Scene descriptions: %s', agent.name, observations[agent.name], scene_descriptions[agent.name])
    # Get the action for the agent
    step_action = await agent.move(observations[agent.name], agent_current_scene, game_time)
    agent_action_map = await generate_agent_actions_map(step_action)
    logger.info('Agent %s action map: %s', agent.name, agent_action_map  )   

    return (agent.name, agent_action_map)

async def game_loop(agents: list[Agent]) -> None:
    """Main game loop. The game loop is executed until the game ends or the maximum number of steps is reached.
    
    Args:
        agents (list[Agent]): List of agents.

    Returns:
        None
    """
    global step_count
    actions = None
    step_count, max_steps = 0, 100

    # Get the initial observations and environment information
    observations, scene_descriptions = env.step(actions)

    while step_count < max_steps:
        # Reset the actions for each agent
        game_time = env.get_time()
        # Execute an action for each agent on each step
        agents_actions_manager = [agent_loop(agent, observations, scene_descriptions, game_time) for agent in agents]
        agents_actions_list = await asyncio.gather(*agents_actions_manager) 
        
        agents_map_actions = {agent_name: map_actions  for agent_name, map_actions in agents_actions_list}

        env.step(agents_map_actions)
        logger.info('Calculated all Agents actions for this step: %s', agents_map_actions)
        step_count += 1
        time.sleep(0.01)

if __name__ == "__main__":
    logger.info("Program started")

    logger_instance = LoggerSingleton()

    # Define players
    players = ["Juan", "Laura", "Pedro"]
    players_context = ["juan_context.json", "laura_context.json", "pedro_context.json"]
    valid_actions = ['grab apple (x,y)', 'attack player (player_name)', 'go to the tree (treeId) at (x,y)','explore'] # TODO : Change this.
    scenario_obstacles  = ['W', '$'] # TODO : Change this.
    scenario_info = {'scenario_map': get_scenario_map(), 'valid_actions': valid_actions, 'scenario_obstacles': scenario_obstacles}
    # Create agents
    agents = [Agent(name=player, data_folder="data", agent_context_file=player_context, world_context_file="world_context.txt", scenario_info=scenario_info) for player, player_context in zip(players, players_context)]

    # Start the game server
    env = start_server(players, record=True)


    llm = LLMModels().get_main_model()
    try:
        asyncio.run(game_loop(agents))  # updated line
    except KeyboardInterrupt:
        logger.info("Program interrupted. %s steps executed.", step_count)
    except Exception as e:
        logger.exception("Exception: %s", e)
    
    env.end_game()
       
    # LLm total cost
    costs = llm.cost_manager.get_costs()
    tokens = llm.cost_manager.get_tokens()
    logger.info("LLM total cost: %.2f, total tokens: %s", costs['total_cost'], tokens['total_tokens'])


    logger.info("Program finished")