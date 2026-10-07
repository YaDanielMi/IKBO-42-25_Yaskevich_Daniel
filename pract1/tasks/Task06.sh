#!/bin/bash
dir="$1"
if [ -z "$dir" ]; then
    dir="."
fi

for file in "$dir"/*.c "$dir"/*.js "$dir"/*.py; do
    if [ -f "$file" ]; then
        first_line=$(head -n 1 "$file")

        case "$file" in
            *.py)
                if echo "$first_line" | grep -q "^#"; then
                    echo "$file: комментарий есть"
                else
                    echo "$file: комментария нет"
                fi
                ;;
            *.c|*.js)
                if echo "$first_line" | grep -qE "^(//|/\*)"; then
                    echo "$file: комментарий есть"
                else
                    echo "$file: комментария нет"
                fi
                ;;
        esac
    fi
done
