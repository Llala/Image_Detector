import os
import csv
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_csv_reading():
    """Test CSV reading functionality"""
    products_csv = "/home/evgeniya/Downloads/Telegram Desktop/products.csv"
    images_csv = "/home/evgeniya/Downloads/Telegram Desktop/images.csv"
    
    print("Testing CSV file access...")
    
    # Check products.csv
    try:
        with open(products_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            first_row = next(reader)
            print("Products CSV header:", list(first_row.keys()))
            print("First product:", first_row)
    except Exception as e:
        print(f"Error reading products.csv: {e}")
    
    print()
    
    # Check images.csv
    try:
        with open(images_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            first_row = next(reader)
            print("Images CSV header:", list(first_row.keys()))
            print("First image:", first_row)
    except Exception as e:
        print(f"Error reading images.csv: {e}")

def test_env_loading():
    """Test environment variable loading"""
    api_key = os.getenv('OPENROUTER_API_KEY')
    print(f"OPENROUTER_API_KEY loaded: {'Yes' if api_key and api_key != 'your_openrouter_api_key_here' else 'No'}")
    if api_key:
        print(f"API key (first 10 chars): {api_key[:10]}...")

if __name__ == "__main__":
    test_env_loading()
    print()
    test_csv_reading()