# utils.py
import json
import os

# Имя файла для сохранения данных
DATA_FILE = "house_data.json"

def load_data_from_file(filename):
    """Загружает данные из JSON-файла."""
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {} # Возвращаем пустой словарь, если файл не существует

def save_data_to_file(data, filename):
    """Сохраняет данные в JSON-файл."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)