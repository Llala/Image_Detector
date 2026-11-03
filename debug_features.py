#!/usr/bin/env python3

"""
Утилита для тестирования ответов бэкенда
"""

import requests
import json

# Тестируем конкретный продукт
PRODUCT_ID = "39506410299"

def test_backend_endpoint():
    print(f"Тестируем бэкенд для продукта: {PRODUCT_ID}")
    
    # Получаем список изображений
    images_url = f"http://localhost:5003/product-images/{PRODUCT_ID}"
    print(f"Запрашиваем изображения: {images_url}")
    
    try:
        images_response = requests.get(images_url)
        if images_response.status_code == 200:
            images_data = images_response.json()
            print("Изображения получены:")
            print(json.dumps(images_data, indent=2, ensure_ascii=False))
        else:
            print(f"Ошибка получения изображений: {images_response.status_code}")
            print(images_response.text)
            return
    except Exception as e:
        print(f"Ошибка при запросе изображений: {e}")
        return
    
    # Запускаем анализ
    analyze_url = "http://localhost:5003/analyze-product"
    print(f"\nЗапрашиваем анализ: {analyze_url}")
    
    try:
        response = requests.post(analyze_url, json={"product_id": PRODUCT_ID})
        if response.status_code == 200:
            data = response.json()
            print("Анализ завершен:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Проверим, есть ли в features данные
            features = data.get("features", [])
            print(f"\nКоличество элементов features: {len(features)}")
            
            if features:
                for i, item in enumerate(features):
                    if isinstance(item, list):
                        print(f"feature[{i}]: массив длиной {len(item)}")
                        if item:
                            print(f"внутри: {item[0] if isinstance(item[0], dict) else type(item[0])}")
                    else:
                        print(f"feature[{i}]: {type(item)} - {item}")
            else:
                print("features - пустой массив!")
        else:
            print(f"Ошибка анализа: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Ошибка при анализе: {e}")

if __name__ == "__main__":
    test_backend_endpoint()