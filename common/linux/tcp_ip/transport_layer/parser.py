import ipaddress
import socket

from common.linux.users import user


# Convert a hexadecimal IPv4 address to dotted notation.
def parse_ip(ip):

  # Convert the hexadecimal value into bytes.
  ip_bytes = bytes.fromhex(ip)

  # Reverse the Linux byte order.
  ip_bytes = ip_bytes[::-1]

  # Return the IPv4 address.
  return socket.inet_ntoa(ip_bytes)


# Convert a hexadecimal IPv6 address to standard notation.
def parse_ip6(ip):

  # Convert the hexadecimal value into bytes.
  ip_bytes = bytes.fromhex(ip)

  # Return the IPv6 address.
  return str(ipaddress.IPv6Address(ip_bytes))


# Convert a hexadecimal port into decimal.
def parse_port(port):

  # Return the decimal port.
  return int(port, 16)


# Parse an IPv4 endpoint.
def parse_endpoint(endpoint):

  # Split IP and port.
  ip, port = endpoint.split(":")

  # Return the parsed endpoint.
  return parse_ip(ip), parse_port(port)


# Parse an IPv6 endpoint.
def parse_endpoint6(endpoint):

  # Split IP and port.
  ip, port = endpoint.split(":")

  # Return the parsed endpoint.
  return parse_ip6(ip), parse_port(port)


# Parse a Linux TCP state.
def parse_transport_state(state):

  # Linux transport states.
  states = {

    "01": "ESTABLISHED",
    "02": "SYN_SENT",
    "03": "SYN_RECV",
    "04": "FIN_WAIT1",
    "05": "FIN_WAIT2",
    "06": "TIME_WAIT",
    "07": "CLOSE",
    "08": "CLOSE_WAIT",
    "09": "LAST_ACK",
    "0A": "LISTEN",
    "0B": "CLOSING"

  }

  # Return the parsed state.
  return states.get(state, state)


# Parse a UNIX socket type.
def parse_unix_type(socket_type):

  # Linux UNIX socket types.
  types = {

    "0001": "STREAM",
    "0002": "DGRAM",
    "0005": "SEQPACKET"

  }

  # Return the parsed type.
  return types.get(socket_type, socket_type)


# Parse a UNIX socket state.
def parse_unix_state(state):

  # Linux UNIX socket states.
  states = {

    "01": "UNCONNECTED",
    "02": "CONNECTING",
    "03": "CONNECTED",
    "04": "DISCONNECTING"

  }

  # Return the parsed state.
  return states.get(state, state)


# Parse an IPv4 transport table.
def parse_transport(lines, proto):

  # Ignore the header.
  lines = lines[1:]

  # Store the parsed connections.
  connections = []

  # Parse every entry.
  for line in lines:

    # Split the columns.
    fields = line.split()

    # Parse the source endpoint.
    src_ip, src_port = parse_endpoint(fields[1])

    # Parse the destination endpoint.
    dst_ip, dst_port = parse_endpoint(fields[2])

    # Read the Linux user identifier.
    uid = int(fields[7])

    # Read the Linux username.
    username = user.get_username(uid)

    # Store the parsed connection.
    connections.append({

      "proto": proto,

      "src_ip": src_ip,
      "src_port": src_port,

      "dst_ip": dst_ip,
      "dst_port": dst_port,

      "state": parse_transport_state(fields[3]),

      "uid": uid,

      "username": username,

      "inode": int(fields[9]),

      "type": None,

      "flags": None,

      "path": None

    })

  # Return the parsed connections.
  return connections


# Parse an IPv6 transport table.
def parse_transport6(lines, proto):

  # Ignore the header.
  lines = lines[1:]

  # Store the parsed connections.
  connections = []

  # Parse every entry.
  for line in lines:

    # Split the columns.
    fields = line.split()

    # Parse the source endpoint.
    src_ip, src_port = parse_endpoint6(fields[1])

    # Parse the destination endpoint.
    dst_ip, dst_port = parse_endpoint6(fields[2])

    # Read the Linux user identifier.
    uid = int(fields[7])

    # Read the Linux username.
    username = user.get_username(uid)

    # Store the parsed connection.
    connections.append({

      "proto": proto,

      "src_ip": src_ip,
      "src_port": src_port,

      "dst_ip": dst_ip,
      "dst_port": dst_port,

      "state": parse_transport_state(fields[3]),

      "uid": uid,

      "username": username,

      "inode": int(fields[9]),

      "type": None,

      "flags": None,

      "path": None

    })

  # Return the parsed connections.
  return connections


# Parse the Linux UNIX table.
def parse_unix(lines, proto):

  # Ignore the header.
  lines = lines[1:]

  # Store the parsed sockets.
  connections = []

  # Parse every entry.
  for line in lines:

    # Split the columns.
    fields = line.split()

    # Skip invalid rows.
    if len(fields) < 7:
      continue

    # Read the socket path.
    path = None

    if len(fields) > 7:
      path = " ".join(fields[7:])

    # Linux root user.
    uid = 0

    # Read the Linux username.
    username = user.get_username(uid)

    # Store the parsed socket.
    connections.append({

      "proto": proto,

      "src_ip": None,
      "src_port": None,

      "dst_ip": None,
      "dst_port": None,

      "state": parse_unix_state(fields[5]),

      "uid": uid,

      "username": username,

      "inode": int(fields[6]),

      "type": parse_unix_type(fields[4]),

      "flags": fields[3],

      "path": path

    })

  # Return the parsed sockets.
  return connections