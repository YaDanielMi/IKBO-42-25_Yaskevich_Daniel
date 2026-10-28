#!/bin/sh
# Этап 3: VFS живёт в памяти. Каталог на диске удаляется во время
# сеанса, а эмулятор продолжает работать. Исходные примеры не меняются.
cd "$(dirname "$0")/.." || exit 1
EMU="./run.sh --headless"

checksum() {
    find examples/vfs -type f -exec cksum {} + | sort
}

echo "=== 1. Копия VFS удаляется с диска посреди сеанса ==="
TMP=$(mktemp -d)
cp -r examples/vfs/deep/. "$TMP"
{
    echo "ls docs"
    sleep 1
    rm -rf "$TMP"
    echo "[каталог $TMP удалён с диска]" >&2
    echo "ls docs"
    echo "cd src/lib"
    echo "ls"
    echo "exit"
} | $EMU --vfs "$TMP"
echo "[код возврата: $?]"

echo; echo "=== 2. Данные примеров после сеанса не изменились ==="
BEFORE=$(checksum)
$EMU --vfs examples/vfs/deep --script examples/startup/all_commands.emu \
    > /dev/null 2>&1
AFTER=$(checksum)
if [ "$BEFORE" = "$AFTER" ]; then
    echo "OK: файлы VFS на диске не изменены"
else
    echo "ОШИБКА: файлы VFS изменились"
fi
