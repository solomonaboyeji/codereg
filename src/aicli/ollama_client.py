"""Ollama API client with tool calling support."""

import json
import requests
from typing import Any, Dict, List, Optional, Iterator


class OllamaClient:
    """Client for interacting with Ollama API."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen3-coder:30b"):
        self.base_url = base_url.rstrip('/')
        self.model = model

    def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False
    ) -> Dict[str, Any] | Iterator[Dict[str, Any]]:
        """Send a chat request to Ollama.

        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: Optional list of tool schemas for function calling
            stream: Whether to stream the response

        Returns:
            Response dict or iterator of response chunks
        """
        url = f"{self.base_url}/api/chat"

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream
        }

        if tools:
            payload["tools"] = tools

        response = requests.post(url, json=payload, stream=stream)
        response.raise_for_status()

        if stream:
            return self._stream_response(response)
        else:
            return response.json()

    def _stream_response(self, response) -> Iterator[Dict[str, Any]]:
        """Stream response chunks from Ollama."""
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line)
                    yield chunk
                except json.JSONDecodeError:
                    continue

    def list_models(self) -> List[str]:
        """List available Ollama models."""
        url = f"{self.base_url}/api/tags"
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        return [model['name'] for model in data.get('models', [])]

    def check_model_exists(self, model_name: str) -> bool:
        """Check if a model exists in Ollama."""
        models = self.list_models()
        return model_name in models


class ConversationManager:
    """Manages conversation history and context."""

    def __init__(self, system_prompt: str, max_history: int = 50):
        self.messages: List[Dict[str, Any]] = []
        self.system_prompt = system_prompt
        self.max_history = max_history

        # Add system message
        if system_prompt:
            self.messages.append({
                "role": "system",
                "content": system_prompt
            })

    def add_user_message(self, content: str):
        """Add a user message to the conversation."""
        self.messages.append({
            "role": "user",
            "content": content
        })
        self._trim_history()

    def add_assistant_message(self, content: str, tool_calls: Optional[List[Dict]] = None):
        """Add an assistant message to the conversation."""
        message = {
            "role": "assistant",
            "content": content
        }

        if tool_calls:
            message["tool_calls"] = tool_calls

        self.messages.append(message)
        self._trim_history()

    def add_tool_result(self, tool_call_id: str, tool_name: str, result: Any):
        """Add a tool result to the conversation."""
        # Convert result to string if it's a dict
        if isinstance(result, dict):
            result_str = json.dumps(result, indent=2)
        else:
            result_str = str(result)

        self.messages.append({
            "role": "tool",
            "content": result_str
        })
        self._trim_history()

    def get_messages(self) -> List[Dict[str, Any]]:
        """Get all messages in the conversation."""
        return self.messages

    def _trim_history(self):
        """Trim conversation history to max_history, keeping system message."""
        if len(self.messages) > self.max_history:
            # Keep system message and trim oldest messages
            system_msg = self.messages[0] if self.messages[0]["role"] == "system" else None
            if system_msg:
                self.messages = [system_msg] + self.messages[-(self.max_history - 1):]
            else:
                self.messages = self.messages[-self.max_history:]

    def clear(self):
        """Clear conversation history except system message."""
        system_msg = next((msg for msg in self.messages if msg["role"] == "system"), None)
        self.messages = [system_msg] if system_msg else []
