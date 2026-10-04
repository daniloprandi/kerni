from common.linux.remote import ssh
from .parser import parse_transport
from .parser import parse_transport6
from .parser import parse_unix
from . import repository


def inspect_transport_layer(host, node_id):
  ssh_host = f"dprandi@{host}"

  connections = []

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

  valid_connections = []

  for connection in connections:
    connection["node_id"] = node_id
    valid_connections.append(connection)

  repository.insert_all(valid_connections)

  return {
    "connections": valid_connections
  }


def run(host, node_id):
  return inspect_transport_layer(host, node_id)