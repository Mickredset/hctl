import json
import os

# Имя файла для сохранения данных
DATA_FILE = "house_data.json"


class User:
    """Класс для представления пользователя/жильца."""

    def __init__(self, user_id, name, age=None, email=None):
        self.user_id = user_id
        self.name = name
        self.age = age
        self.email = email

    def to_dict(self):
        """Преобразует объект пользователя в словарь для JSON."""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "age": self.age,
            "email": self.email
        }

    @classmethod
    def from_dict(cls, data):
        """Создает объект пользователя из словаря."""
        return cls(
            user_id=data["user_id"],
            name=data["name"],
            age=data.get("age"),
            email=data.get("email")
        )


class Room:
    """Класс для представления комнаты."""

    def __init__(self, room_number, room_type="Обычная"):
        self.room_number = room_number
        self.room_type = room_type
        self.residents = []  # Список user_id жильцов

    def add_resident(self, user_id):
        """Добавляет жильца в комнату."""
        if user_id not in self.residents:
            self.residents.append(user_id)

    def remove_resident(self, user_id):
        """Удаляет жильца из комнаты."""
        if user_id in self.residents:
            self.residents.remove(user_id)

    def to_dict(self):
        """Преобразует объект комнаты в словарь для JSON."""
        return {
            "room_number": self.room_number,
            "room_type": self.room_type,
            "residents": self.residents
        }

    @classmethod
    def from_dict(cls, data):
        """Создает объект комнаты из словаря."""
        room = cls(
            room_number=data["room_number"],
            room_type=data.get("room_type", "Обычная")
        )
        room.residents = data.get("residents", [])
        return room


class Floor:
    """Класс для представления этажа."""

    def __init__(self, floor_number):
        self.floor_number = floor_number
        self.rooms = {}  # Словарь {room_number: Room object}

    def add_room(self, room):
        """Добавляет комнату на этаж."""
        self.rooms[room.room_number] = room

    def remove_room(self, room_number):
        """Удаляет комнату с этажа."""
        if room_number in self.rooms:
            del self.rooms[room_number]

    def get_room(self, room_number):
        """Получает объект комнаты по номеру."""
        return self.rooms.get(room_number)

    def to_dict(self):
        """Преобразует объект этажа в словарь для JSON."""
        return {
            "floor_number": self.floor_number,
            "rooms": {str(num): room.to_dict() for num, room in self.rooms.items()}
        }

    @classmethod
    def from_dict(cls, data):
        """Создает объект этажа из словаря."""
        floor = cls(floor_number=data["floor_number"])
        for room_num_str, room_data in data["rooms"].items():
            room = Room.from_dict(room_data)
            floor.add_room(room)
        return floor


