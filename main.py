# main.py
# Это точка входа для Android APK

from kivy_gui_app import HouseGUIApp
from manager import HouseManager
import utils # Импортируем, чтобы получить DATA_FILE

# Создаем и загружаем менеджер данных
manager = HouseManager()
manager.load_data() # Загружаем данные при запуске приложения

# Запускаем Kivy GUI, передав ему менеджер
if __name__ == '__main__':
    app = HouseGUIApp(manager_instance=manager)
    app.run()
    # Данные сохраняются в on_stop Kivy приложения