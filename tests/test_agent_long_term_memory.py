from dotenv import load_dotenv

from agent.memory_structures.long_term_memory import LongTermMemory

# load environment variables
load_dotenv(override=True)

def test_add_memory():
    ltm = LongTermMemory('test_agent', 'data')

    memory = 'This is a test memory'
    created_at = 'step 1'
    poignancy = 10
    ltm.add_memory(memory, created_at, poignancy)
    memories = ltm.get_memories()
    assert memory in memories['documents'], f'The memory {memory} is not in the memories'
    assert memories['metadatas'][0]['created_at'] == created_at, f'The created_at of the memory {memory} is not correct'
    assert memories['metadatas'][0]['poignancy'] == poignancy, f'The poignancy of the memory {memory} is not correct'

    # Add single memory with additional metadata
    memory = 'This is a test memory'
    created_at = 'step 1'
    poignancy = 10
    additional_metadata = {'test': 'test'}
    ltm.add_memory(memory, created_at, poignancy, additional_metadata)
    memories = ltm.get_memories()
    assert memory in memories['documents'], f'The memory {memory} is not in the memories'
    assert memories['metadatas'][0]['created_at'] == created_at, f'The created_at of the memory {memory} is not correct'
    assert memories['metadatas'][0]['poignancy'] == poignancy, f'The poignancy of the memory {memory} is not correct'
    assert memories['metadatas'][0]['test'] == additional_metadata['test'], f'The additional metadata of the memory {memory} is not correct'

    memory = ['This is a test memory', 'This is another test memory']
    created_at = ['step 1', 'step 2']
    poignancy = [10, 20]
    ltm.add_memory(memory, created_at, poignancy)
    memories = ltm.get_memories()
    assert memory[0] in memories['documents'], f'The memory {memory[0]} is not in the memories'
    assert memory[1] in memories['documents'], f'The memory {memory[1]} is not in the memories'
    assert memories['metadatas'][1]['created_at'] == created_at[0], f'The created_at of the memory {memory[0]} is not correct'
    assert memories['metadatas'][1]['poignancy'] == poignancy[0], f'The poignancy of the memory {memory[0]} is not correct'
    assert memories['metadatas'][0]['created_at'] == created_at[1], f'The created_at of the memory {memory[1]} is not correct'
    assert memories['metadatas'][0]['poignancy'] == poignancy[1], f'The poignancy of the memory {memory[1]} is not correct'

    # Add multiple memories with the same metadata
    memory = ['This is a test memory', 'This is another test memory']
    created_at = 'step 1'
    poignancy = 10
    ltm.add_memory(memory, created_at, poignancy)
    memories = ltm.get_memories()
    assert memory[0] in memories['documents'], f'The memory {memory[0]} is not in the memories'
    assert memory[1] in memories['documents'], f'The memory {memory[1]} is not in the memories'
    assert memories['metadatas'][1]['created_at'] == created_at, f'The created_at of the memory {memory[0]} is not correct'
    assert memories['metadatas'][1]['poignancy'] == poignancy, f'The poignancy of the memory {memory[0]} is not correct'
    assert memories['metadatas'][0]['created_at'] == created_at, f'The created_at of the memory {memory[1]} is not correct'
    assert memories['metadatas'][0]['poignancy'] == poignancy, f'The poignancy of the memory {memory[1]} is not correct'

    # Add multiple memories with additional metadata
    memory = ['This is a test memory', 'This is another test memory']
    created_at = 'step 1'
    poignancy = 10
    additional_metadata = [{'test': 'test1'}, {'test': 'test2'}]
    ltm.add_memory(memory, created_at, poignancy, additional_metadata)
    memories = ltm.get_memories()
    assert memory[0] in memories['documents'], f'The memory {memory[0]} is not in the memories'
    assert memory[1] in memories['documents'], f'The memory {memory[1]} is not in the memories'
    assert memories['metadatas'][1]['created_at'] == created_at, f'The created_at of the memory {memory[0]} is not correct'
    assert memories['metadatas'][1]['poignancy'] == poignancy, f'The poignancy of the memory {memory[0]} is not correct'
    assert memories['metadatas'][0]['created_at'] == created_at, f'The created_at of the memory {memory[1]} is not correct'
    assert memories['metadatas'][0]['poignancy'] == poignancy, f'The poignancy of the memory {memory[1]} is not correct'
    assert memories['metadatas'][1]['test'] == additional_metadata[0]['test'], f'The additional metadata of the memory {memory[0]} is not correct'
    assert memories['metadatas'][0]['test'] == additional_metadata[1]['test'], f'The additional metadata of the memory {memory[1]} is not correct'

def test_get_relevant_memories():
    ltm = LongTermMemory('test_agent', 'data')

    memory = ['This is a test memory', 'This is another test memory']
    created_at = 'step 1'
    poignancy = 10
    ltm.add_memory(memory, created_at, poignancy)
    relevant_memories = ltm.get_relevant_memories('test')
    assert memory[0] in relevant_memories, f'The memory {memory[0]} is not in the relevant memories'
    assert memory[1] in relevant_memories, f'The memory {memory[1]} is not in the relevant memories'

    memory = ['This is a test memory', 'This is another test memory']
    created_at = 'step 1'
    poignancy = 10
    ltm.add_memory(memory, created_at, poignancy)
    relevant_memories = ltm.get_relevant_memories('test', return_metadata=True)
    assert memory[0] in relevant_memories[0], f'The memory {memory[0]} is not in the relevant memories'
    assert memory[1] in relevant_memories[0], f'The memory {memory[1]} is not in the relevant memories'
    assert relevant_memories[1][0]['created_at'] == created_at, f'The created_at of the memory {memory[0]} is not correct'
    assert relevant_memories[1][0]['poignancy'] == poignancy, f'The poignancy of the memory {memory[0]} is not correct'
    assert relevant_memories[1][1]['created_at'] == created_at, f'The created_at of the memory {memory[1]} is not correct'
    assert relevant_memories[1][1]['poignancy'] == poignancy, f'The poignancy of the memory {memory[1]} is not correct'

    # Test filter
    memory = ['This is a test memory 1', 'This is another test memory 2']
    created_at = ['step 2', 'step 1']
    poignancy = [10, 10]
    ltm.add_memory(memory, created_at, poignancy)
    relevant_memories = ltm.get_relevant_memories('test', filter={'created_at': 'step 1'})
    assert memory[1] in relevant_memories, f'The memory {memory[1]} is not in the relevant memories'
    assert memory[0] not in relevant_memories, f'The memory {memory[0]} is in the relevant memories'

    