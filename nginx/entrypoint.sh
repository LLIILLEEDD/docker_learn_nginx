#!/bin/sh

echo "Generating nginx configs"

python3 /app/generator.py

echo "Checking nginx config"

nginx -t

if [ $? -ne 0 ]; then
    echo "Nginx config error"
    exit 1
fi

echo "Starting nginx"

exec nginx -g "daemon off;"