#!/bin/sh

echo ""
echo "==================================="
echo " Avvio transport-api"
echo "==================================="
echo ""

exec gunicorn \
    -w 3 \
    -b 0.0.0.0:5000 \
    app:app