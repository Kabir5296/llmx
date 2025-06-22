from .base_textgen import TextGenerator
from ...utils import num_tokens_from_messages
from typing import Union
from ...datamodel import TextGenerationConfig, TextGenerationResponse, Message
import requests, logging

class CustomServedTextGen(TextGenerator):
    def __init__(self,
                 provider : str = "customserved",
                 api_endpoint : str = "http://192.168.101.231:6969",
                 gen_endpoint : str = "get_response",
                 config_endpoint : str = "get_model_config",
                 model : str = "phi-4",
                 models : dict = None):
        
        super().__init__(provider=provider)
        
        self.generation_api = f"{api_endpoint}/{gen_endpoint}"
        self.config_api = f"{api_endpoint}/{config_endpoint}"
        self.model = model

    def format_messages(self, messages):
        prompt = ""
        for message in messages:
            if message["role"] == "system":
                prompt += message["content"] + "\n"
            else:
                prompt += message["role"] + ": " + message["content"] + "\n"

        return prompt

    def count_tokens(self, text) -> int:
        return num_tokens_from_messages(text)
    
    def generate(self,
                 messages: Union[list[dict], str],
                 config: TextGenerationConfig = TextGenerationConfig(),
                 **kwargs,
                 ) -> TextGenerationResponse:
        
        messages = self.format_messages(messages)
        print(messages)
        payload = {
            "prompt" : messages,
            "bypass_cache" : "True",
        }
        headers = {
            "Content-Type": "application/json"      # Specify the content type
        }
        
        config = {
            "model": config.model,
            "messages": messages,
        }
        response = requests.post(self.generation_api, json = payload, headers=headers)
        response_text = [Message(role="system", content=response.json()['generated_text'])]
        
        gen_response = TextGenerationResponse(
            text = response_text,
            config = config,
        )
        
        return gen_response
