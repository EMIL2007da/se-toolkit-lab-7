"""
/start command handler — returns welcome message.
"""


def handle_start(user_id: int | None = None) -> str:
    """
    Handle /start command.
    
    Args:
        user_id: Telegram user ID (optional, not used in placeholder)
    
    Returns:
        Welcome message text
    """
    return "👋 Welcome to LMS Bot!\n\nUse /help to see available commands."
