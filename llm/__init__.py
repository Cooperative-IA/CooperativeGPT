from llm.openai import GPT35
from llm.base_llm import BaseLLM

class LLMModels():
    """Class to define the available LLM models"""

    def __new__(self):
        """Constructor for the LLMModels class"""
        # Singleton pattern
        if not hasattr(self, 'instance'):
            self.instance = super(LLMModels, self).__new__(self)
            self.instance.llm_models = {
            "gpt-3.5": GPT35()
            }
            self.instance.main_model = "gpt-3.5"
        return self.instance

    def get_main_model(self) -> BaseLLM:
        """Get the main model
        Returns:
            BaseLLM: Main model
        """
        return self.llm_models[self.main_model]