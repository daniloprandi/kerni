# Importazione delle librerie di test e dei moduli reali di Kerni
import pytest
from unittest.mock import patch
from common.linux.application_layer.systemd import parser, inspector

# Fixture di pytest per simulare le linee grezze restituite da systemctl
@pytest.fixture
def mock_systemd_lines():
  return [
    "nginx.service loaded active running A high performance web server",
    "ssh.service loaded active running OpenBSD Secure Shell server"
  ]

# Test unitario per verificare la corretta normalizzazione del parser
def test_systemd_parser(mock_systemd_lines):
  # Esecuzione della funzione parser sui dati simulati
  records = parser.parse_systemd_services(mock_systemd_lines)
  
  # Verifiche sulla struttura dei record restituiti
  assert isinstance(records, list)
  assert len(records) == 2
  assert records[0]["unit"] == "nginx.service"
  assert records[0]["active_state"] == "active"
  assert records[1]["unit"] == "ssh.service"

# Test unitario per verificare l'inspector simulando il reader di sistema
def test_systemd_inspector():
  # Definizione delle linee grezze simulate per il reader
  mock_raw_lines = [
    "nginx.service loaded active running A high performance web server"
  ]
  
  # Utilizzo di patch per intercettare il reader di systemd sottostante
  with patch("common.linux.application_layer.systemd.files.systemd_reader.read_systemd_services", return_value=mock_raw_lines) as mock_read:
    # Esecuzione dell'inspector reale
    results = inspector.inspect_systemd()
    
    # Asserzioni sul corretto funzionamento e sul risultato normalizzato
    assert mock_read.called
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]["unit"] == "nginx.service"
    assert results[0]["active_state"] == "active"