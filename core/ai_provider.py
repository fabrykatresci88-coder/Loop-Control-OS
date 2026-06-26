from __future__ import annotations

import os
import traceback
from abc import ABC, abstractmethod
from typing import Any, List, Optional

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None  # type: ignore[assignment]

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore[assignment]


class AIProvider(ABC):
    """Abstract AI provider interface."""

    @abstractmethod
    def generate_text(self, prompt: str, **kwargs: Any) -> str:
        raise NotImplementedError

    @abstractmethod
    def embed_text(self, text: str, **kwargs: Any) -> list[float]:
        raise NotImplementedError


class OpenAIProvider(AIProvider):
    """An AI provider implementation for OpenAI's Responses API."""

    API_KEY_ENV = "OPENAI_API_KEY"
    MODEL_ENV = "OPENAI_MODEL"
    DEFAULT_MODEL = "gpt-4.1-mini"
    DEFAULT_EMBEDDING_MODEL = "text-embedding-3"
    DEFAULT_TIMEOUT_SECONDS = 60
    DEFAULT_MAX_RETRIES = 0

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        embedding_model: Optional[str] = None,
    ) -> None:
        if load_dotenv is not None:
            load_dotenv()

        self.api_key = api_key or os.getenv(self.API_KEY_ENV)
        self.model = model or os.getenv(self.MODEL_ENV, self.DEFAULT_MODEL)
        self.embedding_model = embedding_model or self.DEFAULT_EMBEDDING_MODEL
        self.client = (
            OpenAI(
                api_key=self.api_key,
                timeout=self.DEFAULT_TIMEOUT_SECONDS,
                max_retries=self.DEFAULT_MAX_RETRIES,
            )
            if OpenAI and self.api_key
            else None
        )

    def generate_text(self, prompt: str, **kwargs: Any) -> str:
        print("[DEBUG] entering generate_text()")
        print(f"[DEBUG] model name: {self.model}")

        try:
            self._ensure_ready()
        except Exception:
            traceback.print_exc()
            raise

        print(f"[DEBUG] client creation: {'ready' if self.client is not None else 'missing'}")

        request_payload = {
            "model": self.model,
            "input": prompt,
            **{k: v for k, v in kwargs.items() if v is not None},
        }
        print(f"[DEBUG] request payload: {request_payload}")

        try:
            print("[DEBUG] before client.responses.create()")
            response = self.client.responses.create(
                model=self.model,
                input=prompt,
                **{k: v for k, v in kwargs.items() if v is not None},
            )
            print("[DEBUG] after client.responses.create()")
        except Exception as error:
            print("[DEBUG] full exception:", error)
            print("[DEBUG] repr(error):", repr(error))
            print("[DEBUG] type(error):", type(error))
            traceback.print_exc()
            raise

        try:
            result = self._parse_model_response(response)
            print("[DEBUG] after extracting text")
            return result
        except Exception:
            traceback.print_exc()
            raise

    def embed_text(self, text: str, **kwargs: Any) -> list[float]:
        self._ensure_ready()
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text,
                **{k: v for k, v in kwargs.items() if v is not None},
            )
        except Exception as error:
            raise RuntimeError(self._format_openai_error(error)) from error

        data = getattr(response, "data", None)
        if not data or not isinstance(data, list):
            raise ValueError("Unexpected OpenAI embeddings response structure.")

        first_item = data[0]
        embedding = None
        if isinstance(first_item, dict):
            embedding = first_item.get("embedding")
        else:
            embedding = getattr(first_item, "embedding", None)

        if not isinstance(embedding, list):
            raise ValueError("OpenAI embeddings response did not contain an embedding vector.")

        return [float(value) for value in embedding]

    def _ensure_ready(self) -> None:
        if load_dotenv is None:
            raise RuntimeError(
                "Missing dependency: python-dotenv. Install with `pip install python-dotenv`."
            )
        if OpenAI is None:
            raise RuntimeError(
                "Missing dependency: openai. Install with `pip install openai`."
            )
        if not self.api_key:
            raise EnvironmentError(
                "Missing OPENAI_API_KEY. Add it to the .env file or environment variables."
            )
        if self.client is None:
            self.client = OpenAI(
                api_key=self.api_key,
                timeout=self.DEFAULT_TIMEOUT_SECONDS,
                max_retries=self.DEFAULT_MAX_RETRIES,
            )

    @staticmethod
    def _format_openai_error(error: Exception) -> str:
        error_type = type(error).__name__
        if error_type in {"APIConnectionError", "APITimeoutError"}:
            return "Network error while contacting OpenAI. Check your connection and try again."
        if error_type == "AuthenticationError":
            return "OpenAI authentication failed. Verify OPENAI_API_KEY in your .env file."
        if error_type == "RateLimitError":
            return "OpenAI rate limit reached. Please wait and try again."
        if error_type in {"APIError", "InternalServerError"}:
            return "OpenAI service error. Please try again shortly."
        if error_type == "BadRequestError":
            return f"OpenAI rejected the request: {error}"
        return f"OpenAI request failed: {error}"

    @staticmethod
    def _parse_model_response(response: Any) -> str:
        output_text = getattr(response, "output_text", None)
        if isinstance(output_text, str) and output_text.strip():
            return output_text.strip()

        output = getattr(response, "output", None)
        if isinstance(output, list):
            parts: List[str] = []
            for item in output:
                content = None
                if isinstance(item, dict):
                    content = item.get("content")
                else:
                    content = getattr(item, "content", None)

                if isinstance(content, list):
                    for element in content:
                        if isinstance(element, dict):
                            text_value = element.get("text")
                        else:
                            text_value = getattr(element, "text", None)

                        if isinstance(text_value, str):
                            parts.append(text_value)
                        elif isinstance(element, str):
                            parts.append(element)

                elif isinstance(content, str):
                    parts.append(content)

            if parts:
                return "".join(parts).strip()

        raise ValueError("OpenAI Responses did not return text output.")


def create_provider(name: str) -> AIProvider:
    normalized_name = name.strip().lower()
    if normalized_name == "openai":
        return OpenAIProvider()
    raise ValueError(f"Unknown AI provider: {name}")
