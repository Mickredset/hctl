# kivy_gui_app.py
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.treeview import TreeView, TreeViewLabel
# Импортируем HouseManager из manager.py
from manager import HouseManager


class HouseGUIApp(App):
    def __init__(self, manager_instance, **kwargs):
        super().__init__(**kwargs)
        # Принимаем экземпляр менеджера из main.py
        self.manager = manager_instance

    def build(self):
        # Основной макет
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Панель кнопок
        button_layout = GridLayout(cols=3, size_hint_y=None, height=50, spacing=5)
        self.add_floor_btn = Button(text='Добавить Этаж')
        self.add_floor_btn.bind(on_press=self.add_floor_popup)
        self.add_room_btn = Button(text='Добавить Комната')
        self.add_room_btn.bind(on_press=self.add_room_popup)
        self.create_user_btn = Button(text='Создать Пользователя')
        self.create_user_btn.bind(on_press=self.create_user_popup)
        self.assign_user_btn = Button(text='Назначить в Комната')
        self.assign_user_btn.bind(on_press=self.assign_user_popup)
        self.show_residents_btn = Button(text='Показать Жильцов')
        # --- ИСПРАВЛЕНО: Убраны скобки ---
        self.show_residents_btn.bind(on_press=self.show_residents_popup)
        # ------------------------------

        button_layout.add_widget(self.add_floor_btn)
        button_layout.add_widget(self.add_room_btn)
        button_layout.add_widget(self.create_user_btn)
        button_layout.add_widget(self.assign_user_btn)
        button_layout.add_widget(self.show_residents_btn)
        # Зарезервируем место для пятой кнопки, если нужно будет добавить
        button_layout.add_widget(Label())

        main_layout.add_widget(button_layout)

        # TreeView для отображения этажей/комнат
        self.tree_view = TreeView(root_options=dict(text='Дом'))
        self.tree_view.size_hint_y = 1
        scroll = ScrollView()
        scroll.add_widget(self.tree_view)
        main_layout.add_widget(scroll)

        self.refresh_tree()

        return main_layout

    def refresh_tree(self):
        """Обновляет содержимое дерева."""
        # Очищаем текущее содержимое, кроме корня
        for node in list(self.tree_view.iterate_all_nodes()):
            if node != self.tree_view.root:
                self.tree_view.remove_node(node)

        # Заполняем дерево данными
        for floor_num in self.manager.get_all_floors_numbers():
            floor_label = TreeViewLabel(text=f'Этаж {floor_num}')
            self.tree_view.add_node(floor_label)
            for room_num in self.manager.get_rooms_on_floor(floor_num):
                room = self.manager.floors[floor_num].get_room(room_num)
                resident_count = len(room.residents)
                room_label = TreeViewLabel(text=f'Комната {room_num} ({room.room_type}, Жильцы: {resident_count})')
                # --- ДОБАВЛЕНЫ АТРИБУТЫ ---
                room_label.floor_num = floor_num
                room_label.room_num = room_num
                # --------------------------
                self.tree_view.add_node(room_label, floor_label)

    def _show_message(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.6, 0.4))
        popup.open()

    def add_floor_popup(self, instance):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        floor_input = TextInput(multiline=False, hint_text='Номер этажа')
        layout.add_widget(Label(text='Введите номер этажа:'))
        layout.add_widget(floor_input)

        def confirm_add_floor(instance):
            try:
                floor_num = int(floor_input.text)
                if self.manager.add_floor(floor_num):
                    self._show_message('Успех', f'Этаж {floor_num} добавлен.')
                    self.refresh_tree()
                else:
                    self._show_message('Предупреждение', f'Этаж {floor_num} уже существует.')
            except ValueError:
                self._show_message('Ошибка', 'Номер этажа должен быть числом.')
            popup.dismiss()

        button_layout = BoxLayout(size_hint_y=None, height=40, spacing=5)
        confirm_btn = Button(text='OK')
        confirm_btn.bind(on_press=confirm_add_floor)
        cancel_btn = Button(text='Отмена')
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        button_layout.add_widget(confirm_btn)
        button_layout.add_widget(cancel_btn)

        layout.add_widget(button_layout)

        popup = Popup(title='Добавить Этаж', content=layout, size_hint=(0.6, 0.4))
        popup.open()

    def add_room_popup(self, instance):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        floor_input = TextInput(multiline=False, hint_text='Номер этажа')
        room_input = TextInput(multiline=False, hint_text='Номер комнаты')
        type_input = TextInput(multiline=False, hint_text='Тип комнаты (Обычная)')
        layout.add_widget(Label(text='Введите номер этажа:'))
        layout.add_widget(floor_input)
        layout.add_widget(Label(text='Введите номер комнаты:'))
        layout.add_widget(room_input)
        layout.add_widget(Label(text='Введите тип комнаты:'))
        layout.add_widget(type_input)

        def confirm_add_room(instance):
            try:
                floor_num = int(floor_input.text)
                if floor_num not in self.manager.get_all_floors_numbers():
                    self._show_message('Ошибка', f'Этаж {floor_num} не существует.')
                    popup.dismiss()
                    return
                room_num = room_input.text
                room_type = type_input.text if type_input.text else "Обычная"

                if self.manager.add_room_to_floor(floor_num, room_num, room_type):
                    self._show_message('Успех', f'Комната {room_num} добавлена на этаж {floor_num}.')
                    self.refresh_tree()
                else:
                    self._show_message('Предупреждение', f'Комната {room_num} уже существует на этаже {floor_num}.')
            except ValueError:
                self._show_message('Ошибка', 'Номер этажа должен быть числом.')
            popup.dismiss()

        button_layout = BoxLayout(size_hint_y=None, height=40, spacing=5)
        confirm_btn = Button(text='OK')
        confirm_btn.bind(on_press=confirm_add_room)
        cancel_btn = Button(text='Отмена')
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        button_layout.add_widget(confirm_btn)
        button_layout.add_widget(cancel_btn)

        layout.add_widget(button_layout)

        popup = Popup(title='Добавить Комната', content=layout, size_hint=(0.6, 0.4))
        popup.open()

    def create_user_popup(self, instance):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        name_input = TextInput(multiline=False, hint_text='Имя')
        age_input = TextInput(multiline=False, hint_text='Возраст (необязательно)')
        email_input = TextInput(multiline=False, hint_text='Email (необязательно)')
        layout.add_widget(Label(text='Введите имя пользователя:'))
        layout.add_widget(name_input)
        layout.add_widget(Label(text='Введите возраст (необязательно):'))
        layout.add_widget(age_input)
        layout.add_widget(Label(text='Введите email (необязательно):'))
        layout.add_widget(email_input)

        def confirm_create_user(instance):
            name = name_input.text
            if not name:
                self._show_message('Ошибка', 'Имя не может быть пустым.')
                return
            age = int(age_input.text) if age_input.text and age_input.text.isdigit() else None
            email = email_input.text if email_input.text else None

            user_id = self.manager.create_user(name, age, email)
            self._show_message('Успех', f'Пользователь \'{name}\' создан с ID {user_id}.')
            popup.dismiss()

        button_layout = BoxLayout(size_hint_y=None, height=40, spacing=5)
        confirm_btn = Button(text='OK')
        confirm_btn.bind(on_press=confirm_create_user)
        cancel_btn = Button(text='Отмена')
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        button_layout.add_widget(confirm_btn)
        button_layout.add_widget(cancel_btn)

        layout.add_widget(button_layout)

        popup = Popup(title='Создать Пользователя', content=layout, size_hint=(0.6, 0.4))
        popup.open()

    def assign_user_popup(self, instance):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        user_id_input = TextInput(multiline=False, hint_text='ID пользователя')
        floor_input = TextInput(multiline=False, hint_text='Номер этажа')
        room_input = TextInput(multiline=False, hint_text='Номер комнаты')
        layout.add_widget(Label(text='Введите ID пользователя:'))
        layout.add_widget(user_id_input)
        layout.add_widget(Label(text='Введите номер этажа:'))
        layout.add_widget(floor_input)
        layout.add_widget(Label(text='Введите номер комнаты:'))
        layout.add_widget(room_input)

        def confirm_assign_user(instance):
            try:
                user_id = int(user_id_input.text)
                floor_num = int(floor_input.text)
                room_num = room_input.text

                user = self.manager.get_user_by_id(user_id)
                if not user:
                    self._show_message('Ошибка', f'Пользователь с ID {user_id} не найден.')
                    popup.dismiss()
                    return
                if floor_num not in self.manager.get_all_floors_numbers():
                    self._show_message('Ошибка', f'Этаж {floor_num} не существует.')
                    popup.dismiss()
                    return

                if self.manager.assign_user_to_room(user_id, floor_num, room_num):
                    self._show_message('Успех',
                                       f'Пользователь {user.name} назначен в комнату {room_num} на этаже {floor_num}.')
                    self.refresh_tree()
                else:
                    self._show_message('Ошибка', f'Не удалось назначить пользователя. Возможно, комната не существует.')
            except ValueError:
                self._show_message('Ошибка', 'ID пользователя и номер этажа должны быть числами.')
            popup.dismiss()

        button_layout = BoxLayout(size_hint_y=None, height=40, spacing=5)
        confirm_btn = Button(text='OK')
        confirm_btn.bind(on_press=confirm_assign_user)
        cancel_btn = Button(text='Отмена')
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        button_layout.add_widget(confirm_btn)
        button_layout.add_widget(cancel_btn)

        layout.add_widget(button_layout)

        popup = Popup(title='Назначить в Комната', content=layout, size_hint=(0.6, 0.4))
        popup.open()

    def show_residents_popup(self, instance):
        # --- ИСПРАВЛЕНО: Используем selected_node вместо selected_nodes ---
        node = self.tree_view.selected_node
        if not node:
            self._show_message('Предупреждение', 'Выберите комнату в дереве.')
            return
        # ----------------------------------------------------------

        # Проверяем, является ли выбранный элемент комнатой (имеет атрибуты floor_num и room_num)
        # Также проверим, что атрибуты существуют, прежде чем их использовать
        floor_num = getattr(node, 'floor_num', None)
        room_num = getattr(node, 'room_num', None)

        if floor_num is not None and room_num is not None:
            residents = self.manager.get_residents_of_room(floor_num, room_num)
            if residents:
                resident_text = "\n".join([f"{u.name} (ID: {u.user_id})" for u in residents])
                self._show_message(f'Жильцы комнаты {room_num} (этаж {floor_num})', resident_text)
            else:
                self._show_message(f'Жильцы комнаты {room_num} (этаж {floor_num})',
                                   'В этой комнате никто не проживает.')
        else:
            self._show_message('Предупреждение', 'Пожалуйста, выберите именно комнату.')

    def on_stop(self):
        """Сохраняем данные при закрытии приложения."""
        self.manager.save_data()
