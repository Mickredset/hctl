# models.py

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