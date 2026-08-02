#!/usr/bin/env python3
"""
Kivy Build Tool - Сборка Kivy приложений через GitHub Actions
НЕ требует Docker, buildozer, Java, Android SDK локально!
Сборка происходит в облаке GitHub.
"""

import os
import sys
import json
import subprocess
import shutil
import argparse
from pathlib import Path
from typing import Optional, Dict, Any

class KivyBuilder:
    def __init__(self, config_path: str = "build_config.json"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.project_dir = Path.cwd()
        
    def load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации"""
        default_config = {
            "app_name": "MyApp",
            "package_name": "com.mycompany.myapp",
            "version": "1.0.0",
            "main_py": "main.py",
            "title": "My Kivy App",
            "orientation": "portrait",
            "permissions": ["INTERNET"],
            "requirements": ["python3", "kivy==2.3.0"],
            "android_sdk": None,
            "android_ndk": None,
            "jdk_path": None
        }
        
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        else:
            self.save_config(default_config)
            
        return default_config
    
    def save_config(self, config: Dict[str, Any]):
        """Сохранение конфигурации"""
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✓ Создан файл конфигурации: {self.config_path}")

    def setup_github_actions(self):
        """Создание workflow файла для сборки APK на GitHub"""
        print("\n🌐 Настройка GitHub Actions для сборки APK...")
        
        github_dir = self.project_dir / ".github" / "workflows"
        github_dir.mkdir(parents=True, exist_ok=True)
        
        workflow_file = github_dir / "build-apk.yml"
        
        reqs_list = self.config.get("requirements", ["python3", "kivy"])
        reqs_str = ", ".join([f"'{r}'" for r in reqs_list])
        
        workflow_content = f"""name: Build Kivy APK

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
  workflow_dispatch: # Позволяет запускать вручную

jobs:
  build-apk:
    runs-on: ubuntu-latest
    container: kivy/python-for-android:latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.x'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt || true
        pip install kivy

    - name: Build APK with p4a
      run: |
        p4a apk --private=. \\
          --package={self.config.get('package_name', 'com.mycompany.myapp')} \\
          --name="{self.config.get('app_name', 'MyApp')}" \\
          --version={self.config.get('version', '1.0.0')} \\
          --permission={",".join(self.config.get('permissions', ['INTERNET']))} \\
          --requirements={",".join(self.config.get('requirements', ['python3', 'kivy']))} \\
          --bootstrap=sdl2 \\
          --orientation={self.config.get('orientation', 'portrait')} \\
          --input={self.config.get('main_py', 'main.py')} \\
          --debug
        
    - name: Upload APK artifact
      uses: actions/upload-artifact@v3
      with:
        name: my-app-apk
        path: dist/*.apk
"""
        
        with open(workflow_file, 'w') as f:
            f.write(workflow_content)
        
        print(f"✅ Создан workflow файл: {workflow_file}")
        print("\n📋 ИНСТРУКЦИЯ ПО СБОРКЕ:")
        print("1. Убедитесь, что ваш проект находится в Git репозитории:")
        print("   git init")
        print("   git add .")
        print("   git commit -m 'Initial commit'")
        print("")
        print("2. Создайте репозиторий на GitHub и запушьте код:")
        print("   git remote add origin https://github.com/ВАШ_НИК/ВАШ_РЕПОЗИТОРИЙ.git")
        print("   git push -u origin main")
        print("")
        print("3. Перейдите на вкладку 'Actions' в вашем репозитории на GitHub.")
        print("   Там вы увидите запущенный процесс сборки 'Build Kivy APK'.")
        print("")
        print("4. После завершения сборки (10-20 минут) скачайте APK:")
        print("   - Нажмите на успешный запуск (зеленая галочка)")
        print("   - Внизу страницы в разделе 'Artifacts' нажмите на 'my-app-apk'")
        print("   - APK файл загрузится на ваш компьютер")
        print("")
        print("💡 Теперь при каждом пуше в репозиторий APK будет собираться автоматически!")
        print("   Вы также можете запустить сборку вручную через кнопку 'Run workflow'.")

    def build_android_cloud(self):
        """Запуск сборки через GitHub Actions"""
        if not (self.project_dir / ".git").exists():
            print("\n⚠️  Это не Git репозиторий!")
            print("Для работы GitHub Actions необходимо инициализировать Git:")
            print("  git init")
            print("  git add .")
            print("  git commit -m 'Init'")
            response = input("\nИнициализировать Git сейчас? (y/n): ")
            if response.lower() == 'y':
                subprocess.run(["git", "init"], check=True)
                subprocess.run(["git", "add", "."], check=True)
                subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)
                print("✅ Git инициализирован")
            else:
                print("❌ Без Git репозитория сборка невозможна")
                sys.exit(1)

        self.setup_github_actions()
        
        print("\n✅ Готово! Файл workflow создан.")
        print("Теперь вам нужно запушить изменения на GitHub, чтобы запустить сборку.")
        print("Команда: git push")

    def build_desktop(self, mode: str = "release"):
        """Сборка для Desktop через PyInstaller"""
        print("\n💻 Сборка для Desktop...")
        
        try:
            subprocess.run(["pyinstaller", "--version"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("Установка PyInstaller...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        
        main_py = self.config.get("main_py", "main.py")
        app_name = self.config.get("app_name", "MyApp")
        
        cmd = [
            "pyinstaller",
            "--onefile",
            "--name", app_name,
            "--windowed" if mode == "release" else "--console",
            main_py
        ]
        
        print(f"Выполнение: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        
        print("\n✅ Desktop сборка завершена!")
        print(f"Исполняемый файл в: {self.project_dir}/dist/")
    
    def init_project(self):
        """Инициализация проекта Kivy"""
        print("\n📁 Инициализация проекта Kivy...")
        
        main_py = self.project_dir / self.config.get("main_py", "main.py")
        if not main_py.exists():
            main_content = '''from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label


class MainApp(App):
    def build(self):
        self.title = "{}"
        layout = BoxLayout(orientation='vertical')
        
        label = Label(text='Hello from Kivy!', font_size=24)
        button = Button(text='Click me!')
        button.bind(on_press=self.on_button_press)
        
        layout.add_widget(label)
        layout.add_widget(button)
        return layout
    
    def on_button_press(self, instance):
        print("Button pressed!")


if __name__ == '__main__':
    MainApp().run()
'''.format(self.config.get("title", "My Kivy App"))
            
            with open(main_py, 'w') as f:
                f.write(main_content)
            print(f"✓ Создан {main_py}")
        
        # Создаем requirements.txt если нет
        req_file = self.project_dir / "requirements.txt"
        if not req_file.exists():
            with open(req_file, 'w') as f:
                f.write("kivy\n")
            print("✓ Создан requirements.txt")

        # Создаем .gitignore
        gitignore = self.project_dir / ".gitignore"
        if not gitignore.exists():
            with open(gitignore, 'w') as f:
                f.write("""__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
*.spec.lock
.github/
""")
            print("✓ Создан .gitignore")
        
        print("\n✓ Проект инициализирован!")
        print(f"  Запустите: python {main_py}")

    def clean(self):
        """Очистка временных файлов"""
        print("\n🧹 Очистка...")
        
        dirs_to_clean = ['dist', 'build', '__pycache__', '.buildozer']
        for d in dirs_to_clean:
            path = self.project_dir / d
            if path.exists():
                shutil.rmtree(path)
                print(f"  Удалено: {d}")
        
        files_to_clean = list(self.project_dir.glob("*.spec"))
        for f in files_to_clean:
            f.unlink()
            print(f"  Удалено: {f}")
        
        print("✓ Очистка завершена")


def main():
    parser = argparse.ArgumentParser(description="Kivy Build Tool (через GitHub Actions)")
    subparsers = parser.add_subparsers(dest="command", help="Команды")
    
    # build команда
    build_parser = subparsers.add_parser("build", help="Сборка приложения")
    build_parser.add_argument("--target", choices=["android", "desktop"], required=True)
    build_parser.add_argument("--mode", choices=["debug", "release"], default="debug")
    
    # init команда
    subparsers.add_parser("init", help="Инициализация проекта")
    
    # clean команда
    subparsers.add_parser("clean", help="Очистка временных файлов")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    builder = KivyBuilder()
    
    print("=" * 60)
    print("Kivy Build Tool - Сборка через GitHub Actions")
    print("=" * 60)
    if hasattr(args, 'target'):
        print(f"Цель: {args.target}")
    if hasattr(args, 'mode'):
        print(f"Режим: {args.mode}")
    print("=" * 60)
    
    if args.command == "build":
        if args.target == "android":
            builder.build_android_cloud()
        elif args.target == "desktop":
            builder.build_desktop(args.mode)
    elif args.command == "init":
        builder.init_project()
    elif args.command == "clean":
        builder.clean()


if __name__ == "__main__":
    main()
