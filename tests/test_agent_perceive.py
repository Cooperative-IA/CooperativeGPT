from agent.memory_structures.short_term_memory import ShortTermMemory
from agent.cognitive_modules.perceive import update_known_agents

stm = ShortTermMemory()

def test_update_known_agents():
    observations = ['Observed agent Manuel at position [3, 4]']
    update_known_agents(observations, stm)
    known_agents = stm.get_known_agents()
    assert 'Manuel' in known_agents, "The agent Manuel is not in the known agents"

    observations = ['Observed agent Manuel at position [3, 4]', 'Observed agent Juan at position [5, 6]']
    update_known_agents(observations, stm)
    known_agents = stm.get_known_agents()
    assert 'Juan' in known_agents, "The agent Juan is not in the known agents"
    assert len(known_agents) == 2, "The number of known agents is not 2"
