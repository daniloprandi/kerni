#!/bin/bash

set -e

cd /var/www/kerni

echo "==> Git status"
git status

echo
echo "==> Verifica working tree"

if [ -n "$(git status --porcelain)" ]; then
  echo "Errore: il working tree non è pulito."
  echo "Fai prima commit delle modifiche oppure ripristinale."
  exit 1
fi

echo
echo "==> Verifica GitHub CLI"

if ! command -v gh >/dev/null 2>&1; then
  echo "Errore: GitHub CLI (gh) non è installata."
  exit 1
fi

echo
echo "==> Verifica autenticazione GitHub"
gh auth status

echo
echo "==> Creazione repository privato: kerni_clone"

gh repo create kerni_clone \
  --private \
  --source=. \
  --remote=kerni_clone \
  --push

echo
echo "========================================="
echo " Copia completata con successo."
echo " Repository: kerni_clone"
echo " Visibilità: PRIVATE"
echo " Remote: kerni_clone"
echo "========================================="