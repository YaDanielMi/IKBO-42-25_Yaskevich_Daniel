#!/bin/sh
# Этап 2: ошибочные значения параметров и неизвестные параметры.
cd "$(dirname "$0")/.." || exit 1
EMU="./run.sh --headless"

echo "=== 1. Несуществующий каталог VFS ==="
$EMU --vfs /no/such/dir --script examples/startup/basic.emu
echo "[код возврата: $?]"

echo; echo "=== 2. VFS указывает на файл, а не на каталог ==="
$EMU --vfs examples/vfs/minimal/hello.txt
echo "[код возврата: $?]"

echo; echo "=== 3. Несуществующий стартовый скрипт ==="
$EMU --vfs examples/vfs/minimal --script /no/such/script.emu
echo "[код возврата: $?]"

echo; echo "=== 4. Скрипт — это каталог ==="
$EMU --script examples/startup
echo "[код возврата: $?]"

echo; echo "=== 5. Параметр без значения ==="
$EMU --vfs
echo "[код возврата: $?]"

echo; echo "=== 6. Неизвестный параметр ==="
$EMU --unknown
echo "[код возврата: $?]"
