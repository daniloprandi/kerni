# Transport Layer Inspector.

# Coordinates the inspection of the Linux Transport Layer.

from common.linux.remote import ssh

from .parser import parse_transport
from .parser import parse_transport6
from .parser import parse_unix

from . import repository


# Inspect the Linux Transport Layer of a specific node.
def inspect_transport_layer(host, node_id):

  # Build the SSH host.
  ssh_host = f"dprandi@{host}"

  # Store all connections discovered on the node.
  connections = []

  # Read the Linux TCP table.
  tcp_data = ssh.execute(
    ssh_host,
    "cat /proc/net/tcp"
  )

  # Parse the Linux TCP table.
  connections.extend(
    parse_transport(
      tcp_data.splitlines(),
      "TCP"
    )
  )

  # Read the Linux TCP IPv6 table.
  tcp6_data = ssh.execute(
    ssh_host,
    "cat /proc/net/tcp6"
  )

  # Parse the Linux TCP IPv6 table.
  connections.extend(
    parse_transport6(
      tcp6_data.splitlines(),
      "TCP6"
    )
  )

  # Read the Linux UDP table.
  udp_data = ssh.execute(
    ssh_host,
    "cat /proc/net/udp"
  )

  # Parse the Linux UDP table.
  connections.extend(
    parse_transport(
      udp_data.splitlines(),
      "UDP"
    )
  )

  # Read the Linux UDP IPv6 table.
  udp6_data = ssh.execute(
    ssh_host,
    "cat /proc/net/udp6"
  )

  # Parse the Linux UDP IPv6 table.
  connections.extend(
    parse_transport6(
      udp6_data.splitlines(),
      "UDP6"
    )
  )

  # Read the Linux RAW table.
  raw_data = ssh.execute(
    ssh_host,
    "cat /proc/net/raw"
  )

  # Parse the Linux RAW table.
  connections.extend(
    parse_transport(
      raw_data.splitlines(),
      "RAW"
    )
  )

  # Read the Linux RAW IPv6 table.
  raw6_data = ssh.execute(
    ssh_host,
    "cat /proc/net/raw6"
  )

  # Parse the Linux RAW IPv6 table.
  connections.extend(
    parse_transport6(
      raw6_data.splitlines(),
      "RAW6"
    )
  )

  # Read the Linux UNIX socket table.
  unix_data = ssh.execute(
    ssh_host,
    "cat /proc/net/unix"
  )

  # Parse the Linux UNIX socket table.
  connections.extend(
    parse_unix(
      unix_data.splitlines(),
      "UNIX"
    )
  )

  # Associate every connection with the discovered node.
  for connection in connections:
    connection["node_id"] = node_id

  # Store all discovered connections in PostgreSQL.
  repository.insert_all(connections)

  # Return the discovered connections.
  return {
    "connections": connections
  }


# Run the Transport Layer inspection.
def run(host, node_id):

  # Execute the inspection for the specified node.
  return inspect_transport_layer(
    host,
    node_id
  )