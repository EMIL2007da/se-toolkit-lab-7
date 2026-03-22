"""
/start command handler — returns welcome message with inline keyboard.
"""

from keyboards import get_start_keyboard, format_keyboard_message


def handle_start(user_id: int | None = None) -> dict:
    """
    Handle /start command.

    Args:
        user_id: Telegram user ID (optional, not used in placeholder)

    Returns:
        Welcome message with inline keyboard
    """
    text = """👋 Welcome to LMS Bot!

I can help you explore lab data, scores, and analytics.

**What I can do:**
- Show available labs and tasks
- Display scores and pass rates for any lab
- Find top performers
- Compare lab performance
- Answer questions in natural language!

Try asking me things like:
• "what labs are available?"
• "show me scores for lab 4"
• "which lab has the lowest pass rate?"
"""
    keyboard = get_start_keyboard()
    return format_keyboard_message(text, keyboard)
