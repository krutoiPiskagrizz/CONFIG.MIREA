import tkinter as tk
from tkinter import scrolledtext, Entry, Frame, messagebox
import os
import sys
import argparse
import logging
import xml.etree.ElementTree as ET
from datetime import datetime
import subprocess
import platform
from collections import defaultdict

class VFSNode:
    """Узел виртуальной файловой системы"""
    def __init__(self, name, is_directory=False, content=""):
        self.name = name
        self.is_directory = is_directory
        self.content = content
        self.children = {} if is_directory else None
        self.parent = None

class VirtualFileSystem:
    """Виртуальная файловая система"""
    def __init__(self, physical_path=None):
        self.root = VFSNode("", is_directory=True)
        self.current_dir = self.root
        self.physical_path = physical_path
        
        # Создаем базовую структуру VFS
        self.create_default_structure()
        
        # Загружаем из физической директории если указана
        if physical_path and os.path.exists(physical_path):
            self.load_from_physical_path(physical_path)
    
    def create_default_structure(self):
        """Создание базовой структуры VFS"""
        # Создаем домашнюю директорию
        home = self.mkdir("home", self.root)
        user = self.mkdir("user", home)
        
        # Создаем несколько тестовых файлов и папок
        documents = self.mkdir("documents", user)
        downloads = self.mkdir("downloads", user)
        temp = self.mkdir("temp", user)
        
        # Создаем тестовые файлы с разным содержимым
        self.create_file("readme.txt", user, "Добро пожаловать в эмулятор!\nЭто файл readme.")
        self.create_file("test.py", user, "print('Hello World')\n\nclass Test:\n    def method(self):\n        return True")
        self.create_file("data.txt", user, "Строка 1\nСтрока 2\nСтрока 3\nСтрока 4\nСтрока 5")
        self.create_file("empty.txt", user, "")
        self.create_file("source.txt", temp, "Исходный файл для копирования\nСодержимое исходного файла")
        
        self.create_file("report.md", documents, "# Отчет\n\n## Раздел 1\nТекст раздела 1\n\n## Раздел 2\nТекст раздела 2")
        self.create_file("notes.txt", documents, "Заметка 1\nЗаметка 2\nЗаметка 3")
        
        # Создаем тестовые директории для rmdir
        self.mkdir("empty_dir", user)
        self.mkdir("dir_with_files", user)
        self.create_file("file1.txt", self.mkdir("dir_with_files", user), "Файл 1")
        self.create_file("file2.txt", self.mkdir("dir_with_files", user), "Файл 2")
        
        # Создаем системуные директории
        etc = self.mkdir("etc", self.root)
        self.mkdir("var", self.root)
        self.mkdir("tmp", self.root)
        
        # Создаем конфигурационные файлы
        self.create_file("version", etc, "EmulatorOS 1.0")
        self.create_file("hostname", etc, "emulator-host")
    
    def load_from_physical_path(self, physical_path):
        """Загрузка VFS из физической директории"""
        try:
            for root_dir, dirs, files in os.walk(physical_path):
                # Вычисляем VFS путь
                rel_path = os.path.relpath(root_dir, physical_path)
                vfs_dir = self.current_dir
                
                if rel_path != ".":
                    path_parts = rel_path.split(os.sep)
                    for part in path_parts:
                        if part in vfs_dir.children:
                            vfs_dir = vfs_dir.children[part]
                        else:
                            vfs_dir = self.mkdir(part, vfs_dir)
                
                # Создаем директории
                for dir_name in dirs:
                    self.mkdir(dir_name, vfs_dir)
                
                # Создаем файлы
                for file_name in files:
                    file_path = os.path.join(root_dir, file_name)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        self.create_file(file_name, vfs_dir, content)
                    except:
                        self.create_file(file_name, vfs_dir, f"Бинарный файл {file_name}")
            
            print(f"VFS загружена из: {physical_path}")
        except Exception as e:
            print(f"Ошибка загрузки VFS: {e}")
    
    def mkdir(self, name, parent=None):
        """Создание директории в VFS"""
        if parent is None:
            parent = self.current_dir
        
        if not parent.is_directory:
            return None
        
        if name in parent.children:
            return parent.children[name]
        
        new_dir = VFSNode(name, is_directory=True)
        new_dir.parent = parent
        parent.children[name] = new_dir
        return new_dir
    
    def create_file(self, name, parent=None, content=""):
        """Создание файла в VFS"""
        if parent is None:
            parent = self.current_dir
        
        if not parent.is_directory:
            return None
        
        new_file = VFSNode(name, is_directory=False, content=content)
        new_file.parent = parent
        parent.children[name] = new_file
        return new_file
    
    def remove_directory(self, name, parent=None):
        """Удаление директории из VFS"""
        if parent is None:
            parent = self.current_dir
        
        if not parent.is_directory:
            return False, "Родительский узел не является директорией"
        
        if name not in parent.children:
            return False, f"Директория '{name}' не найдена"
        
        node = parent.children[name]
        
        if not node.is_directory:
            return False, f"'{name}' не является директорией"
        
        if node.children and len(node.children) > 0:
            return False, f"Директория '{name}' не пуста"
        
        # Удаляем директорию
        del parent.children[name]
        return True, f"Директория '{name}' удалена"
    
    def copy_file(self, source_name, target_name, source_parent=None, target_parent=None):
        """Копирование файла в VFS"""
        if source_parent is None:
            source_parent = self.current_dir
        if target_parent is None:
            target_parent = self.current_dir
        
        if not source_parent.is_directory or not target_parent.is_directory:
            return False, "Родительские узлы не являются директориями"
        
        if source_name not in source_parent.children:
            return False, f"Исходный файл '{source_name}' не найден"
        
        source_node = source_parent.children[source_name]
        
        if source_node.is_directory:
            return False, f"'{source_name}' является директорией (используйте рекурсивное копирование)"
        
        # Создаем копию файла
        self.create_file(target_name, target_parent, source_node.content)
        return True, f"Файл '{source_name}' скопирован в '{target_name}'"
    
    def change_directory(self, path):
        """Смена текущей директории в VFS"""
        if path == "/":
            self.current_dir = self.root
            return True
        
        if path == "..":
            if self.current_dir.parent:
                self.current_dir = self.current_dir.parent
            return True
        
        if path == "~":
            # Переход в домашнюю директорию (/home/user)
            home_user = self._find_node("/home/user")
            if home_user:
                self.current_dir = home_user
                return True
            return False
        
        # Поиск по относительному пути
        target_dir = self.current_dir
        parts = path.split('/')
        
        for part in parts:
            if not part:  # Пропускаем пустые части
                continue
                
            if part == "..":
                if target_dir.parent:
                    target_dir = target_dir.parent
                continue
            elif part == ".":
                continue
            elif part == "~":
                home_user = self._find_node("/home/user")
                if home_user:
                    target_dir = home_user
                else:
                    return False
            elif part in target_dir.children and target_dir.children[part].is_directory:
                target_dir = target_dir.children[part]
            else:
                return False
        
        self.current_dir = target_dir
        return True
    
    def _find_node(self, path):
        """Поиск узла по абсолютному пути"""
        if path == "/":
            return self.root
        
        parts = path.strip('/').split('/')
        current = self.root
        
        for part in parts:
            if part in current.children:
                current = current.children[part]
            else:
                return None
        
        return current
    
    def get_current_path(self):
        """Получение текущего пути в VFS"""
        path_parts = []
        current = self.current_dir
        
        while current and current.parent:  # Поднимаемся до корня
            path_parts.append(current.name)
            current = current.parent
        
        return "/" + "/".join(reversed(path_parts)) if path_parts else "/"
    
    def list_directory(self, path=None, show_hidden=False, long_format=False):
        """Список содержимого директории"""
        target_dir = self.current_dir
        
        if path:
            # Временное изменение директории для листинга
            original_dir = self.current_dir
            if self.change_directory(path):
                target_dir = self.current_dir
                self.current_dir = original_dir
            else:
                return None
        
        if not target_dir.is_directory or not target_dir.children:
            return []
        
        items = []
        for name, node in target_dir.children.items():
            # Пропускаем скрытые файлы если не запрошены
            if not show_hidden and name.startswith('.'):
                continue
                
            if long_format:
                # Длинный формат: тип, размер, имя
                if node.is_directory:
                    item_type = "d"
                    size = "4096"  # Размер директории
                else:
                    item_type = "-"
                    size = str(len(node.content.encode('utf-8')))  # Размер файла в байтах
                
                items.append(f"{item_type}rw-r--r-- 1 user user {size} Jan 01 00:00 {name}{'/' if node.is_directory else ''}")
            else:
                # Короткий формат
                items.append(f"{name}{'/' if node.is_directory else ''}")
        
        return sorted(items)
    
    def get_file_stats(self, filename):
        """Получение статистики файла для wc"""
        current_dir = self.current_dir
        
        if filename in current_dir.children and not current_dir.children[filename].is_directory:
            content = current_dir.children[filename].content
            lines = content.split('\n')
            words = content.split()
            chars = len(content)
            
            return {
                'lines': len(lines) if content else 0,
                'words': len(words),
                'chars': chars,
                'bytes': len(content.encode('utf-8'))
            }
        
        return None
    
    def get_motd(self):
        """Получение сообщения MOTD из корня VFS"""
        if "motd" in self.root.children and not self.root.children["motd"].is_directory:
            return self.root.children["motd"].content
        return None

