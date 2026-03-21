"""
/labs command handler — returns list of available labs.
"""

from services import LmsApiClient
from config import settings


def handle_labs(user_id: int | None = None) -> str:
    """
    Handle /labs command.

    Returns:
        List of available labs
    """
    client = LmsApiClient(settings.lms_api_base_url, settings.lms_api_key)

    try:
        items = client.get_items()
        if not items:
            return "📋 No labs available. The backend may be empty."

        # Filter for labs (type might be 'lab' or items with 'lab-' prefix)
        labs = [
            item
            for item in items
            if item.get("type") == "lab" or item.get("name", "").startswith("lab-")
        ]

        if not labs:
            # Fallback: show all items if no explicit labs found
            labs = items[:10]  # Limit to first 10

        lines = ["📋 Available Labs:"]
        for lab in labs:
            # API returns 'title' not 'name'
            name = lab.get("title", lab.get("name", "Unknown"))
            description = lab.get("description", "")
            if description:
                lines.append(f"- {name} — {description}")
            else:
                lines.append(f"- {name}")

        return "\n".join(lines)
    except Exception as e:
        return f"❌ Error fetching labs: {e}"
