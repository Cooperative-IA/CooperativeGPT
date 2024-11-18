import os
from queue import Queue
import queue
import time
from agent.agent import Agent
from utils.llm import load_prompt, replace_inputs_in_prompt
from utils.player_gui import PlayerGUI
from agent.cognitive_modules.perceive import update_known_objects
from agent.cognitive_modules.perceive import should_react, update_known_agents, create_memory, update_known_objects
from utils.communication_handler import CommunicationHandler
class HumanAgent(Agent):
    """HumanAgent class.
    """

    def __init__(self, name: str, data_folder: str, agent_context: dict, world_context_file: str, scenario_info:dict, observations_poignancy = 10, prompts_folder = "base_prompts_v0", substrate_name = "commons_harvest_open", start_from_scene = None, agent_id="" ) -> None:
        """Initializes the agent.

        Args:
            name (str): Name of the agent.
            data_folder (str): Path to the data folder.
            agent_context (str): Path to the json agent context file. Initial info about the agent.
            world_context_file (str): Path to the text world context file. Info about the world that the agent have access to.
            scenario_info (dict): Dictionary with the scenario info. Contains the scenario map and the scenario obstacles.
            att_bandwidth (int, optional): Attention bandwidth. The attention bandwidth is the number of observations that the agent can attend to at the same time. Defaults to 10.
            reflection_umbral (int, optional): Reflection umbral. The reflection umbral is the number of poignancy that the agent needs to accumulate to reflect on its observations. Defaults to 30.
            mode (Mode, optional): Defines the type of architecture to use. Defaults to 'normal'.
            understanding_umbral (int, optional): Understanding umbral. The understanding umbral is the number of poignancy that the agent needs to accumulate to update its understanding (only the poignancy of reflections are taken in account). Defaults to 6.
            observations_poignancy (int, optional): Poignancy of the observations. Defaults to 10.
            substrate_name (str, optional): Name of the substrate. Defaults to "commons_harvest_open".
        """
        prompts_folder = prompts_folder + '_human'
        att_bandwidth = 100
        reflection_umbral = float('inf')
        mode = 'normal'
        super().__init__(name, data_folder, agent_context, world_context_file, scenario_info, att_bandwidth, reflection_umbral, mode, observations_poignancy, prompts_folder=prompts_folder, substrate_name=substrate_name, start_from_scene=start_from_scene, agent_id=agent_id)
        self.agent_id = agent_id
        self.ltm = None
        self.logger.info(f'Initializing {self.name} HumanAgent')

    def move(self, observations: list[str], agent_current_scene:dict, changes_in_state: list[tuple[str, str]], current_global_map: list[list[str]], game_time: str, communication_handler: CommunicationHandler, agent_reward: float = 0, agent_is_out:bool = False) -> Queue:
        """Use all the congnitive sequence of the agent to decide an action to take

        Args:
            observations (list[str]): List of observations of the environment.
            agent_current_scene (dict): Dictionary with the current scene of the agent. It contains the agent position, orientation and the scene description.
                -> global_position (tuple): Current position of the agent in the global map.
                -> orientation (int): Current orientation of the agent. 0: North, 1: East, 2: South, 3: West.
                -> observation (str): ascii representation of the scene.
            changes_in_state (list[tuple[str, str]]): List of changes in the state of the environment and its game time.
            current_global_map (list[list[str]]): Current global map of the environment.
            game_time (str): Current game time.
            agent_reward (float, optional): Current reward of the agent. Defaults to 0.
            agent_is_out (bool, optional): True if the agent is out of the scenario (was taken), False otherwise. Defaults to False.

        Returns:
            Queue: Steps sequence for the current action.
        """
        #Updates the position of the agent in the spatial memory 
        self.spatial_memory.update_current_scene(agent_current_scene['global_position'], agent_current_scene['orientation'],\
                                                    agent_current_scene['observation'], current_global_map)
        self.perceive(observations, changes_in_state, game_time, agent_reward)
        
        # If the agent is out of the game, it does not take any action
        if agent_is_out:
            self.logger.info(f'{self.name} is out of the game, skipping its turn.')
            return None
        
        react = self.generate_new_actions(changes_in_state, communication_handler)
        if react == "not react":
            step_actions = self.get_actions_to_execute(current_global_map, need_update=True)
            return step_actions
        else:
            step_actions = self.get_actions_to_execute(current_global_map, need_update=True)
            return step_actions

    def perceive(self, observations: list[str], changes_in_state: list[tuple[str, str]], game_time: str, reward: float, is_agent_out: bool = False) -> tuple[bool, list[str], list[str]]:
        """Perceives the environment and stores the observation in the long term memory. Decide if the agent should react to the observation.
        It also filters the observations to only store the closest ones, and asign a poignancy to the observations.
        Game time is also stored in the short term memory.
        Args:
            observations (list[str]): List of observations of the environment.
            game_time (str): Current game time.
            reward (float): Current reward of the agent.
        
        Returns:
            tuple[bool, list[str], list[str]]: Tuple with True if the agent should react to the observation, False otherwise, the filtered observations and the changes in the state of the environment.
        """
        action_executed = self.stm.get_memory('step_to_take')
        if is_agent_out:
            memory = create_memory(self.name, game_time, action_executed, [], reward, observations, self.spatial_memory.position, self.spatial_memory.get_orientation_name(), True)
            current_observation = '\n'.join(observations)
            self.stm.add_memory(current_observation, 'current_observation')
            return False, observations, changes_in_state
        
        # Add the game time to the short term memory
        self.stm.add_memory(game_time, 'game_time')
        # Observations are filtered to only store the closest ones. The att_bandwidth defines the number of observations that the agent can attend to at the same time
        sorted_observations = self.spatial_memory.sort_observations_by_distance(observations)
        observations = sorted_observations[:self.att_bandwidth]

        # Update the agent known agents
        update_known_agents(observations, self.stm)
        # Update the agent known objects
        update_known_objects(observations, self.stm, self.substrate_name)
                
        # Parse the changes in the state of the environment observed by the agent
        changes = []
        for change, obs_time in changes_in_state:
            changes.append(f'{change} At {obs_time}')


        # Create a memory from the observations, the changes in the state of the environment and the reward, and add it to the long term memory
        position = self.spatial_memory.position
        orientation = self.spatial_memory.get_orientation_name()
        memory = create_memory(self.name, game_time, action_executed, changes, reward, observations, position, orientation)

        
        current_observation = '\n'.join(observations)
        self.stm.add_memory(current_observation, 'current_observation')
        orientation = self.spatial_memory.get_orientation_name()

        last_reward = self.stm.get_memory('current_reward') or 0.0
        self.stm.add_memory(reward, 'current_reward')
        self.stm.add_memory(last_reward, 'last_reward')
        last_position = self.stm.get_memory('current_position') or self.spatial_memory.position
        self.stm.add_memory(self.spatial_memory.position, 'current_position')
        self.stm.add_memory(last_position, 'last_position')
        self.stm.add_memory(orientation, 'current_orientation')

  
    def generate_new_actions(self, state_changes: list[str], communication_handler: CommunicationHandler) -> None:
        """
        Acts in the environment given the observations, the current plan and the current goals.
        Stores the actions sequence in the short term memory.
        """
        world_context = self.stm.get_memory('world_context')
        agent_bio_str = self.stm.get_memory('bio_str')
        current_plan = self.stm.get_memory('current_plan')
        valid_actions = self.stm.get_memory('valid_actions') 
        observations = self.stm.get_memory('current_observation') or 'None'
        current_goals = self.stm.get_memory('current_goals')
        
        # Generate new actions sequence and add it to the short term memory
        if isinstance(observations, list):
            observations = "\n".join(observations)
        #state_changes = '\n'.join(state_changes) if state_changes else 'None'
        previous_actions = self.stm.get_memory('previous_actions')
        previous_actions = f"You should consider that your previous actions were:  \n  -Action: {previous_actions[0]}: Reasoning: {previous_actions[1]}"
        known_trees = self.stm.get_memory('known_trees')
        known_trees = "These are the known trees: "+' '.join([f"tree {tree[0]} with center at {tree[1]}" for tree in known_trees]) if known_trees else "There are no known trees yet"
        percentage_explored = self.spatial_memory.get_percentage_known()
        prompt_path = os.path.join(self.prompts_folder, 'act.txt')
        prompt = load_prompt(prompt_path)
        prompt = replace_inputs_in_prompt(prompt, [self.name, world_context, current_plan, state_changes, observations, self.spatial_memory.position, 1, valid_actions, current_goals, agent_bio_str,
                                                   known_trees, percentage_explored, previous_actions])
        self.logger.info(f'Prompt: {prompt}')
        #gui.update_text(prompt)
        communication_handler.publish_data_topic_from_agent(self.agent_id, prompt)
        #user_action = input("What action would you like to perform? ")

        # Espera la acción del usuario desde 'topic/actions'
        while True:
            print(f"Waiting for action from {self.agent_id}")
            agent_id, user_action = communication_handler.get_next_action(timeout=None)
            if agent_id == self.agent_id:
                break
            else:
                # Ignora acciones que no son para este agente
                continue

        self.logger.info(f'User action: {user_action}')
        print(f"Received action: {user_action}")
        if not self.stm.get_memory('actions_sequence')  :
            self.stm.add_memory(Queue(), 'actions_sequence')
        if not self.stm.get_memory('current_steps_sequence')  :
            self.stm.add_memory(Queue(), 'current_steps_sequence')
            
        if user_action == 'not react' or user_action == "":
            self.logger.info(f'{self.name} decided to not react.')
            self.logger.info(f'The current action is {self.stm.get_memory("current_action")}')
            if self.stm.get_memory('current_action') is None:
                self.logger.info(f'{self.name} has no current action to follow.')
                user_action == "stay put"
            elif self.stm.get_memory('actions_sequence').empty():
                user_action = "stay put"
                print(f'{self.name} decided to stay put because the actions sequence is empty.')

            elif self.stm.get_memory('current_action') is not None:
                self.logger.info(f'{self.name} will continue with the current actions sequence.')
                return "not react"
        # If user decides to react, generate the new actions sequence
        self.logger.info(f'What action would you like to perform? {user_action}')
        actions_sequence_queue = self.stm.get_memory('actions_sequence')
        actions_sequence_queue.put(user_action)
        self.logger.info(f'{self.name} generated new actions sequence: {actions_sequence_queue.queue}')
        self.stm.add_memory(actions_sequence_queue, 'actions_sequence')

        return "react"