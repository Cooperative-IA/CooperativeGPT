import os

from llm.base_llm import BaseLLM
import tiktoken
from groq import Groq
import groq


class Llama31_8B(BaseLLM):
    """Class for the GPT-4o mini model from OpenAI with 128K tokens of context"""

    def __init__(self):
        """Constructor for the class
        Args:
            prompt_token_cost (float): Cost of a token in the prompt
            response_token_cost (float): Cost of a token in the response
        """
        super().__init__(0.05/1e6, 0.08/1e6, 128000, 0.87)

        self.logger.info("Loading Llama3.1 8B model...")
        # Load the model
        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY"),
        )
        self.model_name = 'llama-3.1-8b-instant'
        # Encoding to estimate the number of tokens
        self.encoding = tiktoken.encoding_for_model("gpt-4o")
        
        self.logger.info("GPT-4o mini model loaded")

    def _format_prompt(self, prompt: str, role: str = 'user') -> list[dict[str, str]]:
        """Format the prompt to be used by the model
        Args:
            prompt (str): Prompt
        Returns:
            list: List of dictionaries containing the prompt and the role of the speaker
        """
        return [
            {"content": prompt, "role": role}
        ]

    def __completion(self, prompt: str, **kwargs) -> tuple[str, int, int]:
        """Completion api for the model
        Args:
            prompt (str): Prompt for the completion
        Returns:
            tuple(str, int, int): A tuple with the completed text, the number of tokens in the prompt and the number of tokens in the response
        """
        prompt = self._format_prompt(prompt)

        # Check if there is a system prompt
        if "system_prompt" in kwargs:
            system_prompt = self._format_prompt(kwargs["system_prompt"], role="system")
            prompt = system_prompt + prompt
            del kwargs["system_prompt"]


        response = self.client.chat.completions.create(model=self.model_name, messages=prompt, stream=False, **kwargs)
        completion = response.choices[0].message.content
        prompt_tokens = response.usage.prompt_tokens
        response_tokens = response.usage.completion_tokens
    
        return completion, prompt_tokens, response_tokens
    
    def _completion(self, prompt: str, **kwargs) -> tuple[str, int, int]:
        """Wrapper for the completion api with retry and exponential backoff
        
        Args:
            prompt (str): Prompt for the completion

        Returns:
            tuple(str, int, int): A tuple with the completed text, the number of tokens in the prompt and the number of tokens in the response
        """
        wrapper = BaseLLM.retry_with_exponential_backoff(self.__completion, self.logger, errors=(groq.RateLimitError))
        return wrapper(prompt, **kwargs)
    
    def _calculate_tokens(self, prompt: str) -> int:
        """Calculate the number of tokens in the prompt
        Args:
            prompt (str): Prompt
        Returns:
            int: Number of tokens in the prompt
        """
        
        num_tokens = 0
        num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
        num_tokens += len(self.encoding.encode(prompt))
        num_tokens += 2  # every reply is primed with <im_start>assistant
        return num_tokens