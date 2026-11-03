#!/bin/bash

echo "Starting React application..."

# Перейти в директорию проекта
cd /home/evgeniya/Image_Detector

# Проверить, установлены ли зависимости
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
else
    echo "Dependencies already installed"
fi

# Запустить React приложение
echo "Starting React development server..."
npm start