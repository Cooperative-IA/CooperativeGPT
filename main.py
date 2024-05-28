from datetime import datetime
import logging
import os
from agent.cognitive_modules.communicate import CommunicationMode
from agent.management.agent_registry import AgentRegistry
from dotenv import load_dotenv
import time
import traceback
from utils.logging import setup_logging, CustomAdapter
from game_environment.utils import generate_agent_actions_map, check_agent_out_of_game, get_defined_valid_actions, get_number_of_apples_by_tree
from agent.agent import Agent
from game_environment.server import start_server, get_scenario_map,  default_agent_actions_map, condition_to_end_game
from llm import LLMModels
from utils.queue_utils import new_empty_queue
from utils.args_handler import get_args
from utils.files import extract_players, persist_short_term_memories, create_directory_if_not_exists

# Set up logging timestamp
logger_timestamp = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
# load environment variables
load_dotenv(override=True)

logger = logging.getLogger(__name__)
rounds_count = 0

def game_loop(agents: list[Agent], substrate_name:str, persist_memories:bool) -> None:
    """Main game loop. The game loop is executed until the game ends or the maximum number of steps is reached.

    Args:
        agents (list[Agent]): List of agents.
        substrate_name (str): Name of the substrate.
        persist_memories (bool): Whether to persist the agents memories to the logs folder.
    Returns:
        None
    """
    global rounds_count
    actions = None

    # Define bots number of steps per action
    rounds_count, steps_count, max_rounds = 0, 0, 100
    bots_steps_per_agent_move = 2

    # Get the initial observations and environment information
    env.step(actions)
    actions = {player_name: default_agent_actions_map() for player_name in env.player_prefixes}
    env.step(actions)
    
    while rounds_count < max_rounds and not condition_to_end_game(substrate_name, env.get_current_global_map()):
        # Reset the actions for each agent
        actions = {player_name: default_agent_actions_map() for player_name in env.player_prefixes}
        # Execute an action for each agent on each step
        for agent in agents:
            # Helps to define the dynamic number of bot steps per action as acumulated number
            accumulated_steps = 0

            #Updates the observations for the current agent
            all_observations =  env.get_observations_by_player(agent.name)
            observations = all_observations['curr_state']
            scene_description = all_observations['scene_description']
            state_changes = all_observations['state_changes']
            # Get the current observations and environment information
            game_time = env.get_time()
            logger.info("\n\n" + f"Agent's {agent.name} turn".center(50, '#') + "\n")
            logger.info('%s Observations: %s, Scene descriptions: %s', agent.name, observations, scene_description)
            # Get the steps for the agent to execute a high level action
            agent_reward = env.score[agent.name]
            if check_agent_out_of_game(observations):
                logger.info('Agent %s was taken out of the game', agent.name)
                agent.move(observations, scene_description, state_changes, game_time, rounds_count, env.get_current_global_map(), agent_reward, agent_is_out=True)
                step_actions = new_empty_queue()
            else:
                step_actions = agent.move(observations, scene_description, state_changes, game_time, rounds_count, env.get_current_global_map(), agent_reward)

            map_previous_to_actions = env.get_current_global_map()
            while not step_actions.empty():
                step_action = step_actions.get()
                # Update the actions map for the agent
                actions[agent.name] = generate_agent_actions_map(step_action, default_agent_actions_map())
                logger.info('Agent %s action map: %s', agent.name, actions[agent.name] )

                # Execute a move for the bots
                if env.bots:
                    for bot in env.bots:
                        bot_observations =  env.get_observations_by_player(bot.name)
                        bot_observations = bot_observations['curr_state']
                        if check_agent_out_of_game(bot_observations):
                            logger.info(f'Bot {bot.name} was taken out of the game. Skipping bot move.')
                            actions[bot.name] = default_agent_actions_map()
                        if env.get_current_step_number() % bots_steps_per_agent_move == 0:
                            bot_action = bot.move(env.timestep)
                            actions[bot.name] = bot_action
                        else:
                            actions[bot.name] = default_agent_actions_map()

                # Execute each step one by one until the agent has executed all the steps for the high level action
                try:
                    env.step(actions)
                    steps_count += 1
                    accumulated_steps += 1
                except:
                    logger.exception("Error executing action %s", step_action)
                    step_actions = new_empty_queue()
            if not check_agent_out_of_game(observations):
                all_observations =  env.get_observations_by_player(agent.name)
                observations = all_observations['curr_state']
                scene_description = all_observations['scene_description']
                agent.spatial_memory.update_current_scene(scene_description['global_position'], scene_description['orientation'],\
                                                        scene_description['observation'], env.get_current_global_map())
                agent.communicate_environment_observations()
            map_after_actions = env.get_current_global_map()
            own_actions = list()

            # Precompute the number of apples by tree
            apples_by_tree = get_number_of_apples_by_tree(map_previous_to_actions, agent.spatial_memory.global_trees_fixed)
            set_of_remaining_apples_by_tree = {apples_by_tree[tree] for tree in apples_by_tree}

            # Obtenemos todos los valores del diccionario
            valores = list(apples_by_tree.values())

            # Comparamos todos los valores con el primer valor de la lista
            todos_iguales = all(valor == valores[0] for valor in valores)

            # Iterate over the matrix positions
            for row in range(len(map_previous_to_actions)):
                for col in range(len(map_previous_to_actions[row])):
                    prev, after = map_previous_to_actions[row][col], map_after_actions[row][col]
                    
                    # Check if there's a change in the map at the current position
                    if prev != after:
                        # Handle apple consumption
                        if prev == 'A' and after != 'B':
                            message = f"Hello, I am {agent.name} and I ate an Apple at position [{row},{col}]"
                            own_actions.append(message)
                            
                            # Update apple consumption count
                            tree_index = agent.spatial_memory.global_trees_fixed[(row, col)][0]
                            apple_count = apples_by_tree[tree_index]
                            if not todos_iguales:
                                agent.apple_consumption_per_remaining[apple_count-1] += 1
                            
                                # Update remaining apples for all trees
                                for tree in set_of_remaining_apples_by_tree:
                                    agent.remaining_total[tree - 1] += 1
                        
                        # Handle attacks
                        if prev.isnumeric() and prev != agent.agent_registry.agent_name_to_id[agent.name]:
                            attacked_agent = agent.agent_registry.agent_id_to_name[prev]
                            message = f"Hello, I am {agent.name} and I Attacked to the agent {attacked_agent} at position {row},{col}"
                            own_actions.append(message)

            # Communicate the actions to the other agents
            agent.communicate_own_actions(own_actions, rounds_count)



            # Reset actions for the agent until its next turn
            actions[agent.name] = default_agent_actions_map()
            
            # Persist the short term memories of the agents
            if persist_memories:
                memories = {agent.name: agent.stm.get_memories().copy() for agent in agents}
                persist_short_term_memories(memories, rounds_count, steps_count, logger_timestamp)
            if "known_agent_interactions" in agent.stm.memory:
                logger.info(f"Known agent interactions: {agent.stm.memory['known_agent_interactions']}")
        rounds_count += 1
        logger.info('Round %s completed. Executed all the high level actions for each agent.', rounds_count)
        env.update_history_file(logger_timestamp, rounds_count, steps_count)
        time.sleep(0.01)
    metrics = {
        'updated_frequency_map': {},
        'apple_consumption_per_remaining': {},
        'remaining_total': {},
        'react_per_round': {},
        'explored_map_per_round': {},
        'updated_map_per_round': {},
        'known_trees_per_round': {},
        'attacks': {},
        'reflections': {}
    }
    for agent in agents:
        metrics['updated_frequency_map'][agent.name] = agent.spatial_memory.updated_frequency_map
        metrics['apple_consumption_per_remaining'][agent.name] = agent.apple_consumption_per_remaining
        metrics['remaining_total'][agent.name] = agent.remaining_total
        metrics['react_per_round'][agent.name] = agent.reacted_times_per_round
        metrics['explored_map_per_round'][agent.name] = agent.spatial_memory.explored_map_per_round
        metrics['updated_map_per_round'][agent.name] = agent.spatial_memory.updated_map_per_round
        metrics['known_trees_per_round'][agent.name] = agent.spatial_memory.known_trees_per_round
        metrics['attacks'][agent.name] = agent.attacks
        metrics['reflections'][agent.name] = agent.reflections
    env.write_snowartz_metrics(logger_timestamp, metrics)
    logger.info('Game ended after %s rounds', rounds_count)
