# Базове середовище
FROM python:3.10-slim

# Встановлення залежностей системи
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Додавання робочої директорії
WORKDIR /app

# Копіювання файлів та встановлення залежностей
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копіювання коду програми
COPY . .

# Команда для запуску FastAPI з uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
