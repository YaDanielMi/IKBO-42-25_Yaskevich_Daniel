#!/bin/sh
# Этап 3: стартовый скрипт эмулятора, проверяющий все команды и режимы
# этапов 1-3, включая работу с VFS и обработку ошибок.
cd "$(dirname "$0")/.." || exit 1

echo "=== Консольный режим ==="
./run.sh --headless --vfs examples/vfs/deep \
    --script examples/startup/all_commands.emu
echo "[код возврата: $?]"

echo
echo "Для запуска в окне уберите --headless:"
echo "  ./run.sh --vfs examples/vfs/deep" \
     "--script examples/startup/all_commands.emu"
