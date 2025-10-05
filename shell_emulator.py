import tkinter as tk
from tkinter import scrolledtext, Entry, Frame, messagebox
import os
import sys
import argparse
import logging
import xml.etree.ElementTree as ET
from datetime import datetime
import subprocess

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
        self.mkdir("documents", user)
        self.mkdir("downloads", user)
        self.create_file("readme.txt", user, "Добро пожаловать в эмулятор!")
        self.create_file("test.py", user, "print('Hello World')")
        
        # Создаем системуные директории
        self.mkdir("etc", self.root)
        self.mkdir("var", self.root)
        self.mkdir("tmp", self.root)
    
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
    
    def change_directory(self, path):
        """Смена текущей директории в VFS"""
        if path == "/":
            self.current_dir = self.root
            return True
        
        if path == "..":
            if self.current_dir.parent:
                self.current_dir = self.current_dir.parent
            return True
        
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
            elif part in target_dir.children and target_dir.children[part].is_directory:
                target_dir = target_dir.children[part]
            else:
                return False
        
        self.current_dir = target_dir
        return True
    
    def get_current_path(self):
        """Получение текущего пути в VFS"""
        path_parts = []
        current = self.current_dir
        
        while current and current.parent:  # Поднимаемся до корня
            path_parts.append(current.name)
            current = current.parent
        
        return "/" + "/".join(reversed(path_parts)) if path_parts else "/"
    
    def list_directory(self, path=None):
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
            if node.is_directory:
                items.append(f"{name}/")
            else:
                items.append(name)
        
        return sorted(items)
    
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
        """Команда ls - список файлов VFS"""
        path = args[0] if args else None
        items = self.vfs.list_directory(path)
        
        if items is None:
            error_msg = f"Ошибка: директория '{path}' не найдена"
            self.output_area_insert(f"{error_msg}\n")
            self.log_event("ls", f"Директория не найдена: {path}", error=error_msg)
            return
            
        if not items:
            self.output_area_insert("Директория пуста\n")
            return
            
        # Вывод в столбик (упрощенный)
        for item in items:
            self.output_area_insert(f"{item}  ")
        self.output_area_insert("\n")
        
    def cmd_cd(self, args):
        """Команда cd - смена директории VFS"""
        if len(args) == 0:
            path = "/home/user"
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
            
        filename = args[0]
        current_dir = self.vfs.current_dir
        
        if filename in current_dir.children and not current_dir.children[filename].is_directory:
            file_content = current_dir.children[filename].content
            self.output_area_insert(f"{file_content}\n")
        else:
            error_msg = f"Ошибка: файл '{filename}' не найден"
            self.output_area_insert(f"{error_msg}\n")
            self.log_event("cat", f"Файл не найден: {filename}", error=error_msg)
            
    def cmd_echo(self, args):
        """Команда echo - вывод аргументов"""
        self.output_area_insert(" ".join(args) + "\n")
        
    def cmd_pwd(self, args):
        """Команда pwd - показать текущую директорию"""
        self.output_area_insert(f"{self.vfs.get_current_path()}\n")
            
    def cmd_help(self):
        """Команда help - показывает список доступных команд"""
        self.output_area_insert("Доступные команды:\n")
        self.output_area_insert("  ls [путь] - список файлов и директорий\n")
        self.output_area_insert("  cd [путь] - смена директории\n")
        self.output_area_insert("  cat [файл] - вывод содержимого файла\n")
        self.output_area_insert("  echo [текст] - вывод текста\n")
        self.output_area_insert("  pwd - показать текущую директорию\n")
        self.output_area_insert("  exit - выход из эмулятора\n")
        self.output_area_insert("  help - эта справка\n")

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