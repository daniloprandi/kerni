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

import json


def run(host):
  # Raccoglie le informazioni del nodo remoto.
  node = {
    "hostname": hostname.get(host),
    "ip_addr": ip.get(host),
    "os_name": os.get_name(host),
    "os_v": os.get_version(host),
    "kernel_v": kernel.get(host),
    "status": ""
  }

  # Verifica se il nodo è già registrato nella CMDB.
  if repository.get_by_hostname(node["hostname"]):
    repository.update(node)
    node["status"] = "already_registered"
  else:
    repository.insert(node)
    node["status"] = "registered"

  # Recupera il node_id.
  node_record = repository.get_by_hostname(node["hostname"])
  node_id = node_record[0]

  # Discovery dei processi.
  try:
    processes = process_inspector.inspect_processes(host)

    process_repository.insert_all(
      processes,
      node_id
    )

    print(
      f"Processes discovered: {len(processes)}",
      flush=True
    )

  except Exception as error:
    print(
      f"Process discovery failed for {host}: {error}",
      flush=True
    )

  # Discovery dei socket.
  try:
    sockets = socket_inspector.inspect_sockets(host)

    socket_repository.insert_all(
      sockets,
      node_id
    )

    print(
      f"Sockets discovered: {len(sockets)}",
      flush=True
    )

  except Exception as error:
    print(
      f"Socket discovery failed for {host}: {error}",
      flush=True
    )

  # Discovery del Transport Layer.
  try:
    transport_inspector.inspect_transport_layer(
      host,
      node_id
    )

  except Exception as error:
    print(
      f"Transport Layer discovery failed for {host}: {error}",
      flush=True
    )

  # Mostra il risultato della Node Discovery.
  print(
    json.dumps(node, indent=2)
  )

  return node