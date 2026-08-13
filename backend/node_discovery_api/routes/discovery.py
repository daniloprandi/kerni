import socket
import struct

from common.database import get_connection
from common.linux.node_discovery import discovery


def register_ping(src_ip, dest_ip):
  # Apre una connessione al database.
  connection = get_connection()

  try:
    # Inserisce il ping oppure aggiorna last_seen
    # se la coppia src_ip / dest_ip esiste già.
    with connection.cursor() as cursor:
      cursor.execute(
        """
        INSERT INTO tcpip.ping (src_ip, dest_ip)
        VALUES (%s, %s)
        ON CONFLICT (src_ip, dest_ip)
        DO UPDATE SET last_seen = CURRENT_TIMESTAMP
        """,
        (src_ip, dest_ip)
      )

    # Conferma la modifica al database.
    connection.commit()

  finally:
    # Chiude la connessione al database.
    connection.close()


def listen_for_ping():
  # Crea un raw socket per ricevere pacchetti ICMP.
  raw_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_RAW,
    socket.IPPROTO_ICMP
  )

  # Rimane in ascolto dei pacchetti ICMP.
  while True:
    # Riceve il pacchetto e l'indirizzo del mittente.
    packet, address = raw_socket.recvfrom(65535)

    # Prende i primi 20 byte dell'header IPv4.
    ip_header = packet[:20]

    # Estrae l'indirizzo IP sorgente.
    source_ip = socket.inet_ntoa(
      struct.unpack("!4s", ip_header[12:16])[0]
    )

    # Estrae l'indirizzo IP destinazione.
    destination_ip = socket.inet_ntoa(
      struct.unpack("!4s", ip_header[16:20])[0]
    )

    # Mostra il ping osservato.
    print(
      f"PING: {source_ip} -> {destination_ip}",
      flush=True
    )

    # Registra il ping nel database.
    register_ping(source_ip, destination_ip)

    # Avvia la discovery del nodo che ha generato il ping.
    discovery.run(source_ip)