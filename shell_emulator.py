import tkinter as tk
from tkinter import scrolledtext, Entry, Frame
import os
import sys

class ShellEmulator:
    def __init__(self, root):
        self.root = root
        self.username = os.getenv('USERNAME') or os.getenv('USER')
        self.hostname = os.uname().nodename if hasattr(os, 'uname') else os.getenv('COMPUTERNAME', 'localhost')
        
        # Установка заголовка окна
        self.root.title(f"Эмулятор - [{self.username}@{self.hostname}]")
        
        # Создание интерфейса
        self.create_widgets()
        
        # Текущая директория (заглушка)
        self.current_dir = "/home/user"
        
        # Приветственное сообщение
        self.output_area.insert(tk.END, f"Добро пожаловать в эмулятор командной оболочки!\n")
        self.output_area.insert(tk.END, f"Текущий пользователь: {self.username}@{self.hostname}\n")
        self.output_area.insert(tk.END, "Введите 'exit' для выхода или 'help' для списка команд\n\n")
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
        
    def show_prompt(self):
        self.output_area.config(state=tk.NORMAL)
        self.output_area.insert(tk.END, f"{self.username}@{self.hostname}:{self.current_dir}$ ")
        self.output_area.config(state=tk.DISABLED)
        self.output_area.see(tk.END)
        
    def execute_command(self, event):
        command_text = self.command_entry.get().strip()
        self.command_entry.delete(0, tk.END)
        
        if not command_text:
            self.show_prompt()
            return
            
        # Парсинг команды и аргументов
        parts = command_text.split()
        command = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        # Вывод введенной команды
        self.output_area.config(state=tk.NORMAL)
        self.output_area.insert(tk.END, f"{command_text}\n")
        
        # Обработка команд
        if command == "exit":
            self.root.quit()
        elif command == "ls":
            self.cmd_ls(args)
        elif command == "cd":
            self.cmd_cd(args)
        elif command == "help":
            self.cmd_help()
        else:
            self.output_area.insert(tk.END, f"Ошибка: неизвестная команда '{command}'\n")
        
        self.show_prompt()
        
    def cmd_ls(self, args):
        """Команда ls - заглушка"""
        self.output_area.insert(tk.END, f"Команда: ls\n")
        if args:
            self.output_area.insert(tk.END, f"Аргументы: {args}\n")
        else:
            self.output_area.insert(tk.END, "Аргументы отсутствуют\n")
        self.output_area.insert(tk.END, "file1.txt  file2.txt  directory1/\n")
        
    def cmd_cd(self, args):
        """Команда cd - заглушка"""
        self.output_area.insert(tk.END, f"Команда: cd\n")
        if len(args) == 0:
            # cd без аргументов - переход в домашнюю директорию
            self.current_dir = "/home/user"
            self.output_area.insert(tk.END, "Переход в домашнюю директорию\n")
        elif len(args) == 1:
            if args[0] == "..":
                # Упрощенная обработка перехода на уровень выше
                if self.current_dir != "/":
                    parts = self.current_dir.split('/')
                    self.current_dir = '/'.join(parts[:-1]) or '/'
            else:
                # "Переход" в указанную директорию
                self.current_dir = f"{self.current_dir}/{args[0]}"
            self.output_area.insert(tk.END, f"Переход в директорию: {self.current_dir}\n")
        else:
            self.output_area.insert(tk.END, "Ошибка: неверное количество аргументов для cd\n")
            self.output_area.insert(tk.END, "Использование: cd [директория]\n")
            
    def cmd_help(self):
        """Команда help - показывает список доступных команд"""
        self.output_area.insert(tk.END, "Доступные команды:\n")
        self.output_area.insert(tk.END, "  ls [аргументы] - список файлов (заглушка)\n")
        self.output_area.insert(tk.END, "  cd [директория] - смена директории (заглушка)\n")
        self.output_area.insert(tk.END, "  exit - выход из эмулятора\n")
        self.output_area.insert(tk.END, "  help - эта справка\n")

def main():
    root = tk.Tk()
    root.geometry("800x600")
    
    # Создание эмулятора
    emulator = ShellEmulator(root)
    
    # Запуск главного цикла
    root.mainloop()

if __name__ == "__main__":
    main()