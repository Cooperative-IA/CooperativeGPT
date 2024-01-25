from llm.openai import GPT35, Ada, GPT35_16K, GPT4
from llm.base_llm import BaseLLM

class LLMModels():
    """Class to define the available LLM models"""

    def __new__(self):
        """Constructor for the LLMModels class"""
        # Singleton pattern
        if not hasattr(self, 'instance'):
            self.instance = super(LLMModels, self).__new__(self)
            self.instance.llm_models = {
            "gpt-3.5": GPT35(),
            "gpt-3.5-16k": GPT35_16K(),
            "gpt-4": GPT4(),
            "ada": Ada()
            }
            self.instance.main_model = "gpt-3.5"
            self.instance.best_model = "gpt-4"
            self.instance.longer_context_fallback = "gpt-3.5-16k"
            self.instance.embedding_model = "ada"
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