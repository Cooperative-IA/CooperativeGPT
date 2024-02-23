import argparse
from typing import List

def get_args():
    """
    Get the arguments for the simulation

    Returns:
        A list with the arguments for the simulation
    """

    parser = argparse.ArgumentParser(
        description="Arguments to run a simulation of LLMs reasoning architecture on Melting Pot"
    )

    parser.add_argument(
        "--substrate",
        type=str,
        default="commons_harvest_open",
        help="Name of the game to run, the name must match a folder in game_environment/substrates/python"
    )

    parser.add_argument(
        "--scenario",
        type=str,
        default="",
        help="Name of the scenario to run, the must be one of the predefined scenarios for the chosen game"
    )

    parser.add_argument(
        "--adversarial_event",
        type=bool,
        default=False,
        help="Whether to include adversarial events in the game. True/False"
    )
    
    parser.add_argument(
        "--world_context",
        type=str,
        default="detailed_context",
        help="Path to the world context file that contains the information about the game world and agents rules and objectives"
    )

    parser.add_argument(
        "--agents_bio_config",
        type=str,
        default="no_bio",
        help="Path to the agents bio config folder, basic valid options are: no_bio, all_coop, 2_coop_1_selfish, all_selfish"
    )

    parser.add_argument(
        "--record",
        type=bool,
        default=True,
        help="Whether to record the game. True/False"
    )

    parser.add_argument(
        "--llm_model",
        type=str,
        default='gpt-3.5',
        help="Which LLM model to use. Valid options are: gpt-3.5, gpt-3.5-16k, gpt-4" 
    )
    
    parser.add_argument(
        "--prompts_source",
        type=str,
        default='base_prompts_v0',
        help="Path to the prompts folder, some valid options are: base_prompts_v0, base_prompts_v1"
    )
    
    args = parser.parse_args()
    return args

