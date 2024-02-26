from llm.base_llm import BaseLLM

class Human(BaseLLM):
    """Class for human as LLM"""

    def __init__(self):
        """Constructor for the Human class
        Args:
            prompt_token_cost (float): Cost of a token in the prompt
            response_token_cost (float): Cost of a token in the response
        """
        super().__init__(0, 0, 100000, 1)

    def _completion(self, prompt: str, **kwargs) -> tuple[str, int, int]:
        """Completion api for the human LLM
        Args:
            prompt (str): Prompt for the completion
        Returns:
            tuple(str, int, int): A tuple with the completed text, the number of tokens in the prompt and the number of tokens in the response
        """

        # Check if there is a system prompt
        if "system_prompt" in kwargs:
            system_prompt = kwargs["system_prompt"] + "\n"
            prompt = system_prompt + prompt
            del kwargs["system_prompt"]

        # Get input from the command line
        response = input("Enter the response: ")
        completion = response
        prompt_tokens = self._calculate_tokens(prompt)
        response_tokens = self._calculate_tokens(completion)
    
        return completion, prompt_tokens, response_tokens
    
    def _calculate_tokens(self, prompt: str) -> int:
        """Calculate the number of tokens in the prompt
        Args:
            prompt (str): Prompt
        Returns:
            int: Number of tokens in the prompt
        """
        return len(prompt.split())