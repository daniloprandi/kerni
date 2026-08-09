#!/bin/bash

# Interrompe lo script al primo errore.
set -e

# Directory principale del progetto Kerni.
PROJECT_DIR="/var/www/kerni"

# Entra nella directory del progetto.
cd "$PROJECT_DIR"

# Verifica che il virtual environment esista.
if [ ! -d ".venv" ]; then
  echo "Errore: virtual environment non trovato."
  echo
  echo "Crealo con il comando:"
  echo "python3 -m venv .venv"
  exit 1
fi

# Attiva il virtual environment.
source .venv/bin/activate

echo
echo "========================================="
echo " Virtual environment attivato."
echo "========================================="
echo "Python : $(which python)"
echo "Pip    : $(which pip)"
echo