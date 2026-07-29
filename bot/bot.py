#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Бот "Новое Вельяминово"
Работает без внешних API и сторонних библиотек.
Поддерживает офлайн-режим через локальное кэширование данных.
"""

import urllib.request
import urllib.error
import json
import os
import re
from datetime import datetime

# Конфигурация
CACHE_FILE = "velyaminovo_cache.json"
TARGET_URL = "https://camaning.vercel.app/"


def fetch_data():
    """Пытается получить HTML-код страницы. Возвращает None при отсутствии интернета."""
    try:
        # Добавляем User-Agent, чтобы сервер не блокировал запрос как от простого скрипта
        req = urllib.request.Request(
            TARGET_URL,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) VelyaminovoBot/1.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode('utf-8')
    except (urllib.error.URLError, urllib.error.HTTPError):
        return None
    except Exception:
        return None


def parse_data(html):
    """Извлекает структурированные данные из HTML с помощью регулярных выражений."""
    # Удаляем все HTML-теги для упрощения поиска
    clean_text = re.sub(r'<[^>]+>', ' ', html)
    # Заменяем множественные пробелы и переносы строк на один пробел
    clean_text = re.sub(r'\s+', ' ', clean_text)

    data = {
        "last_updated": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "season": "Не найдено",
        "location": "Не найдено",
        "task": "Не найдено",
        "water_temp": "Не найдено"
    }

    # Парсинг сезона
    season_match = re.search(r'Текущий сезон\s*([A-Za-zА-Яа-я0-9\s]+?)(?=Локация|Задача|Принять участие|Рецепты|$)',
                             clean_text)
    if season_match:
        data["season"] = season_match.group(1).strip()

    # Парсинг локации
    location_match = re.search(r'Локация\s*([A-Za-zА-Яа-я0-9\s]+?)(?=Задача|Принять участие|Рецепты|Строительство|$)',
                               clean_text)
    if location_match:
        data["location"] = location_match.group(1).strip()

    # Парсинг задачи
    task_match = re.search(r'Задача\s*([A-Za-zА-Яа-я0-9\s]+?)(?=Принять участие|Рецепты|Строительство|Управление|$)',
                           clean_text)
    if task_match:
        data["task"] = task_match.group(1).strip()

    # Парсинг температуры воды (ищет формат вроде "22.0°C")
    temp_match = re.search(r'(\d+\.\d+\s*°C)', clean_text)
    if temp_match:
        data["water_temp"] = temp_match.group(1).strip()

    return data


def load_cache():
    """Загружает данные из локального кэша."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return None


def save_cache(data):
    """Сохраняет данные в локальный кэш."""
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception:
        pass


def update_data():
    """Обновляет данные: пытается скачать их, а при неудаче использует кэш."""
    print("[*] Проверка подключения к сайту...")
    html = fetch_data()

    if html:
        print("[+] Данные успешно получены с сайта.")
        parsed = parse_data(html)
        save_cache(parsed)
        return parsed
    else:
        print("[!] Нет подключения к интернету или сайт недоступен.")
        print("[*] Переход в офлайн-режим. Загрузка из локального кэша...")
        cached = load_cache()
        if cached:
            print("[+] Данные загружены из кэша.")
            return cached
        else:
            print("[!] Кэш отсутствует. Запустите бот с интернетом для первичной загрузки.")
            return None


def main():
    print("=" * 60)
    print(" 🤖 БОТ 'НОВОЕ ВЕЛЬЯМИНОВО'")
    print(" Работает без внешних API и сторонних библиотек (pip)")
    print(" Поддерживает офлайн-режим через локальный кэш")
    print("=" * 60)

    data = update_data()

    if not data:
        print("\n❌ Невозможно продолжить работу без данных.")
        print("💡 Совет: запустите скрипт с включённым интернетом хотя бы один раз.")
        return

    while True:
        print("\n" + "-" * 60)
        print("МЕНЮ:")
        print(" 1. 📍 Информация о локации и сезоне")
        print(" 2. 🎯 Текущая задача сообщества")
        print(" 3. 🌡️ Температура воды (данные с сайта)")
        print(" 4. 🔄 Принудительно обновить данные из интернета")
        print(" 5. 🚪 Выход")

        choice = input("\nВаш выбор (1-5): ").strip()

        if choice == '1':
            print("\n📍 Локация:   " + data.get('location', 'Неизвестно'))
            print("📅 Сезон:     " + data.get('season', 'Неизвестно'))
            print("🕒 Обновлено: " + data.get('last_updated', 'Неизвестно'))

        elif choice == '2':
            print("\n🎯 Текущая задача: " + data.get('task', 'Неизвестно'))

        elif choice == '3':
            print("\n🌡️ Температура воды (пример из данных): " + data.get('water_temp', 'Не найдено'))
            print("   ℹ️ Данные взяты из последнего кэша сайта camaning.vercel.app")

        elif choice == '4':
            print("\n[*] Принудительное обновление...")
            html = fetch_data()
            if html:
                data = parse_data(html)
                save_cache(data)
                print("[+] Данные успешно обновлены и сохранены в кэш!")
            else:
                print("[!] Не удалось подключиться к интернету. Проверьте соединение.")

        elif choice == '5':
            print("\n👋 До свидания! Бот завершил работу.")
            break

        else:
            print("\n[!] Неверный выбор. Пожалуйста, введите число от 1 до 5.")


if __name__ == "__main__":
    main()