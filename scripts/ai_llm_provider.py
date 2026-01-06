"""Classes for different LLM providers."""  # noqa: INP001

import logging
import os
import time

from azure.identity import (
    DefaultAzureCredential,
    get_bearer_token_provider,
)
from dotenv import load_dotenv  # pip install dotenv
from google import genai  # pip install google-genai
from google.genai import types as genai_types
from ollama import ChatResponse, chat  # pip install ollama
from openai import (
    AzureOpenAI,
    OpenAI,  # pip install openai
)

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

    def __init__(self, provider: str, models: list[str]) -> None:
        """Init the LLM with model and context instruction."""
        self.provider = provider
        self.models = models

    def check_model_valid(self, model: str) -> None:
        """Raise ValueError if model is not valid."""
        if model not in self.models:
            msg = (
                f"Model '{model}' is not a valid model for provider '{self.provider}'. "
                f"Valid models: {self.models}"
            )
            raise ValueError(msg)

    def get_models(self) -> list[str]:
        """Return list of available models."""
        return self.models

    def call(self, model: str, instruction: str, prompt: str) -> tuple[str, int]:
        """
        Call the LLM model with instruction and prompt.

        Returns a tuple containing the response text and the number of tokens consumed.
        """
        raise NotImplementedError


class MockProvider(LLMProvider):
    """Mocking LLM provider for local dev and tests."""

    def __init__(self) -> None:  # noqa: D107
        super().__init__(provider="Mocked", models=["random"])
        self.check_model_valid("random")

    def call(self, model: str, instruction: str, prompt: str) -> tuple[str, int]:  # noqa: ARG002
        """Call the LLM."""
        tokens = 51  # random number, chosen by fair dice roll
        response = f"Mocked {prompt} response"
        return response, tokens


class OllamaProvider(LLMProvider):  # noqa: D101
    def __init__(self) -> None:  # noqa: D107
        super().__init__(
            provider="Ollama",
            models=[
                "llama3.2:1b",
                "llama3.2:3b",
                "deepseek-r1:1.5b",
                "deepseek-r1:8b",
                "deepseek-r1:7b",
            ],
        )

    def call(self, model: str, instruction: str, prompt: str) -> tuple[str, int]:
        """Call the LLM."""
        self.check_model_valid(model)
        response: ChatResponse = chat(
            model=model,
            stream=False,
            # think=True,
            messages=[
                {"role": "system", "content": instruction},
                {"role": "user", "content": prompt},
            ],
        )
        tokens = 0  # not returned by ollama
        return str(response.message.content), tokens


class OpenAIProvider(LLMProvider):  # noqa: D101
    def __init__(self) -> None:  # noqa: D107
        super().__init__(
            provider="OpenAI",
            models=[
                "gpt-5-nano",
                "gpt-5-mini",
                "gpt-5",
                "gpt-4o-mini",
            ],
        )

    def call(self, model: str, instruction: str, prompt: str) -> tuple[str, int]:
        """Call the LLM."""
        self.check_model_valid(model)
        client = OpenAI(api_key=my_getenv("OPENAI_API_KEY"))
        tokens = 0
        response = client.responses.create(
            model=model,
            input=[
                {"role": "developer", "content": instruction},
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
    def __init__(self) -> None:  # noqa: D107
        super().__init__(
            provider="Gemini",
            models=[
                "gemini-2.5-flash-lite",
                "gemini-2.5-flash",
                "gemini-2.5-pro",
            ],
        )

    def call(self, model: str, instruction: str, prompt: str) -> tuple[str, int]:
        """Call the LLM."""
        self.check_model_valid(model)
        client = genai.Client(api_key=my_getenv("GEMINI_API_KEY"))

        response = None
        tokens = 0
        retries_max = 3
        for attempt in range(retries_max):
            try:
                response = client.models.generate_content(
                    model=model,
                    config=genai_types.GenerateContentConfig(
                        system_instruction=instruction
                    ),
                    contents=prompt,
                )
                break  # Exit retry loop if successful
            except Exception as e:
                if attempt < retries_max and "The model is overloaded" in str(e):
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


class AzureOpenAIProvider(LLMProvider):
    """Azure OpenAI LLM provider."""

    def __init__(self) -> None:  # noqa: D107
        super().__init__(
            provider="AzureOpenAI", models=["gpt-5-nano", "gpt-5-mini", "gpt-5"]
        )

    def call(self, model: str, instruction: str, prompt: str) -> tuple[str, int]:
        """Call the LLM with retry logic."""
        self.check_model_valid(model)
        client = AzureOpenAI(
            api_version=my_getenv("AZURE_API_VERSION"),
            azure_endpoint=my_getenv("AZURE_API_URL"),
            azure_ad_token_provider=get_bearer_token_provider(
                DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
            ),
        )
        messages = [
            {"role": "system", "content": instruction},
            {"role": "user", "content": prompt},
        ]

        response = client.chat.completions.create(
            model=model,
            messages=messages,  # type: ignore
        )

        s = (
            response.choices[0].message.content
            if response.choices[0].message.content
            else ""
        )
        tokens = (
            response.usage.total_tokens
            if hasattr(response, "usage") and response.usage
            else 0
        )
        return s, tokens


def create_llm_provider(provider_name: str) -> LLMProvider:
    """Create LLM provider, based on string name."""
    if provider_name == "Mock":
        return MockProvider()
    if provider_name == "Ollama":
        return OllamaProvider()
    if provider_name == "OpenAI":
        return OpenAIProvider()
    if provider_name == "Gemini":
        return GeminiProvider()
    if provider_name == "AzureOpenAI":
        return AzureOpenAIProvider()
    msg = f"Unknown LLM {provider_name}"
    raise ValueError(msg)


if __name__ == "__main__":
    instruction = "Talk like a pirate. Give a short answer. "
    prompt = "What is the capital of Germany?"

    # switch here
    llm_provider = OllamaProvider()
    # llm_provider = OpenAIProvider()
    # llm_provider = GeminiProvider()
    # llm_provider = AzureOpenAIProvider()

    print(
        llm_provider.call(model="llama3.2:1b", instruction=instruction, prompt=prompt)
    )
