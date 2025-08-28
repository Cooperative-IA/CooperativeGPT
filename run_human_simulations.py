import subprocess
import time
from datetime import datetime
def run_simulation(simulation_id, person_name, substrate_input, port):
    # First we run a command to copy the world_context file into a new one with the same name but with the simulation_id
    substrate = substrate_input
    if substrate in ["externality_mushrooms", "coins_original"]:
        world_context_name = "definitions"
        new_world_context_name = f"{world_context_name}_{str(simulation_id).format(2)}"
        world_context_path = f"data/defined_experiments/{substrate}/world_context/{world_context_name}.txt"
        new_world_context_path = f"data/defined_experiments/{substrate}/world_context/{new_world_context_name}.txt"

        subprocess.run(["cp", world_context_path, new_world_context_path])
    command_mushrooms = [
        "python", "main_human__arrows_mov.py",
        "--substrate=externality_mushrooms",
        "--scenario=externality_mushrooms__dense_1",
        "--agents_bio_config=no_bio_1p_4b",
        "--world_context=definitions",
        "--llm_model=gpt-4o-mini",
        f"--simulation_id={person_name}__{str(simulation_id).format(2)}",
        f"--port={port}",
    ]
    command_coins = [
        "python", "main_human__arrows_mov.py",
        "--substrate=coins_original",
        "--scenario=coins_1",
        "--agents_bio_config=1_human_1_bot",
        "--world_context=definitions",
        "--llm_model=gpt-4o-mini",
        f"--simulation_id={person_name}__{str(simulation_id).format(2)}",
        f"--port={port}",
    ]
    
    command_commons_harvest = [
        "python", "main_human__arrows_mov.py",
        "--substrate=commons_harvest_open",
        "--scenario=commons_harvest__open_0",
        "--agents_bio_config=no_bio_5h",
        "--world_context=context_with_definitions",
        "--llm_model=gpt-4o-mini",
        f"--simulation_id={person_name}__{str(simulation_id).format(2)}",
        f"--port={port}",
        ]
    command_commons_harvest_adversarial = [
        "python", "main_human__arrows_mov.py",
        "--substrate=commons_harvest_open___adversarial",
        "--scenario=commons_harvest__open_adversarial_0",
        "--agents_bio_config=resilience_2_humans_1_bot",
        "--world_context=context_with_definitions",
        "--llm_model=gpt-4o-mini",
        f"--simulation_id={person_name}__{str(simulation_id).format(2)}",
        f"--port={port}",
        ]
    
    command = command_coins if substrate_input == "coins_original" else command_mushrooms if substrate_input == "externality_mushrooms" else command_commons_harvest if substrate_input == "commons_harvest_open" else command_commons_harvest_adversarial
    subprocess.run(command)


def handle_adversarial_experiments(person_name, substrate_input, port, is_copy, simulations_start_from):
    experiments = [
        {
            "simulation_id": 1,
            "events_times": [250],
            "events_magnitude": 0.3
        },
        {
            "simulation_id": 2,
            "events_times": [50, 250],
            "events_magnitude": 0.3
        },
        {
            "simulation_id": 3,
            "events_times": [50, 250, 400],
            "events_magnitude": 0.3
        },
        {
            "simulation_id": 4,
            "events_times": [250],
            "events_magnitude": 0.5
        },
        {
            "simulation_id": 5,
            "events_times": [50, 250],
            "events_magnitude": 0.5
        },
        {
            "simulation_id": 6,
            "events_times": [50, 250, 400],
            "events_magnitude": 0.5
        },
        {
            "simulation_id": 7,
            "events_times": [250],
            "events_magnitude": 0.7
        },
        {
            "simulation_id": 8,
            "events_times": [50, 250],
            "events_magnitude": 0.7
        },
        {
            "simulation_id": 9,
            "events_times": [50, 250, 400],
            "events_magnitude": 0.7
        }
    ]

    experiments = [
	{
	    "simulation_id":1,
	    "events_times":[1000],
            "events_magnitude": 0.00001
	}
    ]
    for experiment in experiments[simulations_start_from - 1:]:
        simulation_id = experiment["simulation_id"]
        events_times = experiment["events_times"]
        events_magnitude = experiment["events_magnitude"]
        
        start_variables_path = 'config/start_variables.txt' if not is_copy else 'config/start_variables_copy.txt'
        # Write to config/start_variables.txt
        with open(start_variables_path, 'w') as f:
            f.write(str({
                'events_times': events_times,
                'events_magnitude': events_magnitude
            }) + '\n')
        
        num_events = len(events_times)
        magnitude = events_magnitude
        simulation_name = f"{simulation_id}__{num_events}evs__{magnitude}mag"
        print(f"Starting simulation {simulation_name}")
        run_simulation(simulation_name, person_name, substrate_input, port)
        print(f"Completed simulation {simulation_name}")


