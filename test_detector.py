#!/usr/bin/env python3

"""
Test script for Image Detection PoC
This script demonstrates how to use the ImageDetector class 
with the CSV file integration capability.
"""

import os
import sys
from dotenv import load_dotenv
from image_detector import ImageDetector

def main():
    # Load environment variables
    load_dotenv()
    
    # Check if API key is set
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key or api_key == 'your_openrouter_api_key_here':
        print("Warning: OPENROUTER_API_KEY not found or not set properly")
        print("Please set your API key in the .env file")
        print("Get your API key from: https://openrouter.ai/keys")
        return
    
    # Show available CSV files in the expected location
    products_csv = "/home/evgeniya/Downloads/Telegram Desktop/products.csv"
    images_csv = "/home/evgeniya/Downloads/Telegram Desktop/images.csv"
    
    print("CSV Files Available:")
    print(f"Products file: {products_csv}")
    print(f"Images file: {images_csv}")
    print()
    
    # Check if files exist
    if os.path.exists(products_csv) and os.path.exists(images_csv):
        print("Test mode: Would process products and images from CSV files")
        print("In a real scenario, you would:")
        print("1. Set your OPENROUTER_API_KEY in the .env file")
        print("2. Run: python image_detector.py")
        print("3. This will process first 3 products with their images")
        print()
        print("The implementation will:")
        print("- Read product information from products.csv")
        print("- Read image URLs from images.csv")
        print("- Download images from URLs")
        print("- Process them with Qwen's visual-language model")
        print("- Return object detection results")
        print()
        print("To run it for real:")
        print("1. Make sure your .env file has OPENROUTER_API_KEY")
        print("2. Run: python image_detector.py")
    else:
        print("CSV files not found. Please ensure they're in the expected locations.")
        print("Expected locations:")
        print(f"  Products: {products_csv}")
        print(f"  Images: {images_csv}")
        print()
        print("To run with real data:")
        print("1. Place your products.csv and images.csv files in these locations")
        print("2. Set your API key in .env file")
        print("3. Run: python image_detector.py")

if __name__ == "__main__":
    main()