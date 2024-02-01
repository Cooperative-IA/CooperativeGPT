from llm import LLMModels
from utils.llm import extract_answers



def reflect_questions(name: str , world_context:str, statements: list[str]|str, agent_bio: str = "") -> list[str]:
    """
    Description: Returns the relevant questions for the agent given its name, the world context and the statements

    Args:
        name (str): Name of the agent
        world_context (str): World context
        statements (list[str]|str): Statements

    Returns:
        list[str]: Relevant questions for the agent
    """

    if isinstance(statements, list):
        statements = "\n".join(statements)

    llm = LLMModels().get_longer_context_fallback()
    try:
        response = llm.completion(prompt='reflect_questions.txt', inputs=[name, world_context, statements, agent_bio])
        relevant_questions_dict = extract_answers(response)
        relevant_questions = [q['Question'] for q in relevant_questions_dict.values()]
    except ValueError as e:
        if str(e) == 'Prompt is too long':
            llm = LLMModels().get_longer_context_fallback()
            response = llm.completion(prompt='reflect_questions.txt', inputs=[name, world_context, statements, agent_bio])
            relevant_questions_dict = extract_answers(response)
            relevant_questions = [q['Question'] for q in relevant_questions_dict.values()]
        else:
            raise e
   
    return relevant_questions



def reflect_insights(name, world_context, memory_statements, questions: list[str], agent_bio: str = "") -> list[str]:
    """
    Description: Returns the insights for the agent given its name, the world context and the memory statements
    
    Args:
        name (str): Name of the agent
        world_context (str): World context
        memory_statements (list[str]): Memory statements
        questions (list[str]): List of questions, one for each group of statements
        agent_bio (str, optional): Agent bio. Defaults to "".
    
    Returns:
        list[str]: Insights for the agent
    """

    llm = LLMModels().get_main_model()
    memory_statements = list_statements_to_string(memory_statements, questions)
    try:
        response = llm.completion(prompt='reflect_insight.txt', inputs=[name, world_context, memory_statements, agent_bio])
        insights_dict = extract_answers(response)
        insights = [i['Insight'] for i in insights_dict.values()]
    except ValueError as e:
        if str(e) == 'Prompt is too long':
            llm = LLMModels().get_longer_context_fallback()
            response = llm.completion(prompt='reflect_insight.txt', inputs=[name, world_context, memory_statements, agent_bio])
            insights_dict = extract_answers(response)
            insights = [i['Insight'] for i in insights_dict.values()]
        else:
            raise e
   
    return insights


def list_statements_to_string (list_statements: list[str], questions: list[str]) -> str:
    """
    Description: Converts a list of statements to a string

    Args:
        list_statements (list[str]): List of statements
        questions (list[str]): List of questions for each group of statements

    Returns:
        str: String of statements
    """
    statements = ''
    complement = 'here is a list of memories that might be helpful to answer the question:\n'
    for i, statement in enumerate(list_statements):
        statements += f"Question {i+1}: {questions[i]} {complement}{statement}\n\n"
    return statements