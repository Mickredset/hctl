# main.py
from flask import Flask, render_template, request, jsonify
from manager import HouseManager
import utils
import sys  # Импортируем sys для выхода


# --- Функции CLI (скопированы из вашего старого main.py или адаптированы) ---
def run_cli(manager):
    """Функция для запуска командной строки (ваш старый main)."""
    while True:
        print("\n=== Меню Управления Домом (CLI) ===")
        print("1. Добавить этаж")
        print("2. Удалить этаж")
        print("3. Добавить комнату на этаж")
        print("4. Удалить комнату с этажа")
        print("5. Создать пользователя")
        print("6. Назначить пользователя в комнату")
        print("7. Удалить пользователя из комнаты")
        print("8. Показать этажи")
        print("9. Показать комнаты на этаже")
        print("10. Показать жильцов комнаты")
        print("11. Сохранить и выйти")

        choice = input("Выберите действие (1-11): ").strip()

        if choice == '1':
            try:
                floor_num = int(input("Введите номер этажа: "))
                manager.add_floor(floor_num)
            except ValueError:
                print("Ошибка: Номер этажа должен быть числом.")
        elif choice == '2':
            try:
                floor_num = int(input("Введите номер этажа для удаления: "))
                manager.remove_floor(floor_num)
            except ValueError:
                print("Ошибка: Номер этажа должен быть числом.")
        elif choice == '3':
            try:
                floor_num = int(input("Введите номер этажа: "))
                room_num = input("Введите номер комнаты: ")
                room_type = input("Введите тип комнаты (по умолчанию 'Обычная'): ").strip()
                if not room_type:
                    room_type = "Обычная"
                manager.add_room_to_floor(floor_num, room_num, room_type)
            except ValueError:
                print("Ошибка: Номер этажа должен быть числом.")
        elif choice == '4':
            try:
                floor_num = int(input("Введите номер этажа: "))
                room_num = input("Введите номер комнаты для удаления: ")
                manager.remove_room_from_floor(floor_num, room_num)
            except ValueError:
                print("Ошибка: Номер этажа должен быть числом.")
        elif choice == '5':
            name = input("Введите имя пользователя: ").strip()
            if not name:
                print("Имя не может быть пустым.")
                continue
            age_input = input("Введите возраст (или оставьте пустым): ").strip()
            age = int(age_input) if age_input.isdigit() else None
            email = input("Введите email (или оставьте пустым): ").strip()
            if not email:
                email = None
            manager.create_user(name, age, email)
        elif choice == '6':
            try:
                user_id = int(input("Введите ID пользователя: "))
                floor_num = int(input("Введите номер этажа: "))
                room_num = input("Введите номер комнаты: ")
                manager.assign_user_to_room(user_id, floor_num, room_num)
            except ValueError:
                print("Ошибка: ID пользователя и номер этажа должны быть числами.")
        elif choice == '7':
            try:
                user_id = int(input("Введите ID пользователя: "))
                floor_num = int(input("Введите номер этажа: "))
                room_num = input("Введите номер комнаты: ")
                manager.remove_user_from_room(user_id, floor_num, room_num)
            except ValueError:
                print("Ошибка: ID пользователя и номер этажа должны быть числами.")
        elif choice == '8':
            manager.list_floors()
        elif choice == '9':
            try:
                floor_num = int(input("Введите номер этажа: "))
                manager.list_rooms_on_floor(floor_num)
            except ValueError:
                print("Ошибка: Номер этажа должен быть числом.")
        elif choice == '10':
            try:
                floor_num = int(input("Введите номер этажа: "))
                room_num = input("Введите номер комнаты: ")
                manager.list_users_in_room(floor_num, room_num)
            except ValueError:
                print("Ошибка: Номер этажа должен быть числом.")
        elif choice == '11':
            manager.save_data()
            print("Данные сохранены. Выход из программы.")
            break
        else:
            print("Неверный выбор. Пожалуйста, выберите от 1 до 11.")


