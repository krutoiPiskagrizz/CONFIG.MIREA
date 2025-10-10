# Тестовый скрипт для Этапа 5 - Дополнительные команды
echo "=== Тестирование команд Этапа 5 ==="

echo "1. Создание тестовых директорий и файлов:"
cd /home/user
ls
mkdir test_dir1
mkdir test_dir2
echo "Содержимое файла для копирования" > source_file.txt
ls

echo "2. Тестирование cp:"
cp source_file.txt copy1.txt
cp source_file.txt copy2.txt
ls
cat copy1.txt
cat copy2.txt

echo "3. Тестирование rmdir:"
rmdir empty_dir
ls
rmdir dir_with_files  # Должна быть ошибка - директория не пуста
rmdir test_dir1
ls

echo "4. Тестирование обработки ошибок:"
rmdir nonexistent_dir
cp nonexistent.txt target.txt
cp source_file.txt /invalid/path/target.txt

echo "5. Комбинированное использование:"
cd temp
ls
cp source.txt ../backup_source.txt
cd ..
ls
cat backup_source.txt

echo "=== Тестирование завершено ==="