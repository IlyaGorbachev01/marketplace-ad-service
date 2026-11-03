FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:${PATH}"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_DEV=1 \
    UV_FROZEN=1 \
    PYTHONPATH=/app

ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PORT=8000

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY . .

RUN uv sync --frozen --no-dev

EXPOSE 8000

CMD ["python", "-m", "bin.api"]
