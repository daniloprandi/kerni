#!/bin/bash

set -e

cd /var/www/kerni

echo "==> Git status"
git status

echo
read -rp "Messaggio del commit: " COMMIT_MSG

if [ -z "$COMMIT_MSG" ]; then
  echo "Errore: il messaggio del commit è obbligatorio."
  exit 1
fi

echo
echo "==> git add ."
git add .

echo "==> git commit"
git commit -m "$COMMIT_MSG"

echo "==> git push"
git push origin main

echo
echo "========================================="
echo " Commit completato con successo."
echo " Repository sincronizzato con GitHub."
echo "========================================="
