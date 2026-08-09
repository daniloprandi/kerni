# Transport Layer Inspector.

# Coordinates the inspection of the Linux Transport Layer.

from common.linux.node_discovery import hostname
from common.linux.node_discovery import repository as node_repository

from .files import tcp
from .files import tcp6
from .files import udp
from .files import udp6
from .files import raw
from .files import raw6
from .files import unix

from .parser import parse_transport
from .parser import parse_transport6
from .parser import parse_unix

from . import repository


# Inspect the Linux Transport Layer.
def inspect_transport_layer():

  # Get the local hostname.
  hostname_value = hostname.get()

  # Get the node information.
  node = node_repository.get_by_hostname(hostname_value)

  # Stop if the node is not registered.
  if node is None:
    return {
      "error": "Node not registered."
    }

  # Store every transport connection.
  connections = []

  # Parse the Linux TCP table.
  connections.extend(
    parse_transport(
      tcp.read(),
      "TCP"
    )
  )

  # Parse the Linux TCP6 table.
  connections.extend(
    parse_transport6(
      tcp6.read(),
      "TCP6"
    )
  )

  # Parse the Linux UDP table.
  connections.extend(
    parse_transport(
      udp.read(),
      "UDP"
    )
  )

  # Parse the Linux UDP6 table.
  connections.extend(
    parse_transport6(
      udp6.read(),
      "UDP6"
    )
  )

  # Parse the Linux RAW table.
  connections.extend(
    parse_transport(
      raw.read(),
      "RAW"
    )
  )

  # Parse the Linux RAW6 table.
  connections.extend(
    parse_transport6(
      raw6.read(),
      "RAW6"
    )
  )

  # Parse the Linux UNIX table.
  connections.extend(
    parse_unix(
      unix.read(),
      "UNIX"
    )
  )

  # Associate every connection to the node.
  for connection in connections:

    # Set the node identifier.
    connection["node_id"] = node[0]

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