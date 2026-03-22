"""
/health command handler — checks backend connection status.
"""

from services import LmsApiClient
from config import settings


def handle_health(user_id: int | None = None) -> str:
    """
    Handle /health command.

    Returns:
        Backend health status message
    """
    client = LmsApiClient(settings.lms_api_base_url, settings.lms_api_key)

    try:
        items = client.get_items()
        if items:
            return f"✅ Backend is healthy. {len(items)} items available."
        return "⚠️ Backend is reachable but no items found."
    except Exception as e:
        error_msg = str(e).lower()
        if "connection refused" in error_msg or "connect" in error_msg:
            return f"❌ Backend error: connection refused ({settings.lms_api_base_url}). Check that the services are running."
        elif "502" in error_msg or "bad gateway" in error_msg:
            return f"❌ Backend error: HTTP 502 Bad Gateway. The backend service may be down."
        elif "401" in error_msg or "unauthorized" in error_msg:
            return f"❌ Backend error: HTTP 401 Unauthorized. Check LMS_API_KEY in .env.bot.secret."
        elif "404" in error_msg or "not found" in error_msg:
            return f"❌ Backend error: HTTP 404 Not Found. Check LMS_API_BASE_URL."
        else:
            return f"❌ Backend error: {e}"
