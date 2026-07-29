# gui_app.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from manager import HouseManager


class HouseGUIApp:
    def __init__(self, root, manager):
        self.root = root
        self.manager = manager
        self.root.title("Управление Домом - GUI")
        self.root.geometry("800x600")

        # Основные фреймы
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Кнопки действий
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(btn_frame, text="Добавить Этаж", command=self.add_floor).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Добавить Комнату", command=self.add_room).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Создать Пользователя", command=self.create_user).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Назначить в Комната", command=self.assign_user_to_room).pack(side=tk.LEFT,
                                                                                                 padx=(0, 5))
        ttk.Button(btn_frame, text="Показать Жильцов", command=self.show_residents).pack(side=tk.LEFT, padx=(0, 5))

        # Treeview для отображения этажей/комнат
        self.tree = ttk.Treeview(self.main_frame, columns=("info"), show="tree headings")
        self.tree.heading("#0", text="Название")
        self.tree.heading("info", text="Дополнительная информация")
        self.tree.column("#0", width=200)
        self.tree.column("info", width=400)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Обновляем дерево при запуске
        self.refresh_tree()

    def refresh_tree(self):
        """Обновляет содержимое дерева."""
        # Очищаем текущее содержимое
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Заполняем дерево данными
        for floor_num in self.manager.get_all_floors_numbers():
            floor_item_id = self.tree.insert("", "end", text=f"Этаж {floor_num}", values=("", ""))
            for room_num in self.manager.get_rooms_on_floor(floor_num):
                room = self.manager.floors[floor_num].get_room(room_num)
                resident_count = len(room.residents)
                self.tree.insert(floor_item_id, "end", text=f"Комната {room_num}",
                                 values=(f"Тип: {room.room_type}, Жильцы: {resident_count}", ""))

    def add_floor(self):
        floor_num_str = simpledialog.askstring("Добавить Этаж", "Введите номер этажа:")
        if floor_num_str:
            try:
                floor_num = int(floor_num_str)
                if self.manager.add_floor(floor_num):
                    messagebox.showinfo("Успех", f"Этаж {floor_num} добавлен.")
                    self.refresh_tree()
                else:
                    messagebox.showwarning("Предупреждение", f"Этаж {floor_num} уже существует.")
            except ValueError:
                messagebox.showerror("Ошибка", "Номер этажа должен быть числом.")

    def add_room(self):
        floor_num_str = simpledialog.askstring("Выбор Этажа", "Введите номер этажа для добавления комнаты:")
        if floor_num_str:
            try:
                floor_num = int(floor_num_str)
                if floor_num not in self.manager.get_all_floors_numbers():
                    messagebox.showerror("Ошибка", f"Этаж {floor_num} не существует.")
                    return

                room_num = simpledialog.askstring("Добавить Комната", "Введите номер комнаты:")
                if room_num:
                    room_type = simpledialog.askstring("Тип Комната", "Введите тип комнаты (по умолчанию 'Обычная'):",
                                                       initialvalue="Обычная")
                    if room_type is None:  # Отмена ввода типа
                        room_type = "Обычная"

                    if self.manager.add_room_to_floor(floor_num, room_num, room_type):
                        messagebox.showinfo("Успех", f"Комната {room_num} добавлена на этаж {floor_num}.")
                        self.refresh_tree()
                    else:
                        messagebox.showwarning("Предупреждение",
                                               f"Комната {room_num} уже существует на этаже {floor_num}.")
            except ValueError:
                messagebox.showerror("Ошибка", "Номер этажа должен быть числом.")

    def create_user(self):
        name = simpledialog.askstring("Создать Пользователя", "Введите имя пользователя:")
        if name:
            age_str = simpledialog.askstring("Возраст", "Введите возраст (или оставьте пустым):")
            age = int(age_str) if age_str and age_str.isdigit() else None
            email = simpledialog.askstring("Email", "Введите email (или оставьте пустым):")
            if email == "":  # Если пользователь нажал OK без ввода
                email = None

            user_id = self.manager.create_user(name, age, email)
            messagebox.showinfo("Успех", f"Пользователь '{name}' создан с ID {user_id}.")

    def assign_user_to_room(self):
        user_id_str = simpledialog.askstring("Назначить Пользователя", "Введите ID пользователя:")
        if user_id_str:
            try:
                user_id = int(user_id_str)
                user = self.manager.get_user_by_id(user_id)
                if not user:
                    messagebox.showerror("Ошибка", f"Пользователь с ID {user_id} не найден.")
                    return

                floor_num_str = simpledialog.askstring("Выбор Этажа", "Введите номер этажа:")
                if floor_num_str:
                    try:
                        floor_num = int(floor_num_str)
                        if floor_num not in self.manager.get_all_floors_numbers():
                            messagebox.showerror("Ошибка", f"Этаж {floor_num} не существует.")
                            return

                        room_num = simpledialog.askstring("Выбор Комната", "Введите номер комнаты:")
                        if room_num:
                            if self.manager.assign_user_to_room(user_id, floor_num, room_num):
                                messagebox.showinfo("Успех",
                                                    f"Пользователь {user.name} назначен в комнату {room_num} на этаже {floor_num}.")
                                self.refresh_tree()
                            else:
                                messagebox.showerror("Ошибка",
                                                     f"Не удалось назначить пользователя. Возможно, комната не существует.")
                    except ValueError:
                        messagebox.showerror("Ошибка", "Номер этажа должен быть числом.")
            except ValueError:
                messagebox.showerror("Ошибка", "ID пользователя должен быть числом.")

    def show_residents(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите комнату в дереве.")
            return

        item_values = self.tree.item(selection[0], "values")
        item_text = self.tree.item(selection[0], "text")

        # Проверяем, является ли выбранный элемент комнатой
        if "Комната" in item_text:
            # Извлекаем номер комнаты и этажа из текста
            parts = item_text.split()
            if len(parts) >= 2:
                try:
                    room_number = parts[1]
                    parent_item = self.tree.parent(selection[0])
                    if parent_item:
                        parent_text = self.tree.item(parent_item, "text")  # Например, "Этаж 1"
                        floor_parts = parent_text.split()
                        if len(floor_parts) >= 2:
                            floor_number = int(floor_parts[1])

                            residents = self.manager.get_residents_of_room(floor_number, room_number)
                            if residents:
                                resident_names = "\n".join([f"{u.name} (ID: {u.user_id})" for u in residents])
                                messagebox.showinfo(f"Жильцы комнаты {room_number} (этаж {floor_number})",
                                                    resident_names)
                            else:
                                messagebox.showinfo(f"Жильцы комнаты {room_number} (этаж {floor_number})",
                                                    "В этой комнате никто не проживает.")
                        else:
                            messagebox.showerror("Ошибка", "Не удалось определить этаж для комнаты.")
                except ValueError:
                    messagebox.showerror("Ошибка", "Не удалось определить номер этажа или комнаты из дерева.")
        else:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите именно комнату.")

