# Тестовый скрипт для Этапа 4 - Основные команды
echo "=== Тестирование команд Этапа 4 ==="

echo "1. Тестирование ls с опциями:"
ls
ls -l
ls -a
ls -la

echo "2. Тестирование cd:"
pwd
cd documents
pwd
ls
cd ..
pwd
cd /home/user
pwd

echo "3. Тестирование uname:"
uname
uname -s
uname -n
uname -a

echo "4. Тестирование wc:"
wc readme.txt
wc -l readme.txt
wc -w readme.txt
wc -m readme.txt
wc readme.txt data.txt notes.txt

echo "5. Тестирование обработки ошибок:"
cd nonexistent_directory
ls /invalid/path
uname -invalid
wc unknown_file.txt

echo "=== Тестирование завершено ==="