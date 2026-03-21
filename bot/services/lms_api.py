"""
LMS API Client — HTTP client for the Learning Management Service API.

Uses Bearer token authentication. All requests include the API key
in the Authorization header.
"""

import httpx


class LmsApiClient:
    """Client for the LMS backend API."""

    def __init__(self, base_url: str, api_key: str):
        """
        Initialize the LMS API client.

        Args:
            base_url: Base URL of the LMS API (e.g., http://localhost:42002)
            api_key: API key for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=10.0,
        )

    def health_check(self) -> bool:
        """
        Check if the backend is reachable.

        Returns:
            True if backend responds, False otherwise
        """
        try:
            response = self._client.get("/health")
            return response.status_code == 200
        except httpx.RequestError:
            return False

    def get_items(self) -> list[dict]:
        """
        Fetch all items (labs, tasks) from the LMS.

        Returns:
            List of item dictionaries
        """
        try:
            response = self._client.get("/items/")
            response.raise_for_status()
            return response.json()
        except httpx.RequestError:
            return []

    def get_scores(self, lab: str) -> dict:
        """
        Fetch scores for a specific lab.

        Args:
            lab: Lab identifier (e.g., 'lab-04')

        Returns:
            Score data dictionary
        """
        try:
            response = self._client.get("/analytics/scores", params={"lab": lab})
            response.raise_for_status()
            return response.json()
        except httpx.RequestError:
            return {}

    def get_pass_rates(self, lab: str) -> dict:
        """
        Fetch pass rates for a specific lab.

        Args:
            lab: Lab identifier (e.g., 'lab-04')

        Returns:
            Pass rates data dictionary
        """
        try:
            response = self._client.get("/analytics/pass-rates", params={"lab": lab})
            response.raise_for_status()
            return response.json()
        except httpx.RequestError:
            return {}

    def sync_pipeline(self) -> dict:
        """
        Trigger data sync from the autochecker API.

        Returns:
            Sync result summary
        """
        try:
            response = self._client.post("/pipeline/sync", json={})
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            return {"error": str(e)}
