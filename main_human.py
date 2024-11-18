from datetime import datetime
from importlib import import_module
import logging
import os
from dotenv import load_dotenv
import time
import traceback
from utils.logging import setup_logging, CustomAdapter
from game_environment.utils import generate_agent_actions_map, check_agent_out_of_game, get_defined_valid_actions
from agent.agent import Agent
from agent.human_agent import HumanAgent
from game_environment.server import start_server, get_scenario_map,  default_agent_actions_map, condition_to_end_game
from llm import LLMModels
from utils.queue_utils import new_empty_queue
from utils.args_handler import get_args
from utils.agent_creator import agentCreator
from utils.files import extract_players, get_players_contexts, persist_short_term_memories, create_directory_if_not_exists
from utils.player_gui import PlayerGUI

# Set up logging timestamp
logger_timestamp = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
# load environment variables
load_dotenv(override=True)

logger = logging.getLogger(__name__)
rounds_count = 0

def game_loop(agents: list[Agent | HumanAgent], substrate_name:str, persist_memories:bool, gui:PlayerGUI) -> None:
    """Main game loop. The game loop is executed until the game ends or the maximum number of steps is reached.

    Args:
        agents (list[Agent]): List of agents.
        substrate_name (str): Name of the substrate.
        persist_memories (bool): Whether to persist the agents memories to the logs folder.
        gui (PlayerGUI): GUI object.
    Returns:
        None
    """
    global rounds_count
    actions = None

    # Define bots number of steps per action
    rounds_count, steps_count, max_rounds = 0, 0, 1000

    # Get the initial observations and environment information
    env.step(actions)
    actions = {player_name: default_agent_actions_map() for player_name in env.player_prefixes}
    env.step(actions)
    
    while rounds_count < max_rounds and not condition_to_end_game(substrate_name, env.get_current_global_map()):
        # Reset the actions for each agent
        actions = {player_name: default_agent_actions_map() for player_name in env.player_prefixes}
        # Execute an action for each agent on each step
        id_turn = 0
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
            player_images, agents_orientations  = list(env.get_agents_view_imgs().values()), list(env.get_agents_orientations().values())
            gui.update(player_images, agents_orientations, id_turn, "Aloooo observaciones mi papa")
            
            
            logger.info("\n\n" + f"Agent's {agent.name} turn".center(50, '#') + "\n")
            logger.info('%s Observations: %s, Scene descriptions: %s', agent.name, observations, scene_description)
            # Get the steps for the agent to execute a high level action
            agent_reward = env.score[agent.name]
            if check_agent_out_of_game(observations):
                logger.info('Agent %s was taken out of the game', agent.name)
                step_action = agent.move(observations, scene_description, state_changes, env.get_current_global_map(), game_time, gui, agent_reward , agent_is_out=True)
            else:
                step_action = agent.move(observations, scene_description, state_changes, env.get_current_global_map(), game_time, gui, agent_reward)


            # Update the actions map for the agent
            actions[agent.name] = generate_agent_actions_map(step_action, default_agent_actions_map())
            logger.info('Agent %s action map: %s', agent.name, actions[agent.name] )
            
            id_turn += 1

        # Execute a move for the bots
        if env.bots:
            for bot in env.bots:
                bot_observations =  env.get_observations_by_player(bot.name)
                bot_observations = bot_observations['curr_state']
                if check_agent_out_of_game(bot_observations):
                    logger.info(f'Bot {bot.name} was taken out of the game. Skipping bot move.')
                    actions[bot.name] = default_agent_actions_map()
                else:
                    bot_action = bot.move(env.timestep)
                    actions[bot.name] = bot_action

        # Execute the step with all the actions per agent at the same time
        try:
            env.step(actions)
            steps_count += 1
        except:
            logger.exception("Error executing actions %s", actions)

        
                
        # Persist the short term memories of the agents
        if persist_memories:
            memories = {agent.name: agent.stm.get_memories().copy() for agent in agents}
            persist_short_term_memories(memories, rounds_count, steps_count, logger_timestamp)

        rounds_count += 1
        logger.info('Round %s completed. Executed all the high level actions for each agent.', rounds_count)
        env.update_history_file(logger_timestamp, rounds_count, steps_count)
        time.sleep(0.01)

if __name__ == "__main__":
    args = get_args()
    setup_logging(logger_timestamp)
    logger.info("Program started")
    start_time = time.time()

    # Define the simulation mode
    mode = None # cooperative or None, if cooperative the agents will use the cooperative modules
        
    global substrate_utils
    substrate_utils = import_module(f'game_environment.substrates.utilities.{args.substrate}.substrate_utils')
    
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
    players_context = get_players_contexts(agents_bio_dir)
    players_names = extract_players(players_context)
    
    world_context_path = os.path.join(experiment_path, "world_context", f'{args.world_context}.txt')

    # Load the scenario map, the valid actions and the scenario obstacles
    scenario_info = substrate_utils.load_scenario_info(get_players_contexts(agents_bio_dir, include_bots=True), world_context_path=world_context_path)
    data_folder = "data" if not args.simulation_id else f"data/databases/{args.simulation_id}"
    create_directory_if_not_exists (data_folder)
    # Create agents
    agents = [agentCreator(is_human_player=True, name=player_name, data_folder="data", agent_context=player_context, world_context_file=world_context_path, scenario_info=scenario_info, mode=mode, prompts_folder=args.prompts_source,
                           substrate_name=args.substrate, start_from_scene = scene_path, agent_id=player_context["id"][-1]) for player_name, player_context in zip(players_names, players_context)]

    # Start the game server
    env = start_server(players_names, init_timestamp=logger_timestamp, game_name=  args.substrate, scenario=args.scenario, kind_experiment = args.kind_experiment)
    
    # Start the GUI 
    
    player_images  = list (env.get_agents_view_imgs().values())
    gui = PlayerGUI(player_images,players_names, args.substrate)
    gui.start_gui_thread()
    
    logger = CustomAdapter(logger, game_env=env)
    # We are setting args.prompts_source as a global variable to be used in the LLMModels class
    llm = LLMModels()
    gpt_model = llm.get_main_model()
    gpt_longer_context = llm.get_longer_context_fallback()
    embedding_model = llm.get_embedding_model()
    gpt_best_model = llm.get_best_model()
    try:
        game_loop(agents, args.substrate, args.persist_memories, gui)
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
        
