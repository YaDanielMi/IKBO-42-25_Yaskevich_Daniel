#!/bin/sh
# Этап 3: ошибки при загрузке VFS и при работе с ней.
cd "$(dirname "$0")/.." || exit 1
EMU="./run.sh --headless"

echo "=== 1. Каталог VFS не существует ==="
$EMU --vfs /no/such/dir
echo "[код возврата: $?]"

echo; echo "=== 2. VFS — это файл ==="
$EMU --vfs examples/vfs/several/data.csv
echo "[код возврата: $?]"

echo; echo "=== 3. Ошибки команд в минимальном VFS ==="
$EMU --vfs examples/vfs/minimal <<'CMDS'
ls nothing
cd nothing
ls hello.txt/inside
cd hello.txt
cd a b
ls -q
exit
CMDS
echo "[код возврата: $?]"

echo; echo "=== 4. Ошибки команд в глубоком VFS ==="
$EMU --vfs examples/vfs/deep <<'CMDS'
cd docs/guides/missing/advanced
ls docs/manual.txt/x
cd src/main.c
cd -
exit
CMDS
echo "[код возврата: $?]"
