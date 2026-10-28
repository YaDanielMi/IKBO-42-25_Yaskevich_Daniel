#!/bin/sh
# Этап 2: возможности стартового скрипта (комментарии, ошибки, exit).
cd "$(dirname "$0")/.." || exit 1
EMU="./run.sh --headless"

echo "=== 1. Скрипт с exit 7: код возврата эмулятора ==="
$EMU --vfs examples/vfs/minimal --script examples/startup/basic.emu
echo "[код возврата: $?]"

echo; echo "=== 2. Скрипт без exit, затем команды со stdin ==="
printf 'ls\nexit 3\n' | $EMU --vfs examples/vfs/minimal \
    --script examples/startup/no_exit.emu
echo "[код возврата: $?]"

echo; echo "=== 3. Скрипт без exit и пустой stdin (конец ввода) ==="
$EMU --script examples/startup/no_exit.emu < /dev/null
echo "[код возврата: $?]"

echo; echo "=== 4. exit с нечисловым аргументом ==="
$EMU --script examples/startup/bad_exit.emu
echo "[код возврата: $?]"
