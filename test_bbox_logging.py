#!/usr/bin/env python3

"""
Тестовый скрипт для проверки логирования bbox координат 
в бэкенде при анализе изображений
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
import json
from backend_endpoint import ImageDetector

# Загрузка переменных окружения
load_dotenv()

# Создаем экземпляр детектора
detector = ImageDetector()

# Протестируем анализ с известным файлом
test_image_path = "Pics/175336730299.jpg"  # Пример существующего файла
print(f"Тестируем анализ изображения: {test_image_path}")

try:
    # Выполним анализ
    result = detector.detect_objects(test_image_path, product_id="TEST001")
    print("Результат:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Проверим наличие объектов и координат
    if "objects" in result:
        for i, obj in enumerate(result["objects"]):
            print(f"\nОбъект {i+1}:")
            print(f"  Имя: {obj.get('name', 'не указано')}")
            print(f"  Выделения: {len(obj.get('highlights', []))}")
            
            for j, highlight in enumerate(obj.get('highlights', [])):
                bbox = highlight.get('bbox')
                if bbox:
                    print(f"    Выделение {j+1}:")
                    print(f"      Имя: {highlight.get('name', 'не указано')}")
                    print(f"      Описание: {highlight.get('description', 'не указано')}")
                    print(f"      BBox: x_min={bbox.get('x_min')}, y_min={bbox.get('y_min')}, "
                          f"x_max={bbox.get('x_max')}, y_max={bbox.get('y_max')}")
except Exception as e:
    print(f"Ошибка при анализе: {e}")
    import traceback
    traceback.print_exc()