from llm import LLMModels
from utils.llm import extract_answers



def reflect_questions(name: str , world_context:str, statements: str) -> list[str]:
    
    llm = LLMModels().get_main_model()
    response = llm.completion(prompt='reflect_questions.txt', inputs=[name, world_context, statements])
    relevant_questions_dict = extract_answers(response)
    relevant_questions = [q['Question'] for q in relevant_questions_dict.values()]
    return relevant_questions



def reflect_insights(name, world_context, memory_statements):
    
    llm = LLMModels().get_main_model()
    response = llm.completion(prompt='reflect_insight.txt', inputs=[name, world_context, memory_statements])
    insights_dict = extract_answers(response)
    insights = [i['Insight'] for i in insights_dict.values()]
    return insights