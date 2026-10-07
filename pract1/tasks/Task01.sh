#!/bin/bash
cat /etc/passwd | grep -E "^[a-zA-Z]" | cut -d: -f1 | sort
