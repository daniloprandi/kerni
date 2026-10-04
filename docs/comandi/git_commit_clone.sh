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
echo "==> Verifica remote kerni_clone"

if ! git remote get-url kerni_clone >/dev/null 2>&1; then
  echo "Errore: il remote 'kerni_clone' non esiste."
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
echo "==> Recupero stato di kerni_clone"
git fetch kerni_clone main

echo
echo "==> Preparazione snapshot"

TMP_INDEX="$(mktemp)"
trap 'rm -f "$TMP_INDEX"' EXIT

export GIT_INDEX_FILE="$TMP_INDEX"

git read-tree HEAD

echo
echo "==> Creazione tree"
TREE=$(git write-tree)

unset GIT_INDEX_FILE

echo
echo "==> Preparazione commit"

REMOTE_HEAD=$(git rev-parse kerni_clone/main)

if git merge-base --is-ancestor "$REMOTE_HEAD" origin/main; then
  echo "Rilevata vecchia storia condivisa con Kerni."
  echo "Creo il primo commit indipendente."

  COMMIT=$(git commit-tree "$TREE" <<EOF
Snapshot indipendente di Kerni

Copia dello stato corrente di /var/www/kerni nel repository privato kerni_clone.
EOF
)

else
  echo "Storia privata già indipendente."
  echo "Creo un nuovo commit sulla storia di kerni_clone."

  COMMIT=$(git commit-tree "$TREE" -p "$REMOTE_HEAD" <<EOF
Snapshot di Kerni

Copia dello stato corrente di /var/www/kerni nel repository privato kerni_clone.
EOF
)

fi

echo
echo "==> Push del commit privato"

git push kerni_clone "$COMMIT:refs/heads/main" --force

echo
echo "========================================="
echo " Copia completata con successo."
echo " Repository: kerni_clone"
echo " Visibilità: PRIVATE"
echo " Commit privato: $COMMIT"
echo "========================================="