# Importa il modulo SSH per eseguire comandi sul nodo remoto.
from common.linux.remote import ssh

# Importa i parser per le connessioni TCP/UDP e IPv6.
from .parser import parse_transport
from .parser import parse_transport6

# Importa il parser per i socket UNIX.
from .parser import parse_unix

# Importa il repository per salvare i risultati nel database.
from . import repository


def inspect_transport_layer(host, node_id):
  # Inizializza la lista delle connessioni individuate.
  connections = []

  # Legge e interpreta le connessioni TCP IPv4.
  tcp_data = ssh.execute(
    host,
    "cat /proc/net/tcp"
  )
  connections.extend(
    parse_transport(
      tcp_data.splitlines(),
      "TCP"
    )
  )

  # Legge e interpreta le connessioni TCP IPv6.
  tcp6_data = ssh.execute(
    host,
    "cat /proc/net/tcp6"
  )
  connections.extend(
    parse_transport6(
      tcp6_data.splitlines(),
      "TCP6"
    )
  )

  # Legge e interpreta le connessioni UDP IPv4.
  udp_data = ssh.execute(
    host,
    "cat /proc/net/udp"
  )
  connections.extend(
    parse_transport(
      udp_data.splitlines(),
      "UDP"
    )
  )

  # Legge e interpreta le connessioni UDP IPv6.
  udp6_data = ssh.execute(
    host,
    "cat /proc/net/udp6"
  )
  connections.extend(
    parse_transport6(
      udp6_data.splitlines(),
      "UDP6"
    )
  )

  # Legge e interpreta i socket RAW IPv4.
  raw_data = ssh.execute(
    host,
    "cat /proc/net/raw"
  )
  connections.extend(
    parse_transport(
      raw_data.splitlines(),
      "RAW"
    )
  )

  # Legge e interpreta i socket RAW IPv6.
  raw6_data = ssh.execute(
    host,
    "cat /proc/net/raw6"
  )
  connections.extend(
    parse_transport6(
      raw6_data.splitlines(),
      "RAW6"
    )
  )

  # Legge e interpreta i socket UNIX.
  unix_data = ssh.execute(
    host,
    "cat /proc/net/unix"
  )
  connections.extend(
    parse_unix(
      unix_data.splitlines(),
      "UNIX"
    )
  )

  # Prepara la lista delle connessioni da salvare.
  valid_connections = []

  # Associa ogni connessione al nodo di appartenenza.
  for connection in connections:
    connection["node_id"] = node_id
    valid_connections.append(connection)

  # Salva le connessioni nel database.
  repository.insert_all(valid_connections)

  # Restituisce le connessioni raccolte.
  return {
    "connections": valid_connections
  }


# Mantiene il punto di ingresso utilizzato dal modulo.
def run(host, node_id):
  return inspect_transport_layer(host, node_id)