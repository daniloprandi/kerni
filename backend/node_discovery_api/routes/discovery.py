import socket
import struct


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

    # Prende i primi 20 byte del pacchetto, cioè l'header IPv4.
    ip_header = packet[:20]

    # Estrae l'indirizzo IP sorgente dall'header IP.
    source_ip = socket.inet_ntoa(
      struct.unpack("!4s", ip_header[12:16])[0]
    )

    # Estrae l'indirizzo IP destinazione dall'header IP.
    destination_ip = socket.inet_ntoa(
      struct.unpack("!4s", ip_header[16:20])[0]
    )

    # Mostra il percorso del pacchetto ICMP osservato.
    print(
      f"PING: {source_ip} -> {destination_ip}",
      flush=True
    )