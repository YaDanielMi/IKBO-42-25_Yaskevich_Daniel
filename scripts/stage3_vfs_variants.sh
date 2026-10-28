#!/bin/sh
# Этап 3: работа с разными вариантами VFS (команды подаются через stdin).
cd "$(dirname "$0")/.." || exit 1
EMU="./run.sh --headless"

echo "=== 1. Минимальный VFS: один файл ==="
$EMU --vfs examples/vfs/minimal <<'CMDS'
ls
ls -l
cd hello.txt
cd /
ls hello.txt
exit
CMDS
echo "[код возврата: $?]"

echo; echo "=== 2. Пустой каталог как VFS (создаётся на лету) ==="
EMPTY=$(mktemp -d)
$EMU --vfs "$EMPTY" <<'CMDS'
ls
ls -a
cd any
exit
CMDS
echo "[код возврата: $?]"
rmdir "$EMPTY"

echo; echo "=== 3. Несколько файлов в одном каталоге ==="
$EMU --vfs examples/vfs/several <<'CMDS'
ls
ls -a
ls -l
ls "заметки.txt" data.csv
cd notes.txt
exit
CMDS
echo "[код возврата: $?]"

echo; echo "=== 4. Вложенность 4 уровня ==="
$EMU --vfs examples/vfs/deep <<'CMDS'
cd docs/guides/advanced
ls
cd ../../..
cd src/lib
ls
cd /
ls docs/guides/advanced
ls "dir with space"
exit
CMDS
echo "[код возврата: $?]"
