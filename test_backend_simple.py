#!/usr/bin/env python3

"""
Тестирование напрямую потока данных из бэкенда - что именно приходит
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend_endpoint import ImageDetector
import json

# Создаем экземпляр детектора
detector = ImageDetector()

print("=== Тест прямой работы с бэкендом ===")

# Тестируем конкретные изображения
test_image_path = "Pics/175336730299.jpg"

print(f"Тестируем: {test_image_path}")
result = detector.detect_objects(test_image_path, product_id="TEST001")

print("Результат функции detect_objects:")
print(json.dumps(result, indent=2, ensure_ascii=False))

# Отдельно тестировать конкретный продукт
print("\n=== Тест процесса продукта ===")
product_result = detector.process_product_images("39506410299")

print("Результат процесса продукта:")
print(json.dumps(product_result, indent=2, ensure_ascii=False))

# Проверим отдельно пути картинок
print("\n=== Проверка доступности файлов ===")
import os
path1 = "Pics/175336730299.jpg"
path2 = "Pics/175336740299.jpg"
path3 = "Pics/175336750299.jpg"

print(f"Файл {path1} существует: {os.path.exists(path1)}")
print(f"Файл {path2} существует: {os.path.exists(path2)}")
print(f"Файл {path3} существует: {os.path.exists(path3)}")