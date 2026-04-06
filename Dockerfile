FROM python:3.11-slim

WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY bot.py .
COPY currency.py .

# Запускаем бота
CMD ["python", "bot.py"]