if __name__ == "__main__":
    args = get_args()
    setup_logging(logger_timestamp)
    logger.info("Program started")
    start_time = time.time()

    # Define the simulation mode
    mode = None # cooperative or None, if cooperative the agents will use the cooperative modules
    
    # If the experiment is "personalized", prepare a start_variables.txt file on config path
    # It will be copied from args.scene_path, file is called variables.txt 
    scene_path = None
    if args.start_from_scene :
        scene_path = f"data/scenes/{args.start_from_scene}" 
        os.system(f"cp {scene_path}/variables.txt config/start_variables.txt")
        
    # Define players
    experiment_path = os.path.join("data", "defined_experiments", args.substrate)
    agents_bio_dir =  os.path.join( experiment_path, "agents_context", args.agents_bio_config)
    game_scenario = args.scenario if args.scenario != "default" else None
    players_context = [os.path.abspath(os.path.join(agents_bio_dir, player_file)) for player_file in os.listdir(agents_bio_dir)]

    players = extract_players(players_context)
    
    world_context_path = os.path.join(experiment_path, "world_context", f'{args.world_context}.txt')
    valid_actions = get_defined_valid_actions(game_name= args.substrate)
    scenario_obstacles  = ['W', '$'] # TODO : Change this. This should be also loaded from the scenario file
    scenario_info = {'scenario_map': get_scenario_map(game_name=args.substrate), 'valid_actions': valid_actions, 'scenario_obstacles': scenario_obstacles} ## TODO: ALL THIS HAVE TO BE LOADED USING SUBSTRATE NAME
    data_folder = "data" if not args.simulation_id else f"data/databases/{args.simulation_id}"
    create_directory_if_not_exists (data_folder)

    # Create the agent registry
    agent_registry = AgentRegistry(players)

    # Create agents
    agents = [Agent(name=player, data_folder=data_folder, agent_context_file=player_context,
                    world_context_file=world_context_path, scenario_info=scenario_info, mode=mode,
                    prompts_folder=str(args.prompts_source), substrate_name=args.substrate, start_from_scene = scene_path, agent_registry=agent_registry, game_time = datetime.now().replace(minute=0, second=0, microsecond=0).strftime("%Y-%m-%d %H:%M:%S")) 
              for player, player_context in zip(players, players_context)]

    # Start the game server
    env = start_server(players, init_timestamp=logger_timestamp, record=args.record, game_name=  args.substrate, scenario=args.scenario, kind_experiment = args.kind_experiment)
    logger = CustomAdapter(logger, game_env=env)
    # We are setting args.prompts_source as a global variable to be used in the LLMModels class
    llm = LLMModels()
    gpt_model = llm.get_main_model()
    gpt_longer_context = llm.get_longer_context_fallback()
    embedding_model = llm.get_embedding_model()
    gpt_best_model = llm.get_best_model()
    try:
        game_loop(agents, args.substrate, args.persist_memories)
    except KeyboardInterrupt:
        logger.info("Program interrupted. %s rounds executed.", rounds_count)
    except Exception as e:
        logger.exception("Rounds executed: %s. Exception: %s", rounds_count, e)

    env.end_game()

    # Persisting agents memories to the logs folder
    if args.persist_memories:
        os.system(f"cp -r {data_folder}/ltm_database logs/{logger_timestamp}")
    

    # LLm total cost
    costs = llm.get_costs()
    tokens = llm.get_tokens()
    logger.info("LLM total cost: {:,.2f}, Cost by model: {}, Total tokens: {:,}, Tokens by model: {}".format(costs['total'], costs,  tokens['total'], tokens))

    end_time = time.time()
    logger.info("Execution time: %.2f minutes", (end_time - start_time)/60)

    logger.info("Program finished")
    
    # If there's a simulation_id, we will change the logs/{logger_timestamp} name to logs/{logger_timestamp}__{simulation_id}
    if args.simulation_id:
        os.system(f"mv logs/{logger_timestamp} logs/{logger_timestamp}__{args.simulation_id}")
        
