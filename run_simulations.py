import subprocess
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime

def run_simulation(simulation_id, start_delay):
    time.sleep(start_delay)  # Delay for the staggered start time
    # First we run a command to copy the world_context file into a new one with the same name but with the simulation_id
    substrate = "coins_original"
    world_context_name = "definitions"
    new_world_context_name = f"{world_context_name}_{str(simulation_id).format(2)}"
    world_context_path = f"data/defined_experiments/{substrate}/world_context/{world_context_name}.txt"
    new_world_context_path = f"data/defined_experiments/{substrate}/world_context/{new_world_context_name}.txt"
    
    subprocess.run(["cp", world_context_path, new_world_context_path])
    command = [
        "python", "main.py",
        "--substrate=coins_original",
        "--scenario=coins_1",
        "--agents_bio_config=1_human_1_bot",
        f"--world_context={new_world_context_name}",
        "--llm_model=gpt-4o",
        #"--cot_agent=True",
        #f"--simulation_id=coins1__gpt4o__{str(simulation_id).format(2)}",
    ]
    subprocess.run(command)
        #"--cot_agent=True",
        #f"--simulation_id=coins1__cotagent__gpt4o_mini__{str(simulation_id).format(2)}",
        #f"--simulation_id=coins1__cotagent__gpt4o__{str(simulation_id).format(2)}",
        #f"--simulation_id=coins1__gpt4o__{str(simulation_id).format(2)}",

def main(simulations_count):
    start_timestamp = datetime.now()
    print(f"The first simulation started at: {start_timestamp}")
    
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(run_simulation, i, i*5) for i in range(1, simulations_count + 1)]
        # Wait until all simulations are completed
        for future in futures:
            future.result()
    
    print("All simulations have been completed.")

if __name__ == "__main__":
    simulations_count = int(input("Enter the number of simulations to run: "))
    main(simulations_count)
