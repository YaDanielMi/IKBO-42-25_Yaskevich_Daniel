#!/bin/bash
ext="$1"

if [ -z "$ext" ]; then
    echo "Нужно указать расширение"
    exit 1
fi

tar -cf "archive_$ext.tar" *."$ext"

echo "Готово: archive_$ext.tar"
