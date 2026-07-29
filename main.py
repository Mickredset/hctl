# main.py
from manager import HouseManager


def main():
    """Главная функция для запуска интерактивного меню."""
    manager = HouseManager()
    manager.load_data()  # Загружаем данные при старте

    while True:
        print("\n=== Меню Управления Домом ===")
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


if __name__ == "__main__":
    main()