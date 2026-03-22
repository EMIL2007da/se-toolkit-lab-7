"""
LLM Client — calls the LLM API with tool support.

Uses OpenAI-compatible API format for tool calling.
"""

import httpx
from typing import Any


class LlmClient:
    """Client for LLM API with tool calling support."""

    def __init__(self, base_url: str, api_key: str, model: str):
        """
        Initialize the LLM client.

        Args:
            base_url: Base URL of the LLM API (e.g., http://localhost:42005/v1)
            api_key: API key for authentication
            model: Model name to use
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=60.0,
        )

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Send a chat request to the LLM.

        Args:
            messages: List of conversation messages
            tools: Optional list of tool definitions

        Returns:
            LLM response as a dictionary
        """
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        response = self._client.post("/chat/completions", json=payload)
        response.raise_for_status()
        return response.json()

    def extract_tool_calls(self, response: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Extract tool calls from LLM response.

        Args:
            response: LLM response dictionary

        Returns:
            List of tool calls (empty if none)
        """
        choices = response.get("choices", [])
        if not choices:
            return []

        message = choices[0].get("message", {})
        tool_calls = message.get("tool_calls", [])

        return tool_calls if tool_calls else []

    def get_assistant_message(self, response: dict[str, Any]) -> str:
        """
        Extract assistant's text message from response.

        Args:
            response: LLM response dictionary

        Returns:
            Assistant's message text
        """
        choices = response.get("choices", [])
        if not choices:
            return ""

        message = choices[0].get("message", {})
        return message.get("content", "")
