import re

def filter_log_by_agent(log: str, step_init: int = 0, step_end: int = 0) -> dict:
    """
    Filtra los registros de un log por agente y rango de pasos.

    Args:
        log (str): Texto del log a procesar.
        step_init (int): Número de paso inicial para el filtro.
        step_end (int): Número de paso final para el filtro.

    Returns:
        dict: Un diccionario con dos claves: 'log_by_agent', que contiene los logs filtrados por nombre de agente,
              y 'agents_scenes_description', que contiene las descripciones de las escenas por agente.
    """
    # Dividir el texto por agentes
    bloques = re.split(r"################Agent's ", log)[1:]
    log_by_agent = {}
    agents_scenes_description = {}
    print(len(bloques) )
    for bloque in bloques:
        nombre_agente, info = bloque.split(" turn##############", 1)
        nombre_agente = nombre_agente.strip()
        splitted_info = info.split("\n")
        scene_description = {}
        try:
            # Intentar extraer y evaluar la descripción de la escena segura
            third_line = splitted_info[2]
            scene_description_str = third_line.split("Scene descriptions: ")[1]
            scene_description = eval(scene_description_str)
        except (IndexError, SyntaxError):
            pass

        # Extraer cambios observados en el entorno
        changes = []
        for line in splitted_info:
            if "Since then, the following changes in the environment have been observed:" in line:
                index = splitted_info.index(line) + 1
                while index < len(splitted_info) and "I can currently observe the following:" not in splitted_info[index]:
                    try:
                        change, timestamp = splitted_info[index].split(" At ")
                    except:
                        change = splitted_info[index]
                        timestamp = ""
                    changes.append((change, timestamp))
                    index += 1
                scene_description["observed_changes"] = changes
                break
        
        if step_init != 0 and step_end != 0:
            step_number = int(re.search(r"step_(\d+)", info).group(1))
            if not (step_init <= step_number <= step_end):
                continue
        
        lista_previa = log_by_agent.get(nombre_agente, [])
        lista_previa.append(info)
        log_by_agent[nombre_agente] = lista_previa
        
        list_scenes = agents_scenes_description.get(nombre_agente, [])
        list_scenes.append(scene_description)
        agents_scenes_description[nombre_agente] = list_scenes


    return {'log_by_agent': log_by_agent, 'agents_scenes_description': agents_scenes_description}



def get_modules_answer_given_prompt (turn_log:str, agent_name:str, prompts_folder:str) -> str:
    """
    Get the answer of a given module from a turn log
    
    Args:
    - turn_log: str, log of a turn
    Returns:
    - str, answer of the module
    - agent_name: str, name of the agent
    - prompts_folder: str, path to the folder with the prompts
    """
        # Define the start and end patterns
        # Define the start and end patterns
    start_pattern = re.escape("- INFO - llm.base_llm - Prompt: You have this information about an agent called")
    end_pattern = re.escape("- INFO - llm.base_llm - Prompt tokens:")
    
    # Pattern to match the entire segment from start to end
    pattern = f"({start_pattern}.*?{end_pattern})"
    
    # Find all matches
    matches = re.findall(pattern, turn_log, flags=re.DOTALL)
    
    modules_key_strings ={
        "react": "",
        "plan": "",
        "reflect_questions": "",
        "reflect_insight": "",
        "act": ""
    }
    # Now we are extracting the value for the dict modules_key_strings from the prompt that is in the prompt folder
    for key in modules_key_strings.keys():
        with open(f"{prompts_folder}/{key}.txt", "r") as f:

            modules_key_strings[key] = '\n'.join(f.read().split("\n")[-3:])
            if key == "plan":
                modules_key_strings[key] = modules_key_strings[key].replace("<input1>", agent_name)

            
    print(modules_key_strings)
    answers_per_module = {module_key:[] for module_key in modules_key_strings.keys()}
    
    
    for match in matches:
        for module_key, module_string in modules_key_strings.items():
            if module_string in match:
                answers_per_module[module_key].append(match)

    return answers_per_module
    



# Read log of a given agent and separate the answers from each kind of module from the log
def separate_modules_answers_from_log (agent_log_path:str, agent_name, prompts_folder:str) -> dict[str, list[str]]:
    """
    Read the log of a given agent and separate the answers from each kind of module from the log
    
    Args :
    - agent_log_path: str, path to the log of the agent
    - agent_name: str, name of the agent
    - prompts_folder: str, path to the folder with the prompts
    Returns:
    - dict[str, list[str]], dictionary with the answers from each kind of module
    """
    with open(agent_log_path, 'r') as f:
        agent_log = f.read()
    #agent_log = agent_log.split("########## NEW TURN ##########\n\n")
    
    # Separate the answers from each kind of module from the log
    answers_per_module = get_modules_answer_given_prompt(agent_log, agent_name, prompts_folder)
    return answers_per_module
