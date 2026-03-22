"""
Tools Service — defines LLM tools for backend API endpoints.

Each tool is a function the LLM can call to fetch data from the backend.
"""

from typing import Any
from .lms_api import LmsApiClient


class ToolsService:
    """Service that provides tool definitions and executes them."""

    def __init__(self, api_client: LmsApiClient):
        """
        Initialize the tools service.

        Args:
            api_client: LMS API client instance
        """
        self.api_client = api_client

    def get_tool_definitions(self) -> list[dict[str, Any]]:
        """
        Get all tool definitions for the LLM.

        Returns:
            List of tool schemas in OpenAI format
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_items",
                    "description": "Get list of all labs and tasks available in the system",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_learners",
                    "description": "Get list of enrolled students and their groups",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_scores",
                    "description": "Get score distribution (4 buckets) for a specific lab",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {
                                "type": "string",
                                "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                            },
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_pass_rates",
                    "description": "Get per-task average scores and attempt counts for a lab",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {
                                "type": "string",
                                "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                            },
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_timeline",
                    "description": "Get submission timeline (submissions per day) for a lab",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {
                                "type": "string",
                                "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                            },
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_groups",
                    "description": "Get per-group scores and student counts for a lab",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {
                                "type": "string",
                                "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                            },
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_top_learners",
                    "description": "Get top N learners by score for a lab",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {
                                "type": "string",
                                "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of top learners to return, e.g. 5",
                            },
                        },
                        "required": ["lab", "limit"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_completion_rate",
                    "description": "Get completion rate percentage for a lab",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {
                                "type": "string",
                                "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                            },
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "trigger_sync",
                    "description": "Trigger data sync from autochecker API to refresh data",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
        ]

    def execute_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """
        Execute a tool by name with given arguments.

        Args:
            name: Tool name (e.g., 'get_items', 'get_pass_rates')
            arguments: Tool arguments as a dictionary

        Returns:
            Tool execution result
        """
        tool_methods = {
            "get_items": self._get_items,
            "get_learners": self._get_learners,
            "get_scores": self._get_scores,
            "get_pass_rates": self._get_pass_rates,
            "get_timeline": self._get_timeline,
            "get_groups": self._get_groups,
            "get_top_learners": self._get_top_learners,
            "get_completion_rate": self._get_completion_rate,
            "trigger_sync": self._trigger_sync,
        }

        method = tool_methods.get(name)
        if not method:
            return {"error": f"Unknown tool: {name}"}

        try:
            return method(**arguments)
        except Exception as e:
            return {"error": str(e)}

    def _get_items(self) -> list[dict]:
        """Get all items (labs and tasks)."""
        return self.api_client.get_items()

    def _get_learners(self) -> list[dict]:
        """Get all learners."""
        try:
            response = self.api_client._client.get("/learners/")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def _get_scores(self, lab: str) -> dict:
        """Get scores for a lab."""
        return self.api_client.get_scores(lab)

    def _get_pass_rates(self, lab: str) -> list[dict]:
        """Get pass rates for a lab."""
        return self.api_client.get_pass_rates(lab)

    def _get_timeline(self, lab: str) -> dict:
        """Get timeline for a lab."""
        try:
            response = self.api_client._client.get(
                "/analytics/timeline", params={"lab": lab}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def _get_groups(self, lab: str) -> dict:
        """Get groups for a lab."""
        try:
            response = self.api_client._client.get(
                "/analytics/groups", params={"lab": lab}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def _get_top_learners(self, lab: str, limit: int) -> list[dict]:
        """Get top learners for a lab."""
        try:
            response = self.api_client._client.get(
                "/analytics/top-learners", params={"lab": lab, "limit": limit}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def _get_completion_rate(self, lab: str) -> dict:
        """Get completion rate for a lab."""
        try:
            response = self.api_client._client.get(
                "/analytics/completion-rate", params={"lab": lab}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def _trigger_sync(self) -> dict:
        """Trigger pipeline sync."""
        return self.api_client.sync_pipeline()
