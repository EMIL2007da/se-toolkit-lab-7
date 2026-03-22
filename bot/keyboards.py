"""
Inline keyboard helpers for Telegram bot.

Provides predefined keyboards for common actions.
"""


def get_start_keyboard() -> list[list[dict[str, str]]]:
    """
    Get inline keyboard for /start command.

    Returns:
        Inline keyboard markup
    """
    return [
        [
            {"text": "📋 Available Labs", "callback_data": "cmd_labs"},
        ],
        [
            {"text": "📊 View Scores", "callback_data": "cmd_scores"},
            {"text": "💪 Health Check", "callback_data": "cmd_health"},
        ],
        [
            {"text": "❓ Help", "callback_data": "cmd_help"},
        ],
    ]


def get_quick_actions_keyboard() -> list[list[dict[str, str]]]:
    """
    Get quick action keyboard for natural language queries.

    Returns:
        Inline keyboard with suggestion buttons
    """
    return [
        [
            {"text": "📋 What labs are available?", "callback_data": "query_labs"},
        ],
        [
            {"text": "📊 Show scores for lab-04", "callback_data": "query_scores_lab04"},
        ],
        [
            {"text": "🏆 Top 5 students", "callback_data": "query_top5"},
        ],
        [
            {"text": "📉 Lowest pass rate lab", "callback_data": "query_lowest"},
        ],
    ]


def format_keyboard_message(text: str, keyboard: list[list[dict[str, str]]]) -> dict:
    """
    Format a message with inline keyboard.

    Args:
        text: Message text
        keyboard: Inline keyboard markup

    Returns:
        Formatted message dictionary
    """
    return {
        "text": text,
        "reply_markup": {"inline_keyboard": keyboard},
    }
