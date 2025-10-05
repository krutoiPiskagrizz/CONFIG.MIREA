
"""
Скрипт для создания тестовых структур VFS
"""

import os
import sys

def create_minimal_vfs():
    """Создание минимальной VFS структуры"""
    os.makedirs("vfs_minimal", exist_ok=True)
    
    # Создаем motd файл
    with open("vfs_minimal/motd", "w", encoding="utf-8") as f:
        f.write("Добро пожаловать в минимальную VFS!\nЭто тестовое сообщение MOTD.\n")
    
    print("Создана минимальная VFS: vfs_minimal/")

def create_medium_vfs():
    """Создание VFS с несколькими файлами"""
    base_dir = "vfs_medium"
    os.makedirs(f"{base_dir}/home/user/documents", exist_ok=True)
    os.makedirs(f"{base_dir}/home/user/downloads", exist_ok=True)
    os.makedirs(f"{base_dir}/etc", exist_ok=True)
    os.makedirs(f"{base_dir}/var/log", exist_ok=True)
    
    # Создаем файлы
    with open(f"{base_dir}/motd", "w", encoding="utf-8") as f:
        f.write("VFS со средней структурой файлов\n")
    
    with open(f"{base_dir}/home/user/readme.txt", "w", encoding="utf-8") as f:
        f.write("Это файл readme в домашней директории\n")
    
    with open(f"{base_dir}/home/user/documents/report.txt", "w", encoding="utf-8") as f:
        f.write("Важный отчет\nСтрока 1\nСтрока 2\n")
    
    with open(f"{base_dir}/etc/config.conf", "w", encoding="utf-8") as f:
        f.write("# Конфигурационный файл\nsetting1=value1\nsetting2=value2\n")
    
    print("Создана средняя VFS: vfs_medium/")

def create_complex_vfs():
    """Создание сложной VFS с 3+ уровнями вложенности"""
    base_dir = "vfs_complex"
    
    # Создаем сложную структуру директорий
    structure = [
        f"{base_dir}/home/user/projects/python/app/src",
        f"{base_dir}/home/user/projects/python/app/tests", 
        f"{base_dir}/home/user/projects/javascript/web/static",
        f"{base_dir}/home/user/projects/javascript/web/templates",
        f"{base_dir}/home/user/documents/work/reports/2024",
        f"{base_dir}/home/user/documents/work/presentations",
        f"{base_dir}/home/user/music/artists/rock/classic",
        f"{base_dir}/home/user/music/artists/jazz",
        f"{base_dir}/etc/system/network",
        f"{base_dir}/etc/system/security",
        f"{base_dir}/var/log/system",
        f"{base_dir}/var/log/application",
        f"{base_dir}/tmp/cache/images",
        f"{base_dir}/tmp/cache/data"
    ]
    
    for directory in structure:
        os.makedirs(directory, exist_ok=True)
    
    # Создаем различные файлы
    with open(f"{base_dir}/motd", "w", encoding="utf-8") as f:
        f.write("=== Сложная VFS структура ===\n")
        f.write("Эта VFS содержит 3+ уровня вложенности\n")
        f.write("для тестирования навигации и команд\n")
    
    # Файлы в разных директориях
    files = {
        f"{base_dir}/home/user/projects/python/app/src/main.py": "print('Hello from main')\n\nclass App:\n    def run(self):\n        print('App running')",
        f"{base_dir}/home/user/projects/python/app/src/utils.py": "def helper():\n    return 'helper function'",
        f"{base_dir}/home/user/projects/python/app/readme.md": "# Python Project\n\nЭто тестовый проект",
        f"{base_dir}/home/user/documents/work/reports/2024/january.txt": "Отчет за январь 2024\n\nПункт 1\nПункт 2",
        f"{base_dir}/home/user/documents/work/reports/2024/february.txt": "Отчет за февраль 2024\n\nДостижения:\n- Задача 1\n- Задача 2",
        f"{base_dir}/etc/system/network/interfaces": "# Network interfaces\nauto lo\niface lo inet loopback",
        f"{base_dir}/var/log/system/syslog": "2024-01-01 10:00:00 INFO: System started\n2024-01-01 10:01:00 INFO: Services loaded",
        f"{base_dir}/home/user/.bashrc": "# Bash configuration\nexport PATH=$PATH:/home/user/bin",
    }
    
    for filepath, content in files.items():
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
    
    print("Создана сложная VFS: vfs_complex/")

def create_test_scripts():
    """Создание тестовых скриптов для VFS"""
    
    # Скрипт для тестирования VFS
    with open("test_vfs.sh", "w", encoding="utf-8") as f:
        f.write("""#!/bin/bash
# Тестирование работы с VFS
echo "=== Тестирование VFS ==="

echo "1. Тестирование минимальной VFS:"
python shell_emulator.py --vfs vfs_minimal --log logs/vfs_minimal_log.xml

echo "2. Тестирование средней VFS:"
python shell_emulator.py --vfs vfs_medium --log logs/vfs_medium_log.xml

echo "3. Тестирование сложной VFS:"
python shell_emulator.py --vfs vfs_complex --log logs/vfs_complex_log.xml

echo "4. Тестирование без VFS:"
python shell_emulator.py --log logs/no_vfs_log.xml

echo "Тестирование VFS завершено!"
""")
    
    # Скрипт для демонстрации всех возможностей
    with open("vfs_demo_script.sh", "w", encoding="utf-8") as f:
        f.write("""#!/bin/bash
# Демонстрационный скрипт для VFS
echo "=== Демонстрация VFS возможностей ==="

# Навигация по файловой системе
pwd
ls
cd home/user
pwd
ls

# Работа с файлами
cd projects/python/app
pwd
ls
cat readme.md
cd src
ls
cat main.py

# Возврат и исследование других путей
cd /home/user/documents/work/reports/2024
pwd
ls
cat january.txt

# Попытка доступа к несуществующим файлам
cd /nonexistent
cat unknown_file.txt

# Возврат в корень и вывод MOTD
cd /
ls

echo "=== Демонстрация завершена ==="
""")
    
    os.chmod("test_vfs.sh", 0o755)
    os.chmod("vfs_demo_script.sh", 0o755)
    print("Созданы тестовые скрипты: test_vfs.sh, vfs_demo_script.sh")

if __name__ == "__main__":
    # Создаем папку для логов
    os.makedirs("logs", exist_ok=True)
    
    # Создаем тестовые VFS
    create_minimal_vfs()
    create_medium_vfs() 
    create_complex_vfs()
    create_test_scripts()
    
    print("\n=== Все тестовые структуры созданы ===")
    print("Запусти тесты: ./test_vfs.sh")