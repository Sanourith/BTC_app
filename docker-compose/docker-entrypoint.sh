#!/bin/bash

set -e

if [ -d "/docker-entrypoint-initdb.d" ]; then
    echo "Exécution des scripts init SQL..."
    for f in /docker-entrypoint-initdb.d/*.sql; do
        echo "Exécution de $f"
        mysql < "$f"
    done
fi

exec "$@"