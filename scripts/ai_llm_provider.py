"""Classes for different LLM providers."""  # noqa: INP001

import logging
import os
import time

from dotenv import load_dotenv  # pip install dotenv
from google import genai
from google.genai import types as genai_types
from ollama import ChatResponse, chat  # pip install ollama
from openai import OpenAI  # pip install openai

# pip install google-genai


# load .env file
load_dotenv()
logger = logging.getLogger()  # get base logger


def my_getenv(key: str) -> str:
    """Wrap for getenv that throws Exception."""
    value = os.getenv(key)
    if value is None:
        msg = (
            f"{key} is not set in the environment. "
            "Please set it in your .env file or environment variables."
        )
        raise RuntimeError(msg)
    return value


class LLMProvider:
    """Class for different LLM providers."""

    def __init__(self, instruction: str, model: str) -> None:
        """Init the LLM with model and context instruction."""
        self.provider = "NONE"
        self.instruction = instruction
        self.models = {"NONE"}
        self.model = model

    def check_model_valid(self, model: str) -> None:
        """Raise ValueError if model is not valid."""
        if model not in self.models:
            msg = (
                f"Model '{model}' is not a valid model for provider '{self.provider}'. "
                f"Valid models: {self.models}"
            )
            raise ValueError(msg)

    def print_llm_and_model(self) -> None:
        """Print out the LLM and the model."""
        logger.info("LLM: %s %s", self.provider, self.model)

    def call(self, prompt: str) -> tuple[str, int]:
        """Call the LLM with prompt."""
        raise NotImplementedError


class OllamaProvider(LLMProvider):  # noqa: D101
    def __init__(self, instruction: str, model: str) -> None:  # noqa: D107
        super().__init__(instruction, model)
        self.provider = "Ollama"
        self.models = {
            "llama3.2:1b",
            "llama3.2:3b",
            "deepseek-r1:1.5b",
            "deepseek-r1:8b",
            "deepseek-r1:7b",
        }
        self.check_model_valid(model)

    def call(self, prompt: str) -> tuple[str, int]:
        """Call the LLM."""
        response: ChatResponse = chat(
            model=self.model,
            stream=False,
            # think=True,
            messages=[
                {"role": "system", "content": self.instruction},
                {"role": "user", "content": prompt},
            ],
        )
        tokens = 0  # not returned by ollama
        return str(response.message.content), tokens


class OpenAIProvider(LLMProvider):  # noqa: D101
    def __init__(self, instruction: str, model: str) -> None:  # noqa: D107
        super().__init__(instruction, model)
        self.provider = "OpenAI"
        self.models = {
            "gpt-5-nano",
            "gpt-5-mini",
            "gpt-5",
            "gpt-4o-mini",
        }
        self.check_model_valid(model)

    def call(self, prompt: str) -> tuple[str, int]:
        """Call the LLM."""
        client = OpenAI(api_key=my_getenv("OPENAI_API_KEY"))
        tokens = 0
        response = client.responses.create(
            model=self.model,
            input=[
                {"role": "developer", "content": self.instruction},
                {"role": "user", "content": prompt},
            ],
        )
        if response and response.usage and response.usage.input_tokens:
            logger.info(
                "tokens: %d input + %d output = %d total",
                response.usage.input_tokens,
                response.usage.output_tokens,
                response.usage.total_tokens,
            )
            tokens = response.usage.total_tokens
        else:
            logger.warning("No token consumption retrieved.")
        return response.output_text, tokens


class GeminiProvider(LLMProvider):  # noqa: D101
    def __init__(self, instruction: str, model: str) -> None:  # noqa: D107
        super().__init__(instruction, model)
        self.provider = "Gemini"
        self.models = {
            "gemini-2.5-flash-lite",
            "gemini-2.5-flash",
            "gemini-2.5-pro",
        }
        self.check_model_valid(model)

    def call(self, prompt: str) -> tuple[str, int]:
        """Call the LLM."""
        client = genai.Client(api_key=my_getenv("GEMINI_API_KEY"))

        response = None
        tokens = 0
        retries_max = 3
        for attempt in range(retries_max):
            try:
                response = client.models.generate_content(
                    model=self.model,
                    config=genai_types.GenerateContentConfig(
                        system_instruction=self.instruction
                    ),
                    contents=prompt,
                )
                break  # Exit retry loop if successful
            except Exception as e:
                if attempt <= retries_max and "The model is overloaded" in str(e):
                    wait_time = 2**attempt
                    logger.warning(
                        "Model overloaded, retrying in %d seconds...", wait_time
                    )
                    time.sleep(wait_time)
                else:
                    raise

        if (
            response
            and response.usage_metadata
            and response.usage_metadata.total_token_count
        ):
            logger.info(
                "tokens: %d prompt + %d candidates = %d",
                response.usage_metadata.prompt_token_count,
                response.usage_metadata.candidates_token_count,
                response.usage_metadata.total_token_count,
            )
            tokens = response.usage_metadata.total_token_count
        else:
            logger.warning("No token consumption retrieved.")
        s = str(response.text) if response else ""
        return s, tokens


def create_llm_provider(
    provider_name: str, model: str, instruction: str
) -> LLMProvider:
    """Create LLM provider, based on string name."""
    if provider_name == "Ollama":
        llm_provider = OllamaProvider(instruction=instruction, model=model)
    elif provider_name == "OpenAI":
        llm_provider = OpenAIProvider(instruction=instruction, model=model)
    elif provider_name == "Gemini":
        llm_provider = GeminiProvider(instruction=instruction, model=model)
    else:
        msg = f"Unknown LLM {provider_name}"
        raise ValueError(msg)
    return llm_provider


# Example usage
def llm_call(provider: LLMProvider, prompt: str) -> tuple[str, int]:
    """Send prompt to LLM."""
    return provider.call(prompt)


if __name__ == "__main__":
    instruction = "Talk like a pirate. Give a short answer. "
    prompt = "What is the capital of Germany?"

    # switch here
    llm_provider = OllamaProvider(instruction=instruction, model="llama3.2:1b")
    # llm_provider = OpenAIProvider(instruction=instruction, model="gpt-5-nano")
    # llm_provider = GeminiProvider(instruction=instruction, model="gemini-2.5-pro")
    print(llm_call(llm_provider, prompt))
