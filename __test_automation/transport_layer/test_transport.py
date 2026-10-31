# Importazione delle librerie per i test del transport layer di Kerni
import pytest
from unittest.mock import patch

# Fixture di pytest per simulare le connessioni di trasporto attive (es. TCP/UDP)
@pytest.fixture
def mock_transport_connections():
  return [
    {
      "local_ip": "127.0.0.1",
      "local_port": 80,
      "remote_ip": "0.0.0.0",
      "remote_port": 0,
      "state": "LISTEN",
      "protocol": "tcp"
    },
    {
      "local_ip": "192.168.1.10",
      "local_port": 54321,
      "remote_ip": "93.184.216.34",
      "remote_port": 443,
      "state": "ESTABLISHED",
      "protocol": "tcp"
    }
  ]

# Test unitario per verificare la struttura dei dati del transport layer
def test_transport_connections_structure(mock_transport_connections):
  # Assegnazione di un identificativo di nodo fittizio per il test
  node_id = "kerni-node-01"
  
  # Aggiunta del campo node_id per la conformità allo schema relazionale
  records = [{**conn, "node_id": node_id} for conn in mock_transport_connections]
  
  # Verifiche e asserzioni sulla correttezza dei dati di trasporto
  assert isinstance(records, list)
  assert len(records) == 2
  assert records[0]["protocol"] == "tcp"
  assert records[0]["state"] == "LISTEN"
  assert records[1]["state"] == "ESTABLISHED"
  assert records[1]["node_id"] == node_id