class HouseManager:
    """Основной класс для управления домом."""

    def __init__(self):
        self.floors = {}  # Словарь {floor_number: Floor object}
        self.users = {}  # Словарь {user_id: User object}
        self.next_user_id = 1  # Для автоматического генерирования ID

    def load_data(self):
        """Загружает данные из JSON-файла."""
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Загрузка пользователей
            for user_data in data.get("users", []):
                user = User.from_dict(user_data)
                self.users[user.user_id] = user
                # Обновляем next_user_id для новых пользователей
                if user.user_id >= self.next_user_id:
                    self.next_user_id = user.user_id + 1

            # Загрузка этажей и комнат
            for floor_data in data.get("floors", []):
                floor = Floor.from_dict(floor_data)
                self.floors[floor.floor_number] = floor

    def save_data(self):
        """Сохраняет данные в JSON-файл."""
        data = {
            "users": [user.to_dict() for user in self.users.values()],
            "floors": [floor.to_dict() for floor in self.floors.values()]
        }
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def add_floor(self, floor_number):
        """Добавляет этаж в дом."""
        if floor_number not in self.floors:
            self.floors[floor_number] = Floor(floor_number)
            print(f"Этаж {floor_number} добавлен.")
        else:
            print(f"Этаж {floor_number} уже существует.")

    def remove_floor(self, floor_number):
        """Удаляет этаж из дома."""
        if floor_number in self.floors:
            del self.floors[floor_number]
            print(f"Этаж {floor_number} удален.")
        else:
            print(f"Этаж {floor_number} не найден.")

    def add_room_to_floor(self, floor_number, room_number, room_type="Обычная"):
        """Добавляет комнату на этаж."""
        floor = self.floors.get(floor_number)
        if floor:
            if room_number not in floor.rooms:
                room = Room(room_number, room_type)
                floor.add_room(room)
                print(f"Комната {room_number} добавлена на этаж {floor_number}.")
            else:
                print(f"Комната {room_number} уже существует на этаже {floor_number}.")
        else:
            print(f"Этаж {floor_number} не найден.")

    def remove_room_from_floor(self, floor_number, room_number):
        """Удаляет комнату с этажа."""
        floor = self.floors.get(floor_number)
        if floor and room_number in floor.rooms:
            floor.remove_room(room_number)
            print(f"Комната {room_number} удалена с этажа {floor_number}.")
        else:
            print(f"Комната {room_number} на этаже {floor_number} не найдена.")

    def create_user(self, name, age=None, email=None):
        """Создает нового пользователя."""
        user = User(self.next_user_id, name, age, email)
        self.users[self.next_user_id] = user
        self.next_user_id += 1
        print(f"Пользователь '{name}' создан с ID {user.user_id}.")
        return user.user_id

    def assign_user_to_room(self, user_id, floor_number, room_number):
        """Назначает пользователя в комнату."""
        user = self.users.get(user_id)
        floor = self.floors.get(floor_number)
        room = floor.get_room(room_number) if floor else None

        if user and room:
            room.add_resident(user_id)
            print(f"Пользователь {user.name} (ID: {user_id}) назначен в комнату {room_number} на этаже {floor_number}.")
        else:
            if not user:
                print(f"Пользователь с ID {user_id} не найден.")
            if not room:
                print(f"Комната {room_number} на этаже {floor_number} не найдена.")

    def remove_user_from_room(self, user_id, floor_number, room_number):
        """Удаляет пользователя из комнаты."""
        floor = self.floors.get(floor_number)
        room = floor.get_room(room_number) if floor else None

        if room and user_id in room.residents:
            room.remove_resident(user_id)
            print(f"Пользователь с ID {user_id} удален из комнаты {room_number} на этаже {floor_number}.")
        else:
            print(f"Пользователь с ID {user_id} не найден в комнате {room_number} на этаже {floor_number}.")

    def list_floors(self):
        """Выводит список этажей."""
        if not self.floors:
            print("Дом пустой. Нет этажей.")
            return
        print("\n--- Список этажей ---")
        for floor_num in sorted(self.floors.keys()):
            print(f"Этаж {floor_num}")

    def list_rooms_on_floor(self, floor_number):
        """Выводит список комнат на этаже."""
        floor = self.floors.get(floor_number)
        if not floor:
            print(f"Этаж {floor_number} не найден.")
            return
        if not floor.rooms:
            print(f"На этаже {floor_number} нет комнат.")
            return
        print(f"\n--- Комнаты на этаже {floor_number} ---")
        for room_num in sorted(floor.rooms.keys(), key=lambda x: int(x) if x.isdigit() else x):
            room = floor.rooms[room_num]
            print(f"Комната {room_num} ({room.room_type}), Жильцы: {len(room.residents)} чел.")

    def list_users_in_room(self, floor_number, room_number):
        """Выводит список пользователей в комнате."""
        floor = self.floors.get(floor_number)
        room = floor.get_room(room_number) if floor else None
        if not room:
            print(f"Комната {room_number} на этаже {floor_number} не найдена.")
            return
        if not room.residents:
            print(f"В комнате {room_number} на этаже {floor_number} нет жильцов.")
            return
        print(f"\n--- Жильцы комнаты {room_number} на этаже {floor_number} ---")
        for user_id in room.residents:
            user = self.users.get(user_id)
            if user:
                print(
                    f"- {user.name} (ID: {user.user_id}, Возраст: {user.age or 'Не указан'}, Email: {user.email or 'Не указан'})")


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