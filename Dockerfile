# ---------- Этап сборки зависимостей ----------
FROM python:3.12-slim AS builder

# Установка Poetry
ENV POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_NO_INTERACTION=1

RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

WORKDIR /app

# Копируем только файлы с зависимостями (для кэширования слоёв)
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости (без dev-зависимостей)
RUN poetry install --no-dev --no-interaction --no-ansi

# ---------- Финальный образ ----------
FROM python:3.12-slim

WORKDIR /app

# Копируем установленные зависимости из builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Копируем исходный код приложения
COPY . .

# Создаём непривилегированного пользователя
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Открываем порт
EXPOSE 8000

# Запуск приложения (используем модуль app)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]