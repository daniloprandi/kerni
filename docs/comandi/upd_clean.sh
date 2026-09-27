#!/bin/bash

set -e

echo "=== Aggiornamento repository ==="
sudo apt update

echo "=== Aggiornamento sistema ==="
sudo apt full-upgrade -y

echo "=== Rimozione dipendenze non più necessarie ==="
sudo apt autoremove --purge -y

echo "=== Pulizia pacchetti scaricati ==="
sudo apt autoclean

echo "=== Pulizia cache APT ==="
sudo apt clean

echo "=== Operazione completata ==="