def main(simulations_count, person_name, substrate_input, port, simulations_start_from=1):
    start_timestamp = datetime.now()
    print(f"The first simulation started at: {start_timestamp}")

    
    if "commons_harvest_open___adversarial" in substrate_input:
        is_copy = True if "copy" in substrate_input else False
        handle_adversarial_experiments(person_name, substrate_input, port, is_copy, simulations_start_from)
    else:
        # Run simulations sequentially
        for i in range(1, simulations_count + 1):
            print(f"Starting simulation {i}")
            run_simulation(i, person_name, substrate_input, port)
            print(f"Completed simulation {i}")

    print("All simulations have been completed.")
    
    
    

def _menu_commons_harvest_open___adversarial(substrate: str):
    
    sub_group = 1
    while True:
        try:
            sub_group = int(input("\nEnter the sub-group number, either 1 or 2 or 3: "))
            if sub_group in [1, 2, 3]:
                if sub_group == 2:
                    substrate = "commons_harvest_open___adversarial_copy"
                elif sub_group == 3:
                    substrate = "commons_harvest_open___adversarial_copy_2"
                break
            print("Please enter a valid sub-group number.")
        except ValueError:
            print("Please enter a valid number.")
            


    
    port = 8084 if sub_group == 1 else 8085 if sub_group == 2 else 8083
    
    # Nine adversarial experiments
    simulations_count = 9
    
    # Ask if want to start from specific simulation
    simulations_start_from = 1
    start_from_specific = input("\nStart from specific simulation? (y/n): ").lower() == 'y'
    if start_from_specific:
        while True:
            try:
                simulations_start_from = int(input("\nEnter simulation number (1-9): "))
                if 1 <= simulations_start_from <= 9:
                    break
                print("Please enter a number between 1 and 9.")
            except ValueError:
                print("Please enter a valid number.")
    
    communication_mode = None
    while True:
        try:
            communication_mode = int(input("\nEnter the communication mode, either 1 or 2:\n 1. Communication\n 2.WITHOUT Communication\n"))
            if communication_mode in [1, 2]:
                if communication_mode == 1:
                    communication_mode = "communication"
                else:
                    communication_mode = ""
                break
            print("Please enter a valid communication mode.")
        except ValueError:
            print("Please enter a valid communication mode.")
            
            
    current_date = datetime.now().strftime("%B_%d")
    group_name = f"commons_harvest_open_adversarial__{communication_mode}__group_{current_date}__subgroup_{sub_group}"
    
    
    return substrate, group_name, port, simulations_count, communication_mode, simulations_start_from

