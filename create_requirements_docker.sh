#!/bin/bash
# Скрипт установки зависимостей для Docker

# Создаем временный requirements.txt для Docker
cat > requirements_docker.txt << EOF
openai
python-dotenv
requests
Flask
Pillow
annotated-types
anyio
blinker
certifi
charset-normalizer
click
h11
httpcore
httpcore2
httpx
httpx2
idna
itsdangerous
Jinja2
jiter
MarkupSafe
openai
pillow
pydantic
pydantic_core
python-dotenv
requests
sniffio
truststore
typing-inspection
typing_extensions
urllib3
Werkzeug
EOF

echo "Файл requirements_docker.txt создан для использования в Docker"