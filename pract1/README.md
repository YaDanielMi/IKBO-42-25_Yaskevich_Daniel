# Практическая работа №1.

**Выполнил:** Яскевич Даниил Михайлович, группа ИКБО-42-25

## Задача 1

```
#!/bin/bash
cat /etc/passwd | grep -E "^[a-zA-Z]" | cut -d: -f1 | sort
```
(screens/1.png)

## Задача 2

```
#!/bin/bash
grep -v "^#" /etc/protocols | grep -v "^$" | awk '{print $2, $1}' | sort -n | tail -n 5
```
(screens/2.png)

## Задача 3

```
#!/bin/bash
text="$1"
length=${#text}

line=""
i=0
while [ $i -lt $((length + 2)) ]; do
    line="$line-"
    i=$((i + 1))
done

echo "+$line+"
echo "| $text |"
echo "+$line+"
```
(screens/3.png)

## Задача 4

```
#!/bin/bash
file="$1"
grep -oE "[a-zA-Z_][a-zA-Z0-9_]*" "$file" | sort -u | tr "\n" " "
echo ""
```
(screens/4.png)

## Задача 5

```
#!/bin/bash
file="$1"

if [ -z "$file" ]; then
    echo "Нужно указать файл"
    exit 1
fi

chmod 755 "$file"
sudo cp "$file" /usr/local/bin/

echo "Команда $file установлена"
```
(screens/5.png)

## Задача 6

```
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
```
(screens/6.png)

## Задача 7

```
#!/bin/bash
dir="$1"
if [ -z "$dir" ]; then
    dir="."
fi

find "$dir" -type f -exec md5sum {} \; | sort > /tmp/hashes_$$.txt

prev_hash=""
prev_file=""

while read -r hash file; do
    if [ "$hash" = "$prev_hash" ]; then
        echo "$prev_file"
        echo "$file"
    fi
    prev_hash="$hash"
    prev_file="$file"
done < /tmp/hashes_$$.txt

rm /tmp/hashes_$$.txt
```
(screens/7.png)

## Задача 8

```
#!/bin/bash
ext="$1"

if [ -z "$ext" ]; then
    echo "Нужно указать расширение"
    exit 1
fi

tar -cf "archive_$ext.tar" *."$ext"

echo "Готово: archive_$ext.tar"
```
(screens/8.png)

## Задача 9

```
#!/bin/bash
input="$1"
output="$2"

sed "s/    /\t/g" "$input" > "$output"
```
(screens/9.png)

## Задача 10

```
#!/bin/bash
dir="$1"
if [ -z "$dir" ]; then
    dir="."
fi

find "$dir" -maxdepth 1 -type f -empty
```
(screens/10.png)
