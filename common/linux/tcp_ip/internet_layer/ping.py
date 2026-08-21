import subprocess
import re
from common.database import get_connection
from common.linux.node_discovery import discovery


def register_ping(src_ip, dest_ip):
  # Apre una connessione al database.
  con = get_connection()

  try:
    with con.cursor() as cursor:
      cursor.execute(
        """
        INSERT INTO tcpip.ping (src_ip, dest_ip)
        VALUES (%s, %s)
        """,
        (src_ip, dest_ip)
      )

    # Conferma la modifica al database.
    con.commit()

  finally:
    # Chiude la connessione al database.
    con.close()


def listen_for_ping():
  # Avvia tcpdump per osservare solamente gli ICMP Echo Request.
  command = [
    "tcpdump",
    "-i", "any",
    "-n",
    "-l",
    "icmp[icmptype] == icmp-echo",
  ]

  process = subprocess.Popen(
    command,
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    text=True
  )

  # Legge continuamente l'output di tcpdump.
  for line in process.stdout:
    match = re.search(
      r"IP (\d+\.\d+\.\d+\.\d+) > (\d+\.\d+\.\d+\.\d+): ICMP",
      line
    )

    if match:
      source_ip = match.group(1)
      destination_ip = match.group(2)

      # Mostra il ping osservato.
      print(
        f"PING: {source_ip} -> {destination_ip}",
        flush=True
      )

      # Registra ogni singolo ping nel database.
      register_ping(source_ip, destination_ip)

      # Avvia la discovery solamente se il ping
      # proviene da un nodo remoto.
      if source_ip != "192.168.200.130":
        discovery.run(source_ip)