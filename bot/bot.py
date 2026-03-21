#!/usr/bin/env python3
"""
Telegram Bot Entry Point

Supports two modes:
1. --test mode: Call handlers directly from CLI (no Telegram connection)
2. Telegram mode: Run the bot and listen for messages

Usage:
    uv run bot.py --test "/start"     # Test mode
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


def run_test_mode(command_input: str) -> None:
    """
    Run a command in test mode — call handler directly and print result.

    Args:
        command_input: Command string (e.g., "/start" or "/scores lab-04")
    """
    command, argument = parse_command(command_input)

    handler = COMMANDS.get(command)
    if not handler:
        print(f"❌ Unknown command: {command}")
        print(f"Available commands: {', '.join(COMMANDS.keys())}")
        sys.exit(1)

    # Call handler with appropriate arguments
    if command == "/scores" and argument:
        response = handle_scores(lab=argument)
    else:
        response = handler()

    print(response)


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
""",
    )
    parser.add_argument(
        "--test",
        metavar="COMMAND",
        help="Run in test mode with the given command",
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
