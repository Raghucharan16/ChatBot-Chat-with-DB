from vanna.base import VannaBase
import requests
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class MyCustomLLM(VannaBase):
    def __init__(self, config=None):
        """
        Initialize the custom LLM with configuration options.

        Args:
            config (dict, optional): Configuration dictionary with:
                - 'use_api' (bool): Whether to use the Hugging Face API (default: True).
                - 'model_name' (str): Model to use (default: 'mistralai/Mistral-7B-Instruct-v0.1').
                - 'api_key' (str): Hugging Face API key (required if use_api is True).
        """
        if config is None:
            config = {}

        # Default to using Hugging Face API as per your request
        self.use_api = config.get('use_api', True)
        self.model_name = config.get('model_name', 'mistralai/Mistral-7B-Instruct-v0.1')
        self.api_key = config.get('api_key', None)

        if self.use_api:
            # Ensure API key is provided when using the API
            if self.api_key is None:
                raise ValueError("API key is required when use_api is True")
        else:
            # Optional local inference setup
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)

    def submit_prompt(self, prompt, **kwargs) -> str:
        """
        Submit a prompt to the language model and get the response.

        Args:
            prompt (str): The input prompt.
            **kwargs: Additional parameters (e.g., max_length, temperature).

        Returns:
            str: The generated response.
        """
        if self.use_api:
            return self._submit_prompt_hf_api(prompt, **kwargs)
        else:
            return self._submit_prompt_local(prompt, **kwargs)

    def _submit_prompt_hf_api(self, prompt, **kwargs) -> str:
        """
        Submit a prompt to the Hugging Face Inference API.

        Args:
            prompt (str): The input prompt.
            **kwargs: Additional generation parameters.

        Returns:
            str: The generated response.
        """
        endpoint = f"https://api-inference.huggingface.co/models/{self.model_name}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "inputs": prompt,
            "parameters": kwargs
        }
        response = requests.post(endpoint, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()[0]["generated_text"]
        else:
            raise Exception(f"API request failed with status {response.status_code}: {response.text}")

    def _submit_prompt_local(self, prompt, **kwargs) -> str:
        """
        Submit a prompt to a locally loaded model.

        Args:
            prompt (str): The input prompt.
            **kwargs: Additional generation parameters.

        Returns:
            str: The generated response.
        """
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(**inputs, **kwargs)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
