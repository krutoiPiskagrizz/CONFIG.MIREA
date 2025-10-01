# console_demo.py - демонстрационная версия для консоли
import os

class ConsoleShellEmulator:
    def __init__(self):
        self.username = os.getenv('USERNAME') or os.getenv('USER')
        self.hostname = os.uname().nodename if hasattr(os, 'uname') else os.getenv('COMPUTERNAME', 'localhost')
        self.current_dir = "/home/user"
        
    def run(self):
        print(f"Добро пожаловать в эмулятор командной оболочки!")
        print(f"Текущий пользователь: {self.username}@{self.hostname}")
        print("Введите 'exit' для выхода или 'help' для списка команд\n")
        
        while True:
            try:
                command_text = input(f"{self.username}@{self.hostname}:{self.current_dir}$ ").strip()
                
                if not command_text:
                    continue
                    
                parts = command_text.split()
                command = parts[0]
                args = parts[1:] if len(parts) > 1 else []
                
                if command == "exit":
                    break
                elif command == "ls":
                    self.cmd_ls(args)
                elif command == "cd":
                    self.cmd_cd(args)
                elif command == "help":
                    self.cmd_help()
                else:
                    print(f"Ошибка: неизвестная команда '{command}'")
                    
            except KeyboardInterrupt:
                print("\nВыход...")
                break
            except EOFError:
                break
                
    def cmd_ls(self, args):
        print(f"Команда: ls")
        if args:
            print(f"Аргументы: {args}")
        else:
            print("Аргументы отсутствуют")
        print("file1.txt  file2.txt  directory1/")
        
    def cmd_cd(self, args):
        print(f"Команда: cd")
        if len(args) == 0:
            self.current_dir = "/home/user"
            print("Переход в домашнюю директорию")
        elif len(args) == 1:
            if args[0] == "..":
                if self.current_dir != "/":
                    parts = self.current_dir.split('/')
                    self.current_dir = '/'.join(parts[:-1]) or '/'
            else:
                self.current_dir = f"{self.current_dir}/{args[0]}"
            print(f"Переход в директорию: {self.current_dir}")
        else:
            print("Ошибка: неверное количество аргументов для cd")
            print("Использование: cd [директория]")
            
    def cmd_help(self):
        print("Доступные команды:")
        print("  ls [аргументы] - список файлов (заглушка)")
        print("  cd [директория] - смена директории (заглушка)")
        print("  exit - выход из эмулятора")
        print("  help - эта справка")

if __name__ == "__main__":
    emulator = ConsoleShellEmulator()
    emulator.run()