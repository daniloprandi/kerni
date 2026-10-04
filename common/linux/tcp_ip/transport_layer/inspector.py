from common.linux.remote import ssh

from .parser import parse_transport
from .parser import parse_transport6
from .parser import parse_unix

from . import repository


def inspect_transport_layer(host, node_id):

  # Costruisce l'host SSH remoto.
  ssh_host = f"dprandi@{host}"

  # Legge tutti i socket e associa inode, PID e file descriptor
  # con una sola connessione SSH.
  socket_output = ssh.execute(
    ssh_host,
    r"""
    for pid in /proc/[0-9]*; do
      for fd in "$pid"/fd/*; do
        target=$(readlink "$fd" 2>/dev/null)

        case "$target" in
          socket:\[*\])
            inode=$(echo "$target" | tr -cd '0-9')
            echo "${pid##*/} ${fd##*/} $inode"
            ;;
        esac
      done
    done
    """
  )

  # Costruisce una mappa inode -> processo/file descriptor.
  socket_map = {}

  for line in socket_output.splitlines():

    fields = line.split()

    if len(fields) != 3:
      continue

    pid, fd, inode = fields

    socket_map[int(inode)] = {
      "pid": int(pid),
      "fd": int(fd)
    }

  # Lista delle connessioni.
  connections = []

  # Legge TCP.
  tcp_data = ssh.execute(
    ssh_host,
    "cat /proc/net/tcp"
  )

  connections.extend(
    parse_transport(
      tcp_data.splitlines(),
      "TCP"
    )
  )

  # Legge TCP IPv6.
  tcp6_data = ssh.execute(
    ssh_host,
    "cat /proc/net/tcp6"
  )

  connections.extend(
    parse_transport6(
      tcp6_data.splitlines(),
      "TCP6"
    )
  )

  # Legge UDP.
  udp_data = ssh.execute(
    ssh_host,
    "cat /proc/net/udp"
  )

  connections.extend(
    parse_transport(
      udp_data.splitlines(),
      "UDP"
    )
  )

  # Legge UDP IPv6.
  udp6_data = ssh.execute(
    ssh_host,
    "cat /proc/net/udp6"
  )

  connections.extend(
    parse_transport6(
      udp6_data.splitlines(),
      "UDP6"
    )
  )

  # Legge RAW.
  raw_data = ssh.execute(
    ssh_host,
    "cat /proc/net/raw"
  )

  connections.extend(
    parse_transport(
      raw_data.splitlines(),
      "RAW"
    )
  )

  # Legge RAW IPv6.
  raw6_data = ssh.execute(
    ssh_host,
    "cat /proc/net/raw6"
  )

  connections.extend(
    parse_transport6(
      raw6_data.splitlines(),
      "RAW6"
    )
  )

  # Legge UNIX.
  unix_data = ssh.execute(
    ssh_host,
    "cat /proc/net/unix"
  )

  connections.extend(
    parse_unix(
      unix_data.splitlines(),
      "UNIX"
    )
  )

  # Associa ogni connessione al nodo
  # e solamente alle socket effettivamente
  # presenti nella socket discovery.
  valid_connections = []

  for connection in connections:

    connection["node_id"] = node_id

    inode = connection.get("inode")
    socket = socket_map.get(inode)

    # La FK richiede che (node_id, inode)
    # esista in kernel.sockets.
    if not socket:
      continue

    connection["pid"] = socket["pid"]
    connection["fd"] = socket["fd"]

    valid_connections.append(connection)

  # Salva solamente connessioni con una
  # socket corrispondente.
  repository.insert_all(valid_connections)

  return {
    "connections": valid_connections
  }


def run(host, node_id):

  # Avvia la discovery del Transport Layer.
  return inspect_transport_layer(
    host,
    node_id
  )