from datetime import datetime
import logging
from dotenv import load_dotenv
import time
import traceback
from utils.logging import setup_logging, CustomAdapter
from game_environment.utils import generate_agent_actions_map,  default_agent_actions_map, check_agent_out_of_game
from agent.agent import Agent
from game_environment.server import start_server, get_scenario_map
from llm import LLMModels
from utils.queue_utils import new_empty_queue

# Set up logging timestamp
logger_timestamp = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
# load environment variables
load_dotenv(override=True)

logger = logging.getLogger(__name__)

rounds_count = 0

def game_loop(agents: list[Agent]) -> None:
    """Main game loop. The game loop is executed until the game ends or the maximum number of steps is reached.
    
    Args:
        agents (list[Agent]): List of agents.

    Returns:
        None
    """
    global rounds_count
    actions = None
    rounds_count, steps_count, max_steps = 0, 0, 200

    # Define bots number of steps per action
    bots_steps_per_action = 3

    # Get the initial observations and environment information
    observations, scene_descriptions = env.step(actions)

    while rounds_count < max_steps:
        # Reset the actions for each agent
        actions = {player_name: default_agent_actions_map() for player_name in env.player_prefixes}
        # Execute an action for each agent on each step
        for agent in agents:
            #Updates the observations for the current agent
            observations, scene_descriptions = env.step({player_name: default_agent_actions_map() for player_name in env.player_prefixes})
            steps_count += 1
            # Get the current observations and environment information
            game_time = env.get_time()
            scene_descriptions = {agents[i].name : scene_descriptions[i] for i in range(len(agents))}
            agent_current_scene = scene_descriptions[agent.name]
            logger.info("\n\n" + f"Agent's {agent.name} turn".center(50, '#') + "\n")
            logger.info('%s Observations: %s, Scene descriptions: %s', agent.name, observations[agent.name], scene_descriptions[agent.name])
            # Get the steps for the agent to execute a high level action

            if check_agent_out_of_game(observations, agent):
                logger.info('Agent %s was taken out of the game', agent.name)
                agent.move(observations[agent.name], agent_current_scene, game_time, agent_is_out=True)
                step_actions = new_empty_queue()
            else:
                step_actions = agent.move(observations[agent.name], agent_current_scene, game_time)


            while not step_actions.empty():
                step_action = step_actions.get()
                # Update the actions map for the agent
                actions[agent.name] = generate_agent_actions_map(step_action)
                logger.info('Agent %s action map: %s', agent.name, actions[agent.name] )
                # Execute each step one by one until the agent has executed all the steps for the high level action
                try: 
                    observations, scene_descriptions = env.step(actions)
                    steps_count += 1
                except:
                    logger.exception("Error executing action %s", step_action)
                    step_actions = new_empty_queue()
                    
            # Reset actions for the agent until its next turn
            actions[agent.name] = default_agent_actions_map()

        # Execute the actions for the bots if a scenario is provided
        if env.bots:
            for bot in env.bots:
                actions = {player_name: default_agent_actions_map() for player_name in env.player_prefixes}
                for _ in range(bots_steps_per_action): 
                    bot_action = bot.move(env.timestep)
                    actions[bot.name] = bot_action
                    env.step(actions)
                    steps_count += 1

        rounds_count += 1
        logger.info('Round %s completed. Executed all the high level actions for each agent.', rounds_count)
        env.update_history_file(logger_timestamp, rounds_count, steps_count)
        time.sleep(0.01)

if __name__ == "__main__":
    setup_logging(logger_timestamp)

    logger.info("Program started")
    start_time = time.time()


    # Define players
    players = ["Juan", "Laura", "Pedro"]
    players_context = ["juan_context.json", "laura_context.json", "pedro_context.json"]
    valid_actions = ['grab apple (x,y)', 'attack player (player_name) at (x,y)','explore'] # TODO : Change this.
    scenario_obstacles  = ['W', '$'] # TODO : Change this.
    scenario_info = {'scenario_map': get_scenario_map(), 'valid_actions': valid_actions, 'scenario_obstacles': scenario_obstacles}
    # Create agents
    agents = [Agent(name=player, data_folder="data", agent_context_file=player_context, world_context_file="world_context.txt", scenario_info=scenario_info) for player, player_context in zip(players, players_context)]

    # Start the game server
    env = start_server(players, init_timestamp=logger_timestamp, record=True, scenario='commons_harvest__open_0')
    logger = CustomAdapter(logger, game_env=env)


    llm = LLMModels()
    gpt_model = llm.get_main_model()
    embedding_model = llm.get_embedding_model()
    try:
        game_loop(agents)
    except KeyboardInterrupt:
        logger.info("Program interrupted. %s rounds executed.", rounds_count)
    except Exception as e:
        logger.exception("Rounds executed: %s. Exception: %s", rounds_count, e)
    
    env.end_game()
       
    # LLm total cost
    costs = gpt_model.cost_manager.get_costs()['total_cost'] + embedding_model.cost_manager.get_costs()['total_cost']
    tokens = gpt_model.cost_manager.get_tokens()['total_tokens'] + embedding_model.cost_manager.get_tokens()['total_tokens']
    logger.info("LLM total cost: %.2f, total tokens: %s", costs, tokens)

    end_time = time.time()
    logger.info("Execution time: %.2f minutes", (end_time - start_time)/60)

    logger.info("Program finished")