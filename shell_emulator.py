import tkinter as tk
from tkinter import scrolledtext, Entry, Frame, messagebox
import os
import sys
import argparse
import logging
import xml.etree.ElementTree as ET
from datetime import datetime
import subprocess

class ShellEmulator:
    def __init__(self, root, vfs_path=None, log_file=None, startup_script=None):
        self.root = root
        self.username = os.getenv('USERNAME') or os.getenv('USER')
        self.hostname = os.uname().nodename if hasattr(os, 'uname') else os.getenv('COMPUTERNAME', 'localhost')
        
        # Параметры конфигурации
        self.vfs_path = vfs_path
        self.log_file = log_file
        self.startup_script = startup_script
        
        # Настройка логирования
        self.setup_logging()
        
        # Логирование параметров запуска
        self.log_event("startup", f"Эмулятор запущен с параметрами: VFS={vfs_path}, LOG={log_file}, SCRIPT={startup_script}")
        
        # Установка заголовка окна
        self.root.title(f"Эмулятор - [{self.username}@{self.hostname}]")
        
        # Создание интерфейса
        self.create_widgets()
        
        # Текущая директория (заглушка)
        self.current_dir = "/home/user"
        
        # Приветственное сообщение
        self.output_area_insert(f"Добро пожаловать в эмулятор командной оболочки!\n")
        self.output_area_insert(f"Текущий пользователь: {self.username}@{self.hostname}\n")
        
        # Вывод параметров конфигурации (отладочная информация)
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
            # Создаем корневой элемент для XML лога
            self.log_root = ET.Element("emulator_log")
            self.log_tree = ET.ElementTree(self.log_root)
            
            # Создаем папку для логов если нужно
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
            ET.SubElement(event, "current_dir").text = self.current_dir
            
            # Сохраняем лог в файл
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
                if line and not line.startswith('#'):  # Пропускаем пустые строки и комментарии
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
        self.prompt_label = tk.Label(
            input_frame, 
            text=f"{self.username}@{self.hostname}:~$ ",
            bg='black',
            fg='green',
            font=('Courier New', 10, 'bold')
        )
        self.prompt_label.pack(side=tk.LEFT)
        
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
        
    def output_area_insert(self, text):
        """Вставка текста в область вывода"""
        self.output_area.config(state=tk.NORMAL)
        self.output_area.insert(tk.END, text)
        self.output_area.config(state=tk.DISABLED)
        self.output_area.see(tk.END)
        
    def show_prompt(self):
        self.output_area_insert(f"{self.username}@{self.hostname}:{self.current_dir}$ ")
        
    def process_command(self, command_text):
        """Обработка команды (используется и для скриптов)"""
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
            
        # Вывод введенной команды
        self.output_area_insert(f"{command_text}\n")
        self.process_command(command_text)
        self.show_prompt()
        
    def cmd_ls(self, args):
        """Команда ls - заглушка"""
        self.output_area_insert(f"Команда: ls\n")
        if args:
            self.output_area_insert(f"Аргументы: {args}\n")
        self.output_area_insert("file1.txt  file2.txt  directory1/\n")
        
    def cmd_cd(self, args):
        """Команда cd - заглушка"""
        self.output_area_insert(f"Команда: cd\n")
        if len(args) == 0:
            self.current_dir = "/home/user"
            self.output_area_insert("Переход в домашнюю директорию\n")
        elif len(args) == 1:
            if args[0] == "..":
                if self.current_dir != "/":
                    parts = self.current_dir.split('/')
                    self.current_dir = '/'.join(parts[:-1]) or '/'
            else:
                self.current_dir = f"{self.current_dir}/{args[0]}"
            self.output_area_insert(f"Переход в директорию: {self.current_dir}\n")
        else:
            error_msg = "Ошибка: неверное количество аргументов для cd"
            self.output_area_insert(f"{error_msg}\n")
            self.output_area_insert("Использование: cd [директория]\n")
            self.log_event("cd", f"Неверные аргументы: {args}", error=error_msg)
            
    def cmd_echo(self, args):
        """Команда echo - вывод аргументов"""
        self.output_area_insert(" ".join(args) + "\n")
        
    def cmd_pwd(self, args):
        """Команда pwd - показать текущую директорию"""
        self.output_area_insert(f"{self.current_dir}\n")
            
    def cmd_help(self):
        """Команда help - показывает список доступных команд"""
        self.output_area_insert("Доступные команды:\n")
        self.output_area_insert("  ls [аргументы] - список файлов (заглушка)\n")
        self.output_area_insert("  cd [директория] - смена директории (заглушка)\n")
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
    # Парсинг аргументов командной строки
    args = parse_arguments()
    
    # Вывод отладочной информации в консоль
    print("=== Отладочная информация ===")
    print(f"VFS путь: {args.vfs}")
    print(f"Лог-файл: {args.log}") 
    print(f"Стартовый скрипт: {args.script}")
    print("=============================")
    
    root = tk.Tk()
    root.geometry("800x600")
    
    # Создание эмулятора с переданными параметрами
    emulator = ShellEmulator(root, args.vfs, args.log, args.script)
    
    # Запуск главного цикла
    root.mainloop()

if __name__ == "__main__":
    main()