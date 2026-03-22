#!/usr/bin/env python3
"""
Telegram Bot Entry Point

Supports two modes:
1. --test mode: Call handlers directly from CLI (no Telegram connection)
2. Telegram mode: Run the bot and listen for messages

Usage:
    uv run bot.py --test "/start"     # Test mode
    uv run bot.py --test "what labs are available"  # Natural language
    uv run bot.py                     # Telegram mode
"""

import argparse
import sys

from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)
from handlers.intent_router import IntentRouter
from services.llm_client import LlmClient
from services.lms_api import LmsApiClient
from services.tools_service import ToolsService
from config import settings


# Command routing: maps command strings to handler functions
COMMANDS = {
    "/start": handle_start,
    "/help": handle_help,
    "/health": handle_health,
    "/labs": handle_labs,
    "/scores": handle_scores,
}


def parse_command(input_text: str) -> tuple[str, str | None]:
    """
    Parse command from input text.

    Args:
        input_text: Raw input (e.g., "/start" or "/scores lab-04")

    Returns:
        Tuple of (command, argument)
    """
    parts = input_text.strip().split(maxsplit=1)
    command = parts[0].lower()
    argument = parts[1] if len(parts) > 1 else None
    return command, argument


def is_natural_language_query(input_text: str) -> bool:
    """
    Check if input is a natural language query (not a slash command).

    Args:
        input_text: Raw user input

    Returns:
        True if natural language, False if slash command
    """
    return not input_text.strip().startswith("/")


def run_test_mode(command_input: str) -> None:
    """
    Run a command in test mode — call handler directly or use LLM routing.

    Args:
        command_input: Command string or natural language query
    """
    # Check if it's a natural language query
    if is_natural_language_query(command_input):
        response = handle_natural_language(command_input)
        print(response)
    else:
        response = handle_slash_command(command_input)
        format_response(response)


def handle_slash_command(command_input: str) -> str | dict:
    """
    Handle a slash command.

    Args:
        command_input: Slash command string

    Returns:
        Response text or dict with keyboard
    """
    command, argument = parse_command(command_input)

    handler = COMMANDS.get(command)
    if not handler:
        return f"❌ Unknown command: {command}\nAvailable commands: {', '.join(COMMANDS.keys())}"

    # Call handler with appropriate arguments
    if command == "/scores" and argument:
        return handle_scores(lab=argument)
    return handler()


def format_response(response: str | dict) -> None:
    """
    Print response to stdout.

    Args:
        response: String or dict with keyboard
    """
    if isinstance(response, dict):
        # Response with inline keyboard
        print(response.get("text", ""))
        if "reply_markup" in response:
            keyboard = response["reply_markup"].get("inline_keyboard", [])
            print("\n[Inline Keyboard]:")
            for row in keyboard:
                for button in row:
                    print(f"  - {button.get('text', '')}")
    else:
        print(response)


def handle_natural_language(query: str) -> str:
    """
    Handle a natural language query using LLM intent routing.

    Args:
        query: Natural language query

    Returns:
        Response text
    """
    # Check if LLM is configured
    if not settings.llm_api_key or not settings.llm_api_base_url:
        return "⚠️ LLM is not configured. Please set LLM_API_KEY and LLM_API_BASE_URL in .env.bot.secret"

    # Initialize clients
    api_client = LmsApiClient(settings.lms_api_base_url, settings.lms_api_key)
    llm_client = LlmClient(
        settings.llm_api_base_url, settings.llm_api_key, settings.llm_api_model
    )
    tools_service = ToolsService(api_client)
    router = IntentRouter(llm_client, tools_service)

    try:
        return router.route(query)
    except Exception as e:
        return f"❌ Error processing query: {e}"


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="LMS Telegram Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    uv run bot.py --test "/start"
    uv run bot.py --test "/help"
    uv run bot.py --test "/health"
    uv run bot.py --test "/labs"
    uv run bot.py --test "/scores lab-04"
    uv run bot.py --test "what labs are available?"
    uv run bot.py --test "show me scores for lab 4"
    uv run bot.py --test "which lab has the lowest pass rate?"
""",
    )
    parser.add_argument(
        "--test",
        metavar="COMMAND",
        help="Run in test mode with the given command (slash command or natural language)",
    )

    args = parser.parse_args()

    if args.test:
        run_test_mode(args.test)
    else:
        # Telegram mode — will be implemented after handlers are ready
        print("🤖 Telegram mode not yet implemented.")
        print("Use --test mode for now: uv run bot.py --test '/start'")
        sys.exit(0)


if __name__ == "__main__":
    main()
