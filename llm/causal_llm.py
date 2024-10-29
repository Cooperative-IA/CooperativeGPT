import os
import requests
import re

from llm.base_llm import BaseLLM
import openai
from openai import OpenAI
import tiktoken

class FinetunedCausal(BaseLLM):
    """A custom finetuned model to predict the consequences of actions"""

    def __init__(self):
        """Constructor for the class
        Args:
            prompt_token_cost (float): Cost of a token in the prompt
            response_token_cost (float): Cost of a token in the response
        """
        super().__init__(0, 0, 2048, 0.6)

        self.logger.info("Loading finetuned causal model...")

        self.completion_endpoint = 'http://localhost:5000/generate'
        self.batch_completion_endpoint = 'http://localhost:5000/batch_generate'
        # Encoding to estimate the number of tokens
        # TODO: Change the encoding to the one used by the model
        self.encoding = tiktoken.encoding_for_model("gpt-4o")
        
        self.logger.info("finetuned causal model loaded")

    def _format_prompt(self, prompt: str, role: str = 'user') -> list[dict[str, str]]:
        """Format the prompt to be used by the model
        Args:
            prompt (str): Prompt
        Returns:
            dict: Dictionary with the formatted prompt
        """
        return {"prompt": prompt}

    def __completion(self, prompt: str, **kwargs) -> tuple[str, int, int]:
        """Completion api for the model
        Args:
            prompt (str): Prompt for the completion
        Returns:
            tuple(str, int, int): A tuple with the completed text, the number of tokens in the prompt and the number of tokens in the response
        """
        # prompt = self._format_prompt(prompt)

        # Make a post request to the completion endpoint
        try:
            action = re.search(r'### Action taken:\s(.+?)\n', prompt).group(1)
            if action.startswith('explore'):
                response = 'Explore takes you to a random location in your observed window, so it can take several steps, and is impossible to know the observations you will receive after executing it.'
                return response, 0, 0
            # response = requests.post(self.completion_endpoint, json=prompt)
            response = requests.post("http://localhost:11434/api/generate", json={
                "prompt": prompt,
                # "model": "model3_q4",
                "model": "mushrooms",
                "stream": False,
                "raw": True,
                # "keep_alive": '60s',
                "options": {
                        "num_predict": 2000,
                        "min_p": 0.2,
                }
                }, timeout=60)

            if response.status_code != 200:
                raise Exception(f"Error: {response.status_code} - {response.text}")
            
            response = response.json()
            # completion = response['generated_text']
            # prompt_tokens = response['prompt_tokens']
            # response_tokens = response['response_tokens']
            completion = response['response']
            relevant_information = completion

            # Parse the response to extract the relevant information
            # future_observations = completion.split('\n\n')
            # number_of_steps_to_complete_action = len(future_observations)
            # last_observation = future_observations[-1]
            # relevant_information = last_observation + f"It will take you {number_of_steps_to_complete_action} steps to complete the action.\n"

            prompt_tokens = response['prompt_eval_count']
            response_tokens = response['eval_count']
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error: {e}")
    
        return relevant_information, prompt_tokens, response_tokens
    
    def _completion(self, prompt: str, **kwargs) -> tuple[str, int, int]:
        """Wrapper for the completion api with retry and exponential backoff
        
        Args:
            prompt (str): Prompt for the completion

        Returns:
            tuple(str, int, int): A tuple with the completed text, the number of tokens in the prompt and the number of tokens in the response
        """
        wrapper = BaseLLM.retry_with_exponential_backoff(self.__completion, self.logger, errors=(Exception))
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
    
    def batch_completion(self, prompt: str, **kwargs) -> str:
        """Method for the completion api. It updates the cost of the prompt and response and log the tokens and prompts
        Args:
            prompt (str): Prompt file or string for the completion
            inputs (list[str]): List of inputs to replace the <input{number}> in the prompt. For example: ["This is the first input", "This is the second input"]
        Returns:
            str: Completed text
        """

        # prompt = self._load_prompt(prompt)
        # prompts = []
        # for i, input_data in enumerate(kwargs.get("inputs", [])):
        #     prompt_ = self._replace_inputs_in_prompt(prompt, input_data)
        #     prompts.append(prompt_)

        #     # Check that the prompt is not too long
        #     if self._calculate_tokens(prompt) > self.max_tokens * self.max_tokens_ratio_per_input:
        #         raise ValueError("Prompt is too long")
        
        #     self.logger.info(f"Prompt {i}: {prompt_}")

        # kwargs.pop("inputs", None) # Remove the inputs from the kwargs to avoid passing them to the completion api

        # Make a post request to the completion endpoint
        # try:
        #     response = requests.post(self.batch_completion_endpoint, json={"prompts": prompts})

        #     if response.status_code != 200:
        #         raise Exception(f"Error: {response.status_code} - {response.text}")
            
        #     response = response.json()
        #     completions = response['generated_text']
        #     prompt_tokens = response['prompt_tokens']
        #     response_tokens = response['response_tokens']
        # except requests.exceptions.RequestException as e:
        #     raise Exception(f"Error: {e}")
        completions = []
        prompt_tokens_total = 0
        response_tokens_total = 0
        for inputs in kwargs.get("inputs", []):
            completion = self.completion(prompt, inputs=inputs)
            completions.append(completion)
    
        # self.logger.info(f"Response: {completions}")

        # self._update_costs(prompt_tokens, response_tokens)
        # self.logger.info(f"Prompt tokens: {prompt_tokens}")
        # self.logger.info(f"Response tokens: {response_tokens}")

        return completions