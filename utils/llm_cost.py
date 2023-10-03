class CostManager():
    """Class for managing the cost of the LLMs apis"""
    def __init__(self, prompt_token_cost: float, response_token_cost: float):
        """Constructor for the CostManager class
        Args:
            prompt_token_cost (float): Cost of a token in the prompt
            response_token_cost (float): Cost of a token in the response
        """
        self.prompt_token_cost = prompt_token_cost
        self.response_token_cost = response_token_cost
        self.prompt_cost = 0
        self.response_cost = 0
        self.total_cost = 0
        self.prompt_tokens = 0
        self.response_tokens = 0
        self.total_tokens = 0
    
    def update_costs(self, prompt_tokens: int = 0, response_tokens: int = 0):
        """Update the cost of the prompt and response
        Args:
            prompt_tokens (int, optional): Number of tokens in the prompt. Defaults to 0.
            response_tokens (int, optional): Number of tokens in the response. Defaults to 0.
        """
        self.prompt_cost += prompt_tokens * self.prompt_token_cost
        self.response_cost += response_tokens * self.response_token_cost
        self.total_cost = self.prompt_cost + self.response_cost

        self.prompt_tokens += prompt_tokens
        self.response_tokens += response_tokens
        self.total_tokens = self.prompt_tokens + self.response_tokens

    def get_costs(self) -> dict[str, float]:
        """Get the cost of the llm api
        Returns:
            dict: Dictionary containing the cost of the prompt and response, and the total cost
        """
        return {
            "prompt_cost": self.prompt_cost,
            "response_cost": self.response_cost,
            "total_cost": self.total_cost
        }
    
    def get_tokens(self) -> dict[str, int]:
        """Get the number of tokens used in the llm api
        Returns:
            dict: Dictionary containing the number of tokens in the prompt and response, and the total number of tokens
        """
        return {
            "prompt_tokens": self.prompt_tokens,
            "response_tokens": self.response_tokens,
            "total_tokens": self.total_tokens
        }