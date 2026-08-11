# Transport Layer Inspector.

# Coordinates the inspection of the Linux Transport Layer.

from common.linux.node_discovery import repository as node_repository
from common.linux.remote import ssh

from .parser import parse_transport
from .parser import parse_transport6
from .parser import parse_unix

from . import repository


# Inspect the Linux Transport Layer.

def inspect_transport_layer():

  # Get all registered nodes.

  nodes = node_repository.get_all()

  # Store every transport connection.

  connections = []

  # Inspect every registered node.

  for node in nodes:

    # Get the node information.

    node_id = node[0]
    ip_addr = node[2]

    # Build the SSH host.

    host = f"dprandi@{ip_addr}"

    # Read the Linux TCP table.

    tcp_data = ssh.execute(
      host,
      "cat /proc/net/tcp"
    )

    # Parse the Linux TCP table.

    connections.extend(
      parse_transport(
        tcp_data.splitlines(),
        "TCP"
      )
    )

    # Read the Linux TCP6 table.

    tcp6_data = ssh.execute(
      host,
      "cat /proc/net/tcp6"
    )

    # Parse the Linux TCP6 table.

    connections.extend(
      parse_transport6(
        tcp6_data.splitlines(),
        "TCP6"
      )
    )

    # Read the Linux UDP table.

    udp_data = ssh.execute(
      host,
      "cat /proc/net/udp"
    )

    # Parse the Linux UDP table.

    connections.extend(
      parse_transport(
        udp_data.splitlines(),
        "UDP"
      )
    )

    # Read the Linux UDP6 table.

    udp6_data = ssh.execute(
      host,
      "cat /proc/net/udp6"
    )

    # Parse the Linux UDP6 table.

    connections.extend(
      parse_transport6(
        udp6_data.splitlines(),
        "UDP6"
      )
    )

    # Read the Linux RAW table.

    raw_data = ssh.execute(
      host,
      "cat /proc/net/raw"
    )

    # Parse the Linux RAW table.

    connections.extend(
      parse_transport(
        raw_data.splitlines(),
        "RAW"
      )
    )

    # Read the Linux RAW6 table.

    raw6_data = ssh.execute(
      host,
      "cat /proc/net/raw6"
    )

    # Parse the Linux RAW6 table.

    connections.extend(
      parse_transport6(
        raw6_data.splitlines(),
        "RAW6"
      )
    )

    # Read the Linux UNIX table.

    unix_data = ssh.execute(
      host,
      "cat /proc/net/unix"
    )

    # Parse the Linux UNIX table.

    connections.extend(
      parse_unix(
        unix_data.splitlines(),
        "UNIX"
      )
    )

    # Associate every connection to the node.

    for connection in connections:
      connection["node_id"] = node_id

  # Store all connections.

  repository.insert_all(connections)

  # Return the inspection result.

  return {
    "connections": connections
  }


# Run the Transport Layer inspection.

def run():

  # Execute the inspection.

  return inspect_transport_layer()