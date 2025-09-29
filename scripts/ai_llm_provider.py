"""Classes for different LLM providers."""  # noqa: INP001

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
        print(f"LLM: {self.provider} {self.model}")

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
        return str(response.message.content), 0


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
        if response and response.usage:
            print(
                f"tokens: "
                f"{response.usage.input_tokens} input + "
                f"{response.usage.output_tokens} output = "
                f"{response.usage.total_tokens} total"
            )
            tokens = response.usage.total_tokens
        else:
            print("WARN: No token consumption retrieved.")
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

        retries = 2
        response = None
        tokens = 0
        for attempt in range(retries + 1):
            try:
                response = client.models.generate_content(
                    model=self.model,
                    config=genai_types.GenerateContentConfig(
                        system_instruction=self.instruction
                    ),
                    contents=prompt,
                )
                break  # Exit loop if successful
            except Exception as e:
                if attempt < retries and "The model is overloaded" in str(e):
                    wait_time = 2**attempt
                    print(f"Model overloaded, retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise

        if response and response.usage_metadata:
            print(
                f"tokens: "
                f"{response.usage_metadata.prompt_token_count} prompt + "
                f"{response.usage_metadata.candidates_token_count} candidates = "
                f"{response.usage_metadata.total_token_count}"
            )
            tokens = response.usage_metadata.total_token_count
        else:
            print("WARN: No token consumption retrieved.")
        return str(response.text) if response else "", tokens


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
