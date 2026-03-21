"""
/help command handler — returns list of available commands.
"""


def handle_help(user_id: int | None = None) -> str:
    """
    Handle /help command.
    
    Returns:
        List of available commands
    """
    return """📚 Available Commands:

/start — Start the bot
/help — Show this help message
/health — Check backend connection
/labs — List available labs
/scores — View your scores

For Task 3, you can also ask questions in plain text!"""
