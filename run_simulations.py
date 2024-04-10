import subprocess
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime

def command_for_no_bio(simulation_id):
    return [
        "python", "main.py",
        "--substrate=commons_harvest_open",
        "--scenario=",
        "--agents_bio_config=no_bio",
        "--world_context=context_with_definitions",
        f"--simulation_id=sim_{str(simulation_id)}",
    ]

def command_for_no_bio_two_agents(simulation_id):
    return [
        "python", "main.py",
        "--substrate=commons_harvest_open",
        "--scenario=commons_harvest__open_0",
        "--agents_bio_config=no_bio_two_agents",
        "--world_context=context_with_definitions___mini_map",
        f"--simulation_id=sim_{str(simulation_id)}",
    ]
def command_for_all_coop(simulation_id):
    return [
        "python", "main.py",
        "--substrate=commons_harvest_open",
        "--scenario=",
        "--agents_bio_config=all_coop",
        "--world_context=context_with_definitions___mini_map",
        f"--simulation_id=sim_{str(simulation_id)}",
    ]
def command_for_all_coop_with_definition(simulation_id):
    return [
        "python", "main.py",
        "--substrate=commons_harvest_open",
        "--scenario=",
        "--agents_bio_config=all_coop_with_definition",
        "--world_context=context_with_definitions",
        f"--simulation_id=sim_{str(simulation_id)}",
    ]
def command_for_all_selfish(simulation_id):
    return [
        "python", "main.py",
        "--substrate=commons_harvest_open",
        "--scenario=",
        "--agents_bio_config=all_selfish",
        "--world_context=context_with_definitions___mini_map",
        f"--simulation_id=sim_{str(simulation_id)}",
    ]
def command_for_one_apple_per_tree(simulation_id):
    return [
        "python", "main.py",
        "--substrate=commons_harvest_open",
        "--scenario=",
        "--kind_experiment=personalized",
        "--agents_bio_config=no_bio",
        "--world_context=context_with_definitions",
        f"--simulation_id=sim_{str(simulation_id)}",
        "--start_from_scene=scene_one_apple_per_tree___no_memories",
    ]

def command_for_adversarial_round(simulation_id):
    return [
        "python", "main.py",
        "--substrate=commons_harvest_open",
        "--scenario=",
        "--kind_experiment=adversarial_round",
        "--agents_bio_config=no_bio",
        "--world_context=context_with_definitions",
        f"--simulation_id=RE1_sim_{str(simulation_id)}",
    ]

def command_for_bot_adversarial_round(simulation_id):
    return [
        "python", "main.py",
        "--substrate=commons_harvest_open",
        "--scenario=commons_harvest__open_0",
        "--kind_experiment=bot_adversarial_round",
        "--agents_bio_config=no_bio",
        "--world_context=context_with_definitions",
        f"--simulation_id=RBE1_sim_{str(simulation_id)}",
    ]



def run_simulation(simulation_id, start_delay):
    time.sleep(start_delay)  # Delay for the staggered start time
    ######  Choose here the command for the experiment   ######
    command = command_for_bot_adversarial_round(simulation_id)
    subprocess.run(command)

def main(simulations_count):
    start_timestamp = datetime.now()
    print(f"The first simulation started at: {start_timestamp}")
    
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(run_simulation, i, i*20) for i in range(1, simulations_count + 1)]
        # Wait until all simulations are completed
        for future in futures:
            future.result()
    
    print("All simulations have been completed.")

if __name__ == "__main__":
    simulations_count = int(input("Enter the number of simulations to run: "))
    main(simulations_count)
