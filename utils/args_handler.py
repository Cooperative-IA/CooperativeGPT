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
        default="commons_harvest__open_0",
        help="Name of the scenario to run, the must be one of the predefined scenarios for the chosen game"
    )

    parser.add_argument(
        "--players",
        nargs='+',
        default=["Juan", "Laura", "Pedro"],
        help="List with the player names to run the game with"
    )

    parser.add_argument(
        "--agents_bio_config",
        type=str,
        default="no_bio",
        help="Path to the agents bio config folder, valid options are: no_bio, all_coop, 2_coop_1_selfish, all_selfish"
    )

    parser.add_argument(
        "--evaluate_with_bots",
        type=bool,
        default=False,
        help="Whether to evaluate the agents with bots or not"
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

    args = parser.parse_args()
    return args

