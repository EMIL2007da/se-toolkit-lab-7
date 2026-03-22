"""
/scores command handler — returns student scores for a lab.
"""

from services import LmsApiClient
from config import settings


def handle_scores(lab: str | None = None, user_id: int | None = None) -> str:
    """
    Handle /scores command.

    Args:
        lab: Lab identifier (e.g., 'lab-04')
        user_id: Telegram user ID (optional)

    Returns:
        Scores information for the specified lab
    """
    if not lab:
        return "📊 Scores\n\nUsage: /scores lab-04\n\nProvide a lab identifier, e.g., /scores lab-04"

    client = LmsApiClient(settings.lms_api_base_url, settings.lms_api_key)

    try:
        # Try pass-rates endpoint first
        pass_rates = client.get_pass_rates(lab)

        # Check for empty list or empty dict
        if not pass_rates or (isinstance(pass_rates, list) and len(pass_rates) == 0):
            # Fallback to scores endpoint
            scores = client.get_scores(lab)
            if scores and isinstance(scores, list) and len(scores) > 0:
                # Check if all buckets have zero count (non-existent lab)
                total_count = sum(bucket.get("count", 0) for bucket in scores)
                if total_count > 0:
                    return format_scores_response(lab, scores)
            return f"📊 No scores found for {lab}. Check the lab identifier."

        return format_pass_rates_response(lab, pass_rates)
    except Exception as e:
        return f"❌ Error fetching scores for {lab}: {e}"


def format_pass_rates_response(lab: str, pass_rates: dict | list) -> str:
    """Format pass-rates API response."""
    lines = [f"📊 Pass rates for {lab}:"]

    # Handle list response (direct array of tasks)
    if isinstance(pass_rates, list):
        for task in pass_rates:
            task_name = task.get("task", task.get("name", "Unknown"))
            rate = task.get("avg_score", task.get("pass_rate", task.get("rate", 0)))
            attempts = task.get("attempts", 0)
            lines.append(f"- {task_name}: {rate:.1f}% ({attempts} attempts)")
        return "\n".join(lines)

    # Handle dict response with nested tasks
    tasks = pass_rates.get("tasks", pass_rates.get("results", []))
    if isinstance(tasks, list):
        for task in tasks:
            task_name = task.get("name", task.get("task", "Unknown"))
            rate = task.get("pass_rate", task.get("rate", task.get("avg_score", 0)))
            attempts = task.get("attempts", 0)
            lines.append(f"- {task_name}: {rate:.1f}% ({attempts} attempts)")
    elif isinstance(tasks, dict):
        for task_name, data in tasks.items():
            if isinstance(data, dict):
                rate = data.get("pass_rate", data.get("rate", data.get("avg_score", 0)))
                attempts = data.get("attempts", 0)
                lines.append(f"- {task_name}: {rate:.1f}% ({attempts} attempts)")
            else:
                lines.append(f"- {task_name}: {data}%")

    return "\n".join(lines)


def format_scores_response(lab: str, scores: dict) -> str:
    """Format scores API response."""
    lines = [f"📊 Scores for {lab}:"]

    # Handle different response formats
    if "scores" in scores:
        for score in scores["scores"]:
            student = score.get("student", score.get("name", "Unknown"))
            value = score.get("score", score.get("value", 0))
            lines.append(f"- {student}: {value}")

    return "\n".join(lines)
