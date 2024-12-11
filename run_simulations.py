import subprocess
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime

def run_simulation(simulation_id, start_delay):
    time.sleep(start_delay)  # Delay for the staggered start time
    command = [
        "python", "main.py",
        # "--substrate=externality_mushrooms",
        "--scenario=commons_harvest__open_0",
        "--agents_bio_config=no_bio",
        # "--cot_agent=True",
        "--world_context=world_info_v2",
        # "--llm_model=gpt-3.5",
        f"--simulation_id=sim_prueba_{str(simulation_id).format(2)}",
    ]
    subprocess.run(command)

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
