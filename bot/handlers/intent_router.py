"""
Intent Router — routes natural language queries to backend tools via LLM.

User message → LLM with tools → tool execution → LLM summarizes → response
"""

import sys
from typing import Any

from services.llm_client import LlmClient
from services.tools_service import ToolsService


class IntentRouter:
    """Routes user queries to appropriate tools via LLM."""

    SYSTEM_PROMPT = """You are a helpful assistant for a Learning Management System (LMS). 
You have access to tools that fetch data from the backend API.

When a user asks a question:
1. First understand what they're asking
2. Call the appropriate tool(s) to get the data
3. Analyze the results
4. Provide a clear, helpful answer based on the data

Available tools:
- get_items: List all labs and tasks
- get_learners: List enrolled students
- get_scores: Score distribution for a lab (requires lab parameter)
- get_pass_rates: Per-task pass rates for a lab (requires lab parameter)
- get_timeline: Submission timeline for a lab (requires lab parameter)
- get_groups: Per-group performance for a lab (requires lab parameter)
- get_top_learners: Top N learners for a lab (requires lab and limit parameters)
- get_completion_rate: Completion rate for a lab (requires lab parameter)
- trigger_sync: Refresh data from autochecker

For questions about specific labs, use lab identifiers like "lab-01", "lab-02", etc.
For multi-step questions (e.g., "which lab has the lowest pass rate"), first call get_items to get all labs, then call get_pass_rates for each lab.

If the user's message is a greeting or unclear, respond helpfully without calling tools.
"""

    def __init__(self, llm_client: LlmClient, tools_service: ToolsService):
        """
        Initialize the intent router.

        Args:
            llm_client: LLM client instance
            tools_service: Tools service instance
        """
        self.llm_client = llm_client
        self.tools_service = tools_service
        self.tool_definitions = tools_service.get_tool_definitions()

    def route(self, user_message: str) -> str:
        """
        Route a user message through the LLM tool-calling loop.

        Args:
            user_message: The user's natural language query

        Returns:
            Final response text
        """
        # Initialize conversation with system prompt
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

        max_iterations = 5  # Prevent infinite loops
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Call LLM
            response = self.llm_client.chat(messages, self.tool_definitions)

            # Extract tool calls
            tool_calls = self.llm_client.extract_tool_calls(response)

            if not tool_calls:
                # No tool calls — LLM has a final answer
                return self.llm_client.get_assistant_message(response)

            # Execute each tool call
            for tool_call in tool_calls:
                self._log(f"[tool] LLM called: {self._format_tool_call(tool_call)}")

                tool_result = self._execute_tool_call(tool_call)
                self._log(f"[tool] Result: {self._format_result(tool_result)}")

                # Add tool result to conversation
                messages.append({
                    "role": "assistant",
                    "tool_calls": [tool_call],
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.get("id", "unknown"),
                    "content": str(tool_result),
                })

            self._log(f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM")

        # Max iterations reached
        return "I'm having trouble processing this request. Please try rephrasing your question."

    def _execute_tool_call(self, tool_call: dict[str, Any]) -> Any:
        """
        Execute a single tool call.

        Args:
            tool_call: Tool call from LLM

        Returns:
            Tool execution result
        """
        function = tool_call.get("function", {})
        name = function.get("name", "unknown")

        # Parse arguments
        import json
        try:
            arguments = json.loads(function.get("arguments", "{}"))
        except json.JSONDecodeError:
            arguments = {}

        return self.tools_service.execute_tool(name, arguments)

    def _format_tool_call(self, tool_call: dict[str, Any]) -> str:
        """Format tool call for logging."""
        function = tool_call.get("function", {})
        name = function.get("name", "unknown")
        args = function.get("arguments", "{}")
        return f"{name}({args})"

    def _format_result(self, result: Any) -> str:
        """Format tool result for logging."""
        if isinstance(result, list):
            return f"{len(result)} items"
        elif isinstance(result, dict):
            if "error" in result:
                return f"Error: {result['error']}"
            return str(result)[:100]  # Truncate long results
        return str(result)[:100]

    def _log(self, message: str) -> None:
        """Log debug message to stderr."""
        print(message, file=sys.stderr)