def _menu_commons_harvest_open(substrate: str):
     
    simulations_count = None    
    while True:
        try:
            simulations_count = int(input("\nEnter the number of simulations to run: "))
            if simulations_count > 0:
                break
            print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")
        
    kind_experiment = None
    while True:
        try:
            kind_experiment = int(input("\nEnter the kind of experiment, either 1 or 2:\n 1. Cooperative\n 2. Selfish\n"))
            if kind_experiment in [1, 2]:
                break
            print("Please enter a valid kind of experiment.")
        except ValueError:
            print("Please enter a valid kind of experiment.")
    
    communication_mode = None
    while True:
        try:
            communication_mode = int(input("\nEnter the communication mode, either 1 or 2:\n 1. Communication\n 2.WITHOUT Communication\n"))
            if communication_mode in [1, 2]:
                break
            print("Please enter a valid communication mode.")
        except ValueError:
            print("Please enter a valid communication mode.")
    
    current_date = datetime.now().strftime("%B_%d")
    group_name = f"commons_harvest_open__{communication_mode}___{kind_experiment}__group_{current_date}"
    
    # Define port 8081
    port = 8084
    
    return substrate, group_name, port, simulations_count

def _menu_externality_mushrooms__and__coins_original(substrate: str):
    
    simulations_count = None    
    while True:
        try:
            simulations_count = int(input("\nEnter the number of simulations to run: "))
            if simulations_count > 0:
                break
            print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")
    
    kind_experiment = None
    while True:
        try:
            kind_experiment = int(input("\nEnter the kind of experiment, either 1 or 2:\n 1. Cooperative\n 2. Selfish\n"))
            if kind_experiment in [1, 2]:
                break
            print("Please enter a valid kind of experiment.")
        except ValueError:
            print("Please enter a valid kind of experiment.")
    
    person_name = None
    while True:
        try:
            person_name = input("\nEnter the person name: ")
            if person_name:
                break
            print("Please enter a valid person name.")
        except ValueError:
            print("Please enter a valid person name.")
    current_date = datetime.now().strftime("%B_%d")
    group_name = f"{substrate}__{kind_experiment}__group_{current_date}__{person_name}"
    
    available_ports = [8081, 8082, 8083, 8084, 8085]
    
    port = None
    while True:
        try:
            print("\nChoose a port number from the following options:")
            for i, p in enumerate(available_ports, start=1):
                print(f" {i}. Press {i} to use port {p}")
            choice = int(input("Enter the number corresponding to your choice: "))
            if 1 <= choice <= len(available_ports):
                port = available_ports[choice - 1]
                break
            print(f"Please choose a valid option number between 1 and {len(available_ports)}.")
        except ValueError:
            print("Please enter a valid option number.")
            
    return substrate, group_name, port, simulations_count   



    
    
if __name__ == "__main__":

    import os
    import torch
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"

    # Usar GPU si está disponible
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print("\n=== Human Simulation Configuration ===")
    print("\nAvailable substrates:")
    print("1. Coins")
    print("2. Mushrooms") 
    print("3. Commons Harvest")
    print("4. Commons Harvest Adversarial")
    while True:
        substrate_choice = input("\nSelect substrate (1-4): ")
        if substrate_choice in ['1', '2', '3', '4']:
            break
        print("Invalid choice. Please select 1, 2, 3 or 4.")
    
    substrate = "coins_original" if substrate_choice == '1' else "externality_mushrooms" if substrate_choice == '2' else "commons_harvest_open" if substrate_choice == '3' else "commons_harvest_open___adversarial"
    
    if "commons_harvest_open___adversarial" in substrate:
        substrate, group_name, port, simulations_count, communication_mode, simulations_start_from = _menu_commons_harvest_open___adversarial(substrate)
    elif substrate == "commons_harvest_open":
        simulations_start_from = 1
        substrate, group_name, port, simulations_count = _menu_commons_harvest_open(substrate)
    else:
        simulations_start_from = 1
        substrate, group_name, port, simulations_count = _menu_externality_mushrooms__and__coins_original(substrate)

     
    print(f"\nStarting {simulations_count} simulation(s) for {group_name} on {substrate} substrate using port {port} ...")
    main(simulations_count, group_name, substrate, port, simulations_start_from)


