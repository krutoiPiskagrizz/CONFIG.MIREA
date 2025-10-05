# Скрипт для тестирования всех параметров конфигурации
echo "Тестирование различных конфигураций эмулятора..."

echo "1. Запуск с логгированием:"
python shell_emulator.py --log logs/emulator_log.xml

echo "2. Запуск со стартовым скриптом:"
python shell_emulator.py --script test_script1.sh --log logs/script_log.xml

echo "3. Запуск с VFS и скриптом:"
python shell_emulator.py --vfs ./vfs_root --script test_script2.sh --log logs/full_log.xml

echo "4. Запуск со всеми параметрами:"
python shell_emulator.py --vfs ./vfs_root --script test_script1.sh --log logs/complete_log.xml

echo "Тестирование завершено!"