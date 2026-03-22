# Bot Dockerfile — builds the Telegram bot container
# Uses uv for dependency management (no pip, no requirements.txt)

FROM python:3.14.2-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy pyproject.toml and uv.lock for dependency installation
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen --no-dev

# Copy bot source code
COPY bot/ ./bot/

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["uv", "run", "python", "-m", "bot.bot"]