# --- Конец функций CLI ---

def run_kivy_gui(manager):
    """Функция для запуска Kivy GUI."""
    try:
        from kivy_gui_app import HouseGUIApp
        # --- ИСПРАВЛЕНО: Используем правильное имя параметра ---
        app = HouseGUIApp(manager_instance=manager) # Передаем загруженный менеджер в приложение Kivy
        app.run()
        # manager.save_data() вызывается в on_stop Kivy приложения
    except ImportError:
        print("Kivy не установлен. Установите его с помощью 'pip install kivy'.")
        print("Запускаю CLI...")
        run_cli(manager) # Возврат к CLI, если Kivy недоступен


# --- Настройка Flask приложения ---
app = Flask(__name__)

# Создаем и загружаем менеджер один раз, перед запуском CLI или Flask
manager = HouseManager()
manager.load_data()  # Загружаем данные при запуске программы


# --- Маршруты Flask (остаются как есть) ---
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/structure', methods=['GET'])
def get_house_structure():
    return jsonify(manager.get_house_structure())


@app.route('/api/floors', methods=['POST'])
def add_floor():
    data = request.get_json()
    floor_number = data.get('floor_number')
    if manager.add_floor(floor_number):
        manager.save_data()  # Сохраняем после успешного добавления
        return jsonify({"success": True, "message": f"Этаж {floor_number} добавлен."})
    else:
        return jsonify({"success": False, "message": f"Этаж {floor_number} уже существует."}), 400


@app.route('/api/rooms', methods=['POST'])
def add_room():
    data = request.get_json()
    floor_number = data.get('floor_number')
    room_number = data.get('room_number')
    room_type = data.get('room_type', 'Обычная')
    if manager.add_room_to_floor(floor_number, room_number, room_type):
        manager.save_data()
        return jsonify({"success": True, "message": f"Комната {room_number} добавлена."})
    else:
        return jsonify(
            {"success": False, "message": f"Комната {room_number} уже существует на этаже {floor_number}."}), 400


@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    name = data.get('name')
    age = data.get('age')
    email = data.get('email')
    if name:
        user_id = manager.create_user(name, age, email)
        manager.save_data()
        return jsonify({"success": True, "user_id": user_id})
    else:
        return jsonify({"success": False, "message": "Имя пользователя обязательно."}), 400


@app.route('/api/assign', methods=['POST'])
def assign_user():
    data = request.get_json()
    user_id = data.get('user_id')
    floor_number = data.get('floor_number')
    room_number = data.get('room_number')
    success = manager.assign_user_to_room(user_id, floor_number, room_number)
    if success:
        manager.save_data()
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Не удалось назначить пользователя."}), 400


# --- Выбор режима запуска ---
def main():
    """Главная функция для запуска интерактивного меню выбора режима."""
    print("Добро пожаловать в программу управления домом!")
    print("Выберите режим запуска:")
    print("1. Командная строка (CLI)")
    print("2. Графический интерфейс (Kivy GUI)")
    print("3. Веб-интерфейс (Flask, запустить сервер)")

    choice = input("Введите 1, 2 или 3: ").strip()

    if choice == '1':
        print("Запуск в режиме командной строки...")
        run_cli(manager)  # Передаем загруженный менеджер в CLI
        # manager.save_data() уже вызывается внутри CLI при выходе
    elif choice == '2':
        print("Запуск графического интерфейса Kivy...")
        run_kivy_gui(manager)  # Передаем загруженный менеджер в Kivy GUI
    elif choice == '3':
        print("Запуск веб-сервера Flask...")
        print("Откройте браузер и перейдите по адресу: http://127.0.0.1:5000")
        app.run(debug=True)  # Запускаем Flask сервер
        # manager.save_data() можно вызвать при graceful shutdown Flask, но CLI/Kivy это делают явно
    else:
        print("Неверный выбор. Запускаю CLI по умолчанию.")
        run_cli(manager)


if __name__ == '__main__':
    main()