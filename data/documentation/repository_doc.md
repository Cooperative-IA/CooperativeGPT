# Enhanced Architecture Documentation

This document provides a comprehensive overview of the architecture behind the Cooperative AI project. It delves into the code structure, delineates the various modules and their interrelations, and outlines the project's distinct components.

## Overview of the Main Script

The main script serves as the gateway to the simulation, orchestrating the setup and execution of the environment. It encompasses several critical steps:

1. **Argument Parsing**: The script begins by interpreting the simulation parameters provided by the user.
2. **Logging Setup**: A logging system is established to record the simulation's progress and any noteworthy events.
3. **Data Loading**: It loads essential data, including world context, agent details, and substrate information, laying the groundwork for the simulation.
4. **Agent Creation**: Individual agents are instantiated, each with its unique attributes and objectives.
5. **Simulation Environment Initialization**: The script initiates the simulation environment through the `start_server` function within the `server.py` file. This involves:
    - 5.1. Utilizing `level_playing_utils.py` from the `game_environment` folder as a primary interface to the simulation environment.
    - 5.2. Importing and setting up the game using the provided substrate name.
    - 5.3. Generating bots based on the scenario and their properties.
    - 5.4. Creating the game environment (`game_env`) by passing necessary parameters to the `level_playing_utils.Game()` constructor. Further details on this file are provided in subsequent sections.
6. **Language Model Handler Setup**: A handler for Language Models, referred to as `llm`, is instantiated using the `LLMModels` class from the `llm` package. This step involves loading:
    - A main model for general requests (defaulting to GPT-3.5).
    - A model for requests requiring extended context (defaulting to GPT-3.5_16K).
    - A specialized model for certain modules (typically GPT-3.5, with the possibility of using GPT-4).
7. **Game Loop Execution**: The `game_loop` function is invoked with the agents as parameters, marking the commencement of the simulation. This process includes:
    - 7.1. Starting the game and receiving initial environmental observations through the `env.step(actions)` call.
    - 7.2. Continuously running the game loop until the maximum number of rounds is reached.
    - 7.3. Sequentially allowing each agent to take their turn, which involves:
        - 7.3.1. Acquiring accumulated observations for the agent via `env.get_observations_by_player(agent.name)`.
        - 7.3.2. Passing these observations to the agent's `move` function. Depending on the scenario, the agent either:
            - a. Executes its move, completing its turn and generating step actions.
            - b. Is preempted by another agent but eventually takes its turn after all module processes except action execution are completed.
        - 7.3.3. Executing the `env.step` function with the `actions` variable, which is updated for the current agent by the `generate_agent_actions_map` function. This translates textual commands into game actions.
    - 7.4 Resetting the actions map for the current agent before proceeding to the next agent's turn.
    - 7.5 Detailed explanations of the `agent.move` function and agent script are provided in the following sections.

## Agent Script Functionality

The `agent` package is the handler for agent operations within the simulation. It is responsible for agent instantiation and managing the architectural modules. The workflow includes:

- *Constructor Initialization:* The agent is initialized with its attributes and other parameters requiered for the architecture workflow are set up. Also the 3 kind of memory are initialized: short-term, long-term and spatial memory. You can find a description for each one below.

### Move Function

The `move` function is the core of the agent's decision-making process. Use all the congnitive sequence of the agent to decide an action to take.
Note: If cooperative parameter is set to True, the agent will use the cooperative decision-making process by executing `move_cooperative` function.

This function follows the next steps:

1. Updates Spatial Memory: The agent updates its spatial memory with the current observations, agent position and orientation
2. Perceive: By calling the `perceive` function, the agent executes the perception module (explained below). This module will indicates if agent have to react or not to the current observations.
3. If agent have to react, he will execute all the processes associated to Planification and Actuation modules, it will update `step_actions`. 
4. Reflect: Agent will call the Reflect module by using filtered_observations.
5. The step_actions queue is retrieved and returned (note that if Step 3. ocurred, it will be new actions in the queue).


### Modules
Each mentioned module on move function, has its own class and methods. They are in charge to retrieve from Short-term memory and Long-term memory the needed information to execute each module. By passing this information to each module, the modules are able to create the determinated prompt to send to the language model. And each module can extract requiered information as a .json format.