class ShellEmulator:
    def __init__(self, root, vfs_path=None, log_file=None, startup_script=None):
        self.root = root
        self.username = os.getenv('USERNAME') or os.getenv('USER')
        self.hostname = os.uname().nodename if hasattr(os, 'uname') else os.getenv('COMPUTERNAME', 'localhost')
        
        # Параметры конфигурации
        self.vfs_path = vfs_path
        self.log_file = log_file
        self.startup_script = startup_script
        
        # Инициализация VFS
        self.vfs = VirtualFileSystem(vfs_path)
        
        # Настройка логирования
        self.setup_logging()
        
        # Логирование параметров запуска
        self.log_event("startup", f"Эмулятор запущен с параметрами: VFS={vfs_path}, LOG={log_file}, SCRIPT={startup_script}")
        
        # Установка заголовка окна
        self.root.title(f"Эмулятор - [{self.username}@{self.hostname}]")
        
        # Создание интерфейса
        self.create_widgets()
        
        # Приветственное сообщение
        self.output_area_insert(f"Добро пожаловать в эмулятор командной оболочки!\n")
        self.output_area_insert(f"Текущий пользователь: {self.username}@{self.hostname}\n")
        
        # Вывод MOTD если есть
        motd = self.vfs.get_motd()
        if motd:
            self.output_area_insert(f"\n=== MOTD ===\n{motd}\n============\n\n")
        
        # Вывод параметров конфигурации
        self.output_area_insert(f"Параметры запуска:\n")
        self.output_area_insert(f"  VFS путь: {vfs_path or 'Не указан'}\n")
        self.output_area_insert(f"  Лог-файл: {log_file or 'Не указан'}\n")
        self.output_area_insert(f"  Стартовый скрипт: {startup_script or 'Не указан'}\n")
        
        self.output_area_insert("Введите 'exit' для выхода или 'help' для списка команд\n\n")
        
        # Выполнение стартового скрипта если указан
        if startup_script and os.path.exists(startup_script):
            self.execute_startup_script(startup_script)
        else:
            self.show_prompt()
        
    def setup_logging(self):
        """Настройка XML логирования"""
        if self.log_file:
            self.log_root = ET.Element("emulator_log")
            self.log_tree = ET.ElementTree(self.log_root)
            os.makedirs(os.path.dirname(self.log_file) if os.path.dirname(self.log_file) else ".", exist_ok=True)
            
    def log_event(self, command, message, error=None):
        """Логирование события в XML формате"""
        if hasattr(self, 'log_root'):
            event = ET.SubElement(self.log_root, "event")
            ET.SubElement(event, "timestamp").text = datetime.now().isoformat()
            ET.SubElement(event, "command").text = command
            ET.SubElement(event, "message").text = message
            if error:
                ET.SubElement(event, "error").text = error
            ET.SubElement(event, "current_dir").text = self.vfs.get_current_path()
            
            try:
                self.log_tree.write(self.log_file, encoding='utf-8', xml_declaration=True)
            except Exception as e:
                print(f"Ошибка записи лога: {e}")
        
    def execute_startup_script(self, script_path):
        """Выполнение стартового скрипта"""
        self.output_area_insert(f"\n=== Выполнение стартового скрипта: {script_path} ===\n")
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    self.output_area_insert(f"[{line_num}] {line}\n")
                    self.process_command(line)
                    
        except Exception as e:
            error_msg = f"Ошибка выполнения скрипта: {e}"
            self.output_area_insert(f"{error_msg}\n")
            self.log_event("script_error", f"Ошибка в строке {line_num}", error=error_msg)
        
        self.output_area_insert("=== Завершение выполнения скрипта ===\n\n")
        self.show_prompt()
        
    def create_widgets(self):
        # Основная рамка
        main_frame = Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Область вывода с прокруткой
        self.output_area = scrolledtext.ScrolledText(
            main_frame, 
            height=20, 
            width=80,
            bg='black',
            fg='white',
            insertbackground='white',
            font=('Courier New', 10)
        )
        self.output_area.pack(fill=tk.BOTH, expand=True)
        self.output_area.config(state=tk.DISABLED)
        
        # Рамка для ввода команды
        input_frame = Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        # Приглашение командной строки
        self.update_prompt()
        
        # Поле ввода команды
        self.command_entry = Entry(
            input_frame,
            bg='black',
            fg='white',
            insertbackground='white',
            font=('Courier New', 10),
            width=60
        )
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.command_entry.bind('<Return>', self.execute_command)
        self.command_entry.focus()
        
    def update_prompt(self):
        """Обновление приглашения командной строки"""
        current_path = self.vfs.get_current_path()
        short_path = current_path.replace('/home/user', '~') if current_path.startswith('/home/user') else current_path
        
        if hasattr(self, 'prompt_label'):
            self.prompt_label.config(text=f"{self.username}@{self.hostname}:{short_path}$ ")
        else:
            self.prompt_label = tk.Label(
                self.root.winfo_children()[0].winfo_children()[1],  # input_frame
                text=f"{self.username}@{self.hostname}:{short_path}$ ",
                bg='black',
                fg='green',
                font=('Courier New', 10, 'bold')
            )
            self.prompt_label.pack(side=tk.LEFT)
        
    def output_area_insert(self, text):
        """Вставка текста в область вывода"""
        self.output_area.config(state=tk.NORMAL)
        self.output_area.insert(tk.END, text)
        self.output_area.config(state=tk.DISABLED)
        self.output_area.see(tk.END)
        
    def show_prompt(self):
        self.update_prompt()
        self.output_area_insert(f"{self.username}@{self.hostname}:{self.vfs.get_current_path().replace('/home/user', '~')}$ ")
        
    def process_command(self, command_text):
        """Обработка команды"""
        if not command_text:
            return
            
        parts = command_text.split()
        command = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        # Логирование вызова команды
        self.log_event(command, f"Выполнение команды: {command_text}")
        
        # Обработка команд
        if command == "exit":
            self.root.quit()
        elif command == "ls":
            self.cmd_ls(args)
        elif command == "cd":
            self.cmd_cd(args)
        elif command == "help":
            self.cmd_help()
        elif command == "echo":
            self.cmd_echo(args)
        elif command == "pwd":
            self.cmd_pwd(args)
        elif command == "cat":
            self.cmd_cat(args)
        elif command == "uname":
            self.cmd_uname(args)
        elif command == "wc":
            self.cmd_wc(args)
        elif command == "rmdir":
            self.cmd_rmdir(args)
        elif command == "cp":
            self.cmd_cp(args)
        else:
            error_msg = f"Ошибка: неизвестная команда '{command}'"
            self.output_area_insert(f"{error_msg}\n")
            self.log_event(command, f"Неизвестная команда: {command}", error=error_msg)
        
    def execute_command(self, event):
        command_text = self.command_entry.get().strip()
        self.command_entry.delete(0, tk.END)
        
        if not command_text:
            self.show_prompt()
            return
            
        self.output_area_insert(f"{command_text}\n")
        self.process_command(command_text)
        self.show_prompt()
        
    def cmd_ls(self, args):
        """Команда ls - список файлов VFS с поддержкой опций"""
        show_hidden = False
        long_format = False
        path = None
        
        # Парсинг аргументов
        i = 0
        while i < len(args):
            if args[i].startswith('-'):
                if 'a' in args[i]:
                    show_hidden = True
                if 'l' in args[i]:
                    long_format = True
            else:
                path = args[i]
            i += 1
        
        items = self.vfs.list_directory(path, show_hidden, long_format)
        
        if items is None:
            error_msg = f"Ошибка: директория '{path}' не найдена"
            self.output_area_insert(f"{error_msg}\n")
            self.log_event("ls", f"Директория не найдена: {path}", error=error_msg)
            return
            
        if not items:
            self.output_area_insert("Директория пуста\n")
            return
            
        # Вывод
        for item in items:
            self.output_area_insert(f"{item}\n")
        
    def cmd_cd(self, args):
        """Команда cd - смена директории VFS"""
        if len(args) == 0:
            path = "~"  # Домашняя директория
        elif len(args) == 1:
            path = args[0]
        else:
            error_msg = "Ошибка: неверное количество аргументов для cd"
            self.output_area_insert(f"{error_msg}\n")
            self.log_event("cd", f"Неверные аргументы: {args}", error=error_msg)
            return
        
        if self.vfs.change_directory(path):
            self.output_area_insert(f"Переход в директорию: {self.vfs.get_current_path()}\n")
        else:
            error_msg = f"Ошибка: директория '{path}' не найдена"
            self.output_area_insert(f"{error_msg}\n")
            self.log_event("cd", f"Директория не найдена: {path}", error=error_msg)
            
    def cmd_cat(self, args):
        """Команда cat - вывод содержимого файла"""
        if not args:
            error_msg = "Ошибка: не указан файл"
            self.output_area_insert(f"{error_msg}\n")
            self.log_event("cat", "Не указан файл", error=error_msg)
            return
            
        for filename in args:
            current_dir = self.vfs.current_dir
            
            if filename in current_dir.children and not current_dir.children[filename].is_directory:
                file_content = current_dir.children[filename].content
                self.output_area_insert(f"{file_content}\n")
            else:
                error_msg = f"Ошибка: файл '{filename}' не найден"
                self.output_area_insert(f"{error_msg}\n")
                self.log_event("cat", f"Файл не найден: {filename}", error=error_msg)
    
    def cmd_uname(self, args):
        """Команда uname - информация о системе"""
        show_all = False
        show_kernel = False
        show_hostname = False
        
        # Парсинг аргументов
        for arg in args:
            if arg == "-a":
                show_all = True
            elif arg == "-s":
                show_kernel = True
            elif arg == "-n":
                show_hostname = True
        
        # Если нет аргументов или показать все
        if not args or show_all:
            self.output_area_insert(f"EmulatorOS 1.0 {self.hostname} 2024-01-01\n")
        elif show_kernel:
            self.output_area_insert("EmulatorOS\n")
        elif show_hostname:
            self.output_area_insert(f"{self.hostname}\n")
        else:
            self.output_area_insert("EmulatorOS\n")
    
    def cmd_wc(self, args):
        """Команда wc - подсчет строк, слов, символов"""
        count_lines = True
        count_words = True
        count_chars = True
        count_bytes = False
        filenames = []
        
        # Парсинг аргументов
        for arg in args:
            if arg.startswith('-'):
                if 'l' in arg:
                    count_lines = True
                    count_words = False
                    count_chars = False
                    count_bytes = False
                if 'w' in arg:
                    count_lines = False
                    count_words = True
                    count_chars = False
                    count_bytes = False
                if 'm' in arg:
                    count_lines = False
                    count_words = False
                    count_chars = True
                    count_bytes = False
                if 'c' in arg:
                    count_lines = False
                    count_words = False
                    count_chars = False
                    count_bytes = True
            else:
                filenames.append(arg)
        
        # Если файлы не указаны, используем stdin (не реализовано)
        if not filenames:
            self.output_area_insert("Ошибка: wc требует указания файлов\n")
            return
        
        total_lines = 0
        total_words = 0
        total_chars = 0
        total_bytes = 0
        
        for filename in filenames:
            stats = self.vfs.get_file_stats(filename)
            if stats:
                # Вывод статистики для файла
                output_parts = []
                if count_lines:
                    output_parts.append(str(stats['lines']))
                if count_words:
                    output_parts.append(str(stats['words']))
                if count_chars:
                    output_parts.append(str(stats['chars']))
                if count_bytes:
                    output_parts.append(str(stats['bytes']))
                
                output_parts.append(filename)
                self.output_area_insert(" ".join(output_parts) + "\n")
                
                # Суммируем для общего итога
                total_lines += stats['lines']
                total_words += stats['words']
                total_chars += stats['chars']
                total_bytes += stats['bytes']
            else:
                error_msg = f"Ошибка: файл '{filename}' не найден"
                self.output_area_insert(f"{error_msg}\n")
                self.log_event("wc", f"Файл не найден: {filename}", error=error_msg)
        
        # Вывод общего итога если несколько файлов
        if len(filenames) > 1:
            output_parts = []
            if count_lines:
                output_parts.append(str(total_lines))
            if count_words:
                output_parts.append(str(total_words))
            if count_chars:
                output_parts.append(str(total_chars))
            if count_bytes:
                output_parts.append(str(total_bytes))
            
            output_parts.append("total")
            self.output_area_insert(" ".join(output_parts) + "\n")
    
    def cmd_rmdir(self, args):
        """Команда rmdir - удаление пустых директорий"""
        if not args:
            error_msg = "Ошибка: не указана директория для удаления"
            self.output_area_insert(f"{error_msg}\n")
            self.log_event("rmdir", "Не указана директория", error=error_msg)
            return
        
        for dirname in args:
            success, message = self.vfs.remove_directory(dirname)
            if success:
                self.output_area_insert(f"{message}\n")
            else:
                self.output_area_insert(f"rmdir: {message}\n")
                self.log_event("rmdir", f"Ошибка удаления: {dirname}", error=message)
    
    def cmd_cp(self, args):
        """Команда cp - копирование файлов"""
        if len(args) < 2:
            error_msg = "Ошибка: недостаточно аргументов. Использование: cp исходный_файл целевой_файл"
            self.output_area_insert(f"{error_msg}\n")
            self.log_event("cp", "Недостаточно аргументов", error=error_msg)
            return
        
        source_name = args[0]
        target_name = args[1]
        
        success, message = self.vfs.copy_file(source_name, target_name)
        if success:
            self.output_area_insert(f"{message}\n")
        else:
            self.output_area_insert(f"cp: {message}\n")
            self.log_event("cp", f"Ошибка копирования: {source_name} -> {target_name}", error=message)
            
    def cmd_echo(self, args):
        """Команда echo - вывод аргументов"""
        self.output_area_insert(" ".join(args) + "\n")
        
    def cmd_pwd(self, args):
        """Команда pwd - показать текущую директорию"""
        self.output_area_insert(f"{self.vfs.get_current_path()}\n")
            
    def cmd_help(self):
        """Команда help - показывает список доступных команд"""
        self.output_area_insert("Доступные команды:\n")
        self.output_area_insert("  ls [-al] [путь]    - список файлов\n")
        self.output_area_insert("  cd [путь]          - смена директории\n")
        self.output_area_insert("  cat [файл...]      - вывод содержимого файлов\n")
        self.output_area_insert("  echo [текст]       - вывод текста\n")
        self.output_area_insert("  pwd                - показать текущую директорию\n")
        self.output_area_insert("  uname [-a]         - информация о системе\n")
        self.output_area_insert("  wc [-lwm] [файл...]- подсчет строк, слов, символов\n")
        self.output_area.insert("  rmdir [директория] - удаление пустых директорий\n")
        self.output_area.insert("  cp исходный целевой - копирование файлов\n")
        self.output_area_insert("  exit               - выход из эмулятора\n")
        self.output_area_insert("  help               - эта справка\n")

def parse_arguments():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(description='Эмулятор командной оболочки')
    parser.add_argument('--vfs', help='Путь к физическому расположению VFS')
    parser.add_argument('--log', help='Путь к лог-файлу')
    parser.add_argument('--script', help='Путь к стартовому скрипту')
    
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    print("=== Отладочная информация ===")
    print(f"VFS путь: {args.vfs}")
    print(f"Лог-файл: {args.log}") 
    print(f"Стартовый скрипт: {args.script}")
    print("=============================")
    
    root = tk.Tk()
    root.geometry("800x600")
    
    emulator = ShellEmulator(root, args.vfs, args.log, args.script)
    root.mainloop()

if __name__ == "__main__":
    main()