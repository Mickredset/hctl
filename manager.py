# manager.py
from models import User, Room, Floor
import utils


class HouseManager:
    """Основной класс для управления домом."""

    def __init__(self):
        self.floors = {}  # Словарь {floor_number: Floor object}
        self.users = {}  # Словарь {user_id: User object}
        self.next_user_id = 1  # Для автоматического генерирования ID

    def load_data(self):
        """Загружает данные из JSON-файла."""
        data = utils.load_data_from_file(utils.DATA_FILE)

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
        utils.save_data_to_file(data, utils.DATA_FILE)

    def add_floor(self, floor_number):
        """Добавляет этаж в дом."""
        if floor_number not in self.floors:
            self.floors[floor_number] = Floor(floor_number)
            print(f"Этаж {floor_number} добавлен.")
            return True
        else:
            print(f"Этаж {floor_number} уже существует.")
            return False

    def remove_floor(self, floor_number):
        """Удаляет этаж из дома."""
        if floor_number in self.floors:
            del self.floors[floor_number]
            print(f"Этаж {floor_number} удален.")
            return True
        else:
            print(f"Этаж {floor_number} не найден.")
            return False

    def add_room_to_floor(self, floor_number, room_number, room_type="Обычная"):
        """Добавляет комнату на этаж."""
        floor = self.floors.get(floor_number)
        if floor:
            if room_number not in floor.rooms:
                room = Room(room_number, room_type)
                floor.add_room(room)
                print(f"Комната {room_number} добавлена на этаж {floor_number}.")
                return True
            else:
                print(f"Комната {room_number} уже существует на этаже {floor_number}.")
                return False
        else:
            print(f"Этаж {floor_number} не найден.")
            return False

    def remove_room_from_floor(self, floor_number, room_number):
        """Удаляет комнату с этажа."""
        floor = self.floors.get(floor_number)
        if floor and room_number in floor.rooms:
            floor.remove_room(room_number)
            print(f"Комната {room_number} удалена с этажа {floor_number}.")
            return True
        else:
            print(f"Комната {room_number} на этаже {floor_number} не найдена.")
            return False

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
            return True
        else:
            if not user:
                print(f"Пользователь с ID {user_id} не найден.")
            if not room:
                print(f"Комната {room_number} на этаже {floor_number} не найдена.")
            return False

    def remove_user_from_room(self, user_id, floor_number, room_number):
        """Удаляет пользователя из комнаты."""
        floor = self.floors.get(floor_number)
        room = floor.get_room(room_number) if floor else None

        if room and user_id in room.residents:
            room.remove_resident(user_id)
            print(f"Пользователь с ID {user_id} удален из комнаты {room_number} на этаже {floor_number}.")
            return True
        else:
            print(f"Пользователь с ID {user_id} не найден в комнате {room_number} на этаже {floor_number}.")
            return False

    def list_floors(self):
        """Выводит список этажей."""
        if not self.floors:
            print("Дом пустой. Нет этажей.")
            return []
        print("\n--- Список этажей ---")
        floors_list = []
        for floor_num in sorted(self.floors.keys()):
            print(f"Этаж {floor_num}")
            floors_list.append(floor_num)
        return floors_list

    def list_rooms_on_floor(self, floor_number):
        """Выводит список комнат на этаже."""
        floor = self.floors.get(floor_number)
        if not floor:
            print(f"Этаж {floor_number} не найден.")
            return []
        if not floor.rooms:
            print(f"На этаже {floor_number} нет комнат.")
            return []
        print(f"\n--- Комнаты на этаже {floor_number} ---")
        rooms_list = []
        for room_num in sorted(floor.rooms.keys(), key=lambda x: int(x) if x.isdigit() else x):
            room = floor.rooms[room_num]
            print(f"Комната {room_num} ({room.room_type}), Жильцы: {len(room.residents)} чел.")
            rooms_list.append((room_num, room.room_type))
        return rooms_list

    def list_users_in_room(self, floor_number, room_number):
        """Выводит список пользователей в комнате."""
        floor = self.floors.get(floor_number)
        room = floor.get_room(room_number) if floor else None
        if not room:
            print(f"Комната {room_number} на этаже {floor_number} не найдена.")
            return []
        if not room.residents:
            print(f"В комнате {room_number} на этаже {floor_number} нет жильцов.")
            return []
        print(f"\n--- Жильцы комнаты {room_number} на этаже {floor_number} ---")
        users_list = []
        for user_id in room.residents:
            user = self.users.get(user_id)
            if user:
                user_info = f"- {user.name} (ID: {user.user_id}, Возраст: {user.age or 'Не указан'}, Email: {user.email or 'Не указан'})"
                print(user_info)
                users_list.append(user_info)
        return users_list

    # --- Новые методы для GUI ---

    def get_all_floors_numbers(self):
        """Возвращает список номеров этажей."""
        return sorted(self.floors.keys())

    def get_rooms_on_floor(self, floor_number):
        """Возвращает список номеров комнат на этаже."""
        floor = self.floors.get(floor_number)
        if floor:
            return sorted(floor.rooms.keys())
        return []

    def get_residents_of_room(self, floor_number, room_number):
        """Возвращает список объектов User, проживающих в комнате."""
        floor = self.floors.get(floor_number)
        room = floor.get_room(room_number) if floor else None
        residents = []
        if room:
            for user_id in room.residents:
                user = self.users.get(user_id)
                if user:
                    residents.append(user)
        return residents

    def get_user_by_id(self, user_id):
        """Возвращает объект User по ID."""
        return self.users.get(user_id)