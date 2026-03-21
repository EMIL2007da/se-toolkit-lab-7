"""
/scores command handler — returns student scores for a lab.
"""


def handle_scores(lab: str | None = None, user_id: int | None = None) -> str:
    """
    Handle /scores command.
    
    Args:
        lab: Lab identifier (e.g., 'lab-04')
        user_id: Telegram user ID (optional)
    
    Returns:
        Scores information for the specified lab
    """
    # Placeholder — Task 2 will fetch from LMS API
    if lab:
        return f"📊 Scores for {lab}:\n\nStudent scores will appear here after Task 2."
    return "📊 Scores\n\nUsage: /scores lab-04\n\n(Placeholder — real data from LMS API in Task 2)"
