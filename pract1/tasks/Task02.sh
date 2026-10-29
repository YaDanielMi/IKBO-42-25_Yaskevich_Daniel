#!/bin/bash
grep -v "^#" /etc/protocols | grep -v "^$" | awk '{print $2, $1}' | sort -n | tail -n 5
