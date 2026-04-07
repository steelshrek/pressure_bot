# Используем стандартный образ Python
FROM python:3.11-slim

# Устанавливаем только необходимые системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libopenjp2-7 \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую папку
WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код проекта
COPY . .

# Команда для запуска бота
CMD ["python", "daryabot.py"]