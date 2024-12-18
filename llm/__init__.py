from llm.openai import GPT4oMini, GPT4o, Embedding
# from llm.groq import Llama31_8B
from llm.friendli import Llama31_8B, Llama31_70B
from llm.base_llm import BaseLLM

class LLMModels():
    """Class to define the available LLM models"""

    def __new__(self):
        """Constructor for the LLMModels class"""
        # Singleton pattern
        if not hasattr(self, 'instance'):
            self.instance = super(LLMModels, self).__new__(self)
            self.instance.llm_models: dict[str, BaseLLM] = {
            # "llama3.1-8B": Llama31_8B(),
            # "llama3.1-70B": Llama31_70B(),
            # "gpt-4o": GPT4o(),
            "gpt4o-mini": GPT4oMini(),
            "embedding": Embedding()
            }
            self.instance.main_model = "gpt4o-mini"
            self.instance.best_model = "gpt4o-mini"
            self.instance.longer_context_fallback = "gpt4o-mini"
            self.instance.embedding_model = "embedding"
        return self.instance

    def get_main_model(self) -> BaseLLM:
        """Get the main model
        Returns:
            BaseLLM: Main model
        """
        return self.llm_models[self.main_model]
    
    def get_embedding_model(self) -> BaseLLM:
        """Get the embedding model
        Returns:
            BaseLLM: Embedding model
        """
        return self.llm_models[self.embedding_model]
    
    def get_longer_context_fallback(self) -> BaseLLM:
        """Get the longer context fallback model
        Returns:
            BaseLLM: Longer context fallback model
        """
        return self.llm_models[self.longer_context_fallback]
    
    def get_best_model(self) -> BaseLLM:
        """Get the best model
        Returns:
            BaseLLM: Best model
        """
        return self.llm_models[self.best_model]
    
    def get_costs(self) -> dict:
        """Get the costs of the models
        Returns:
            dict: Costs of the models
        """
        costs = {}
        total_cost = 0
        for model_name, model in self.llm_models.items():
            model_cost = model.cost_manager.get_costs()['total_cost']
            costs[model_name] = model_cost
            total_cost += model_cost

        costs['total'] = total_cost

        return costs
    
    def get_tokens(self) -> dict:
        """Get the tokens used by the models
        Returns:
            dict: Tokens used by model
        """
        tokens = {}
        total_tokens = 0
        for model_name, model in self.llm_models.items():
            model_tokens = model.cost_manager.get_tokens()['total_tokens']
            tokens[model_name] = model_tokens
            total_tokens += model_tokens

        tokens['total'] = total_tokens

        return tokens