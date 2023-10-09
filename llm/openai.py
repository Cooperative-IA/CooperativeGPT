import os

from llm.base_llm import BaseLLM
import openai
import tiktoken

class GPT35(BaseLLM):
    """Class for the GPT-3.5 turbo model from OpenAI with 4000 tokens of context"""

    def __init__(self):
        """Constructor for the GPT35 class
        Args:
            prompt_token_cost (float): Cost of a token in the prompt
            response_token_cost (float): Cost of a token in the response
        """
        super().__init__(0.0015/1000, 0.002/1000, 4000, 0.7)

        self.logger.info("Loading GPT-3.5 model...")
        # Load the GPT-3.5 model
        openai.api_key = os.getenv("AZURE_OPENAI_KEY_GPT3")
        openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT_GPT3")
        openai.api_type = os.getenv("OPENAI_API_TYPE")
        openai.api_version = os.getenv("OPENAI_API_VERSION")
        self.deployment_name = os.getenv("GPT_35_MODEL_ID")
        # Encoding to estimate the number of tokens
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        
        self.logger.info("GPT-3.5 model loaded")

    def _format_prompt(self, prompt: str, role: str = 'user') -> list[dict[str, str]]:
        """Format the prompt to be used by the GPT-3.5 model
        Args:
            prompt (str): Prompt
        Returns:
            list: List of dictionaries containing the prompt and the role of the speaker
        """
        return [
            {"content": prompt, "role": role}
        ]

    def _completion(self, prompt: str, **kwargs) -> tuple[str, int, int]:
        """Completion api for the GPT-3.5 model
        Args:
            prompt (str): Prompt for the completion
        Returns:
            tuple(str, int, int): A tuple with the completed text, the number of tokens in the prompt and the number of tokens in the response
        """
        prompt = self._format_prompt(prompt)
        response = openai.ChatCompletion.create(engine=self.deployment_name, messages=prompt, **kwargs)
        completion = response.choices[0].message.content
        prompt_tokens = response.usage.prompt_tokens
        response_tokens = response.usage.completion_tokens
        return completion, prompt_tokens, response_tokens
    
    def _calculate_tokens(self, prompt: str) -> int:
        """Calculate the number of tokens in the prompt
        Args:
            prompt (str): Prompt
        Returns:
            int: Number of tokens in the prompt
        """
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        num_tokens = 0
        num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
        num_tokens += len(encoding.encode(prompt))
        num_tokens += 2  # every reply is primed with <im_start>assistant
        return num_tokens