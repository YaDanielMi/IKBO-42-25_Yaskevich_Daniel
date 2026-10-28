#!/bin/sh
# Этап 2: все параметры командной строки с корректными значениями.
cd "$(dirname "$0")/.." || exit 1
EMU="./run.sh --headless"

echo "=== 1. Без параметров (команды со stdin) ==="
printf 'ls\ncd /tmp\nexit\n' | $EMU
echo "[код возврата: $?]"

echo; echo "=== 2. Только --vfs ==="
printf 'ls\nexit\n' | $EMU --vfs examples/vfs/minimal
echo "[код возврата: $?]"

echo; echo "=== 3. Только --script ==="
$EMU --script examples/startup/basic.emu
echo "[код возврата: $?]"

echo; echo "=== 4. --vfs и --script вместе ==="
$EMU --vfs examples/vfs/minimal --script examples/startup/basic.emu
echo "[код возврата: $?]"
