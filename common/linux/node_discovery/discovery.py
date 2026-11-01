import json
import socket

from common.linux.node_discovery import hostname
from common.linux.node_discovery import ip
from common.linux.node_discovery import os
from common.linux.node_discovery import kernel
from common.linux.node_discovery import repository

from common.linux.kernel.process import inspector as process_inspector
from common.linux.kernel.process import repository as process_repository
from common.linux.kernel.socket import inspector as socket_inspector
from common.linux.kernel.socket import repository as socket_repository
from common.linux.tcp_ip.transport_layer import inspector as transport_inspector

from common.linux.tcp_ip.data_link_layer import inspector as data_link_inspector
from common.linux.tcp_ip.data_link_layer import repository as data_link_repository

from common.linux.tcp_ip.internet_layer.arp import inspector as arp_inspector
from common.linux.tcp_ip.internet_layer.arp import repository as arp_repository

from common.linux.application_layer.systemd import inspector as systemd_inspector
from common.linux.application_layer.systemd import repository as systemd_repository


# Return the IP addresses associated with a hostname.
def _resolve_addresses(host):
  # Resolve the hostname and collect its IP addresses.
  try:
    return {
      info[4][0]
      for info in socket.getaddrinfo(host, None)
    }
  except socket.gaierror:
    # Return an empty set when the hostname cannot be resolved.
    return set()


# Determine whether the requested host is the local machine.
def _is_local_host(host):
  # Collect the local machine's known names.
  local_names = {
    socket.gethostname().lower(),
    socket.getfqdn().lower(),
    "localhost",
  }

  # Collect the local machine's known addresses.
  local_addresses = {
    "127.0.0.1",
    "::1",
  }

  # Resolve the local hostname to discover its addresses.
  local_addresses.update(_resolve_addresses(socket.gethostname()))

  # Resolve the requested host.
  target_addresses = _resolve_addresses(host)

  # Match the host by name or by resolved address.
  return (
    host.lower() in local_names
    or bool(target_addresses.intersection(local_addresses))
  )


# Run discovery for a node and persist the collected information.
def run(host):
  # Collect the node's basic information.
  node = {
    "hostname": hostname.get(host),
    "ip_addr": ip.get(host),
    "os_name": os.get_name(host),
    "os_v": os.get_version(host),
    "kernel_v": kernel.get(host),
    "status": "",
  }

  # Check whether the node is already registered in the CMDB.
  if repository.get_by_hostname(node["hostname"]):
    # Update the existing node record.
    repository.update(node)
    node["status"] = "already_registered"
  else:
    # Register the new node.
    repository.insert(node)
    node["status"] = "registered"

  # Retrieve the node identifier from the CMDB.
  node_record = repository.get_by_hostname(node["hostname"])
  node_id = node_record[0]

  # Discover processes on the requested host.
  try:
    # Inspect the remote or local processes.
    processes = process_inspector.inspect_processes(host)

    # Persist the discovered processes.
    process_repository.insert_all(processes, node_id)

    # Report the number of discovered processes.
    print(f"Processes discovered: {len(processes)}", flush=True)

  except Exception as error:
    # Report process discovery failures.
    print(
      f"Process discovery failed for {host}: {error}",
      flush=True,
    )

  # Discover sockets on the requested host.
  try:
    # Inspect the remote or local sockets.
    sockets = socket_inspector.inspect_sockets(host)

    # Persist the discovered sockets.
    socket_repository.insert_all(sockets, node_id)

    # Report the number of discovered sockets.
    print(f"Sockets discovered: {len(sockets)}", flush=True)

  except Exception as error:
    # Report socket discovery failures.
    print(
      f"Socket discovery failed for {host}: {error}",
      flush=True,
    )

  # Discover transport-layer connections on the requested host.
  try:
    # Inspect TCP and UDP transport information.
    transport_inspector.inspect_transport_layer(host, node_id)

  except Exception as error:
    # Report transport discovery failures.
    print(
      f"Transport Layer discovery failed for {host}: {error}",
      flush=True,
    )

  # Run local-only inspectors only when the target is this machine.
  if _is_local_host(host):
    # Discover local network interfaces.
    try:
      # Inspect the local Data Link Layer.
      data_link_records = data_link_inspector.inspect_data_link()

      # Persist the interface records.
      data_link_repository.save_data_link_data(
        node_id,
        data_link_records,
      )

      # Report the number of discovered interfaces.
      print(
        f"Data Link Layer discovered: {len(data_link_records)} interfaces",
        flush=True,
      )

    except Exception as error:
      # Report Data Link discovery failures.
      print(
        f"Data Link Layer discovery failed for {host}: {error}",
        flush=True,
      )

    # Discover the local ARP table.
    try:
      # Inspect the local ARP entries.
      arp_records = arp_inspector.inspect_arp()

      # Persist the ARP records.
      arp_repository.save_arp_data(node_id, arp_records)

      # Report the number of discovered ARP entries.
      print(
        f"ARP table discovered: {len(arp_records)} entries",
        flush=True,
      )

    except Exception as error:
      # Report ARP discovery failures.
      print(
        f"ARP table discovery failed for {host}: {error}",
        flush=True,
      )

    # Discover local systemd services.
    try:
      # Inspect the local systemd services.
      systemd_records = systemd_inspector.inspect_systemd()

      # Persist the service records.
      systemd_repository.save_systemd_services(
        node_id,
        systemd_records,
      )

      # Report the number of discovered services.
      print(
        f"Systemd services discovered: {len(systemd_records)} units",
        flush=True,
      )

    except Exception as error:
      # Report systemd discovery failures.
      print(
        f"Systemd services discovery failed for {host}: {error}",
        flush=True,
      )

  else:
    # Avoid attributing local data to a remote node.
    print(
      f"Skipping local-only Data Link, ARP, and systemd inspectors "
      f"for remote host {host}",
      flush=True,
    )

  # Print and return the node discovery result.
  print(json.dumps(node, indent=2))
  return node