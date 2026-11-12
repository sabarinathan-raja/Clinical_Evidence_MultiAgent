
import logging
from typing import Optional

from backend.core.config import settings

logger = logging.getLogger(__name__)


class ModelGateway:

    def __init__(self):
        self.model = None
        self.provider = "gemini"
        self.initialized = False

    def initialize(self):

        if self.initialized:
            return self.model

        if not settings.GEMINI_API_KEY:
            logger.warning(
                "Gemini API key not configured. "
                "LLM calls will be unavailable."
            )
            return None

        try:
            from langchain_google_genai import ChatGoogleGenerativeAI

            self.model = ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL,
                google_api_key=settings.GEMINI_API_KEY,
                temperature=0.1,
                max_retries=2,
                timeout=60
            )

            self.initialized = True

            logger.info(
                "Gemini model initialized: %s",
                settings.GEMINI_MODEL
            )

            return self.model

        except Exception:
            logger.exception(
                "Failed to initialize Gemini model."
            )
            raise

    def get_model(self):

        if self.model is None:
            return self.initialize()

        return self.model

    @staticmethod
    def _build_messages(
        prompt: str,
        system_message: Optional[str] = None
    ):
        """
        Combine system instructions and user prompt
        into a single human message.

        This avoids the Gemini API developer-instruction
        compatibility error.
        """

        if system_message and system_message.strip():
            combined_prompt = (
                "INSTRUCTIONS:\n"
                f"{system_message.strip()}\n\n"
                "USER REQUEST:\n"
                f"{prompt.strip()}"
            )
        else:
            combined_prompt = prompt.strip()

        return [
            ("human", combined_prompt)
        ]

    @staticmethod
    def _extract_content(response) -> str:

        content = response.content

        if isinstance(content, str):
            return content.strip()

        if isinstance(content, list):
            parts = []

            for item in content:
                if isinstance(item, dict):
                    parts.append(str(item.get("text", "")))
                else:
                    parts.append(str(item))

            return "\n".join(parts).strip()

        return str(content).strip()

    def invoke(
        self,
        prompt: str,
        system_message: Optional[str] = None
    ) -> str:

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        model = self.get_model()

        if model is None:
            raise RuntimeError(
                "LLM is unavailable. Configure GEMINI_API_KEY."
            )

        messages = self._build_messages(
            prompt,
            system_message
        )

        try:
            response = model.invoke(messages)

            return self._extract_content(response)

        except Exception as exc:
            logger.exception("LLM invocation failed.")

            raise RuntimeError(
                "AI model invocation failed."
            ) from exc

    async def ainvoke(
        self,
        prompt: str,
        system_message: Optional[str] = None
    ) -> str:

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        model = self.get_model()

        if model is None:
            raise RuntimeError(
                "LLM is unavailable. Configure GEMINI_API_KEY."
            )

        messages = self._build_messages(
            prompt,
            system_message
        )

        try:
            response = await model.ainvoke(messages)

            return self._extract_content(response)

        except Exception as exc:
            logger.exception(
                "Async LLM invocation failed."
            )

            raise RuntimeError(
                "AI model invocation failed."
            ) from exc

    def health_check(self) -> dict:

        return {
            "provider": self.provider,
            "model": settings.GEMINI_MODEL,
            "initialized": self.initialized,
            "configured": bool(settings.GEMINI_API_KEY),
            "available": self.model is not None
        }


model_gateway = ModelGateway()


def get_model_gateway() -> ModelGateway:
    return model_gateway
