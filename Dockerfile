FROM python:3.11-slim

WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY bot.py .
COPY database.py .
COPY currency.py .

# Создаем директорию для базы данных
RUN mkdir -p /data

# Запускаем бота
CMD ["python", "bot.py"]
