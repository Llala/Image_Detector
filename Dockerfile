FROM python:3.12-slim

WORKDIR /app

# Копируем файл требований для установки зависимостей
COPY requirements_docker.txt .
RUN pip install --no-cache-dir -r requirements_docker.txt

# Копируем остальные файлы проекта
COPY . .

EXPOSE 5003

CMD ["python3", "backend_endpoint.py"]