#!/bin/bash
file="$1"

if [ -z "$file" ]; then
    echo "Нужно указать файл"
    exit 1
fi

chmod 755 "$file"
sudo cp "$file" /usr/local/bin/

echo "Команда $file установлена"
