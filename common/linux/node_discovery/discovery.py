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

# Importazione dell'inspector e del repository per il Data Link Layer (Livello 2)
from common.linux.tcp_ip.data_link_layer import inspector as data_link_inspector
from common.linux.tcp_ip.data_link_layer import repository as data_link_repository

# Importazione dell'inspector e del repository per l'Internet Layer - ARP (Livello 3)
from common.linux.tcp_ip.internet_layer.arp import inspector as arp_inspector
from common.linux.tcp_ip.internet_layer.arp import repository as arp_repository

# Importazione dell'inspector e del repository per l'Application Layer - Systemd (Livello 7)
from common.linux.application_layer.systemd import inspector as systemd_inspector
from common.linux.application_layer.systemd import repository as systemd_repository

import json


def run(host):
  # Raccoglie le informazioni del nodo remoto.
  node = {
    'hostname': hostname.get(host),
    'ip_addr': ip.get(host),
    'os_name': os.get_name(host),
    'os_v': os.get_version(host),
    'kernel_v': kernel.get(host),
    'status': ''
  }

  # Verifica se il nodo è già registrato nella CMDB.
  if repository.get_by_hostname(node['hostname']):
    repository.update(node)
    node['status'] = 'already_registered'
  else:
    repository.insert(node)
    node['status'] = 'registered'

  # Recupera il node_id.
  node_record = repository.get_by_hostname(node['hostname'])
  node_id = node_record[0]

  # Discovery dei processi.
  try:
    processes = process_inspector.inspect_processes(host)

    process_repository.insert_all(
      processes,
      node_id
    )

    print(
      f'Processes discovered: {len(processes)}',
      flush=True
    )

  except Exception as error:
    print(
      f'Process discovery failed for {host}: {error}',
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
      f'Sockets discovered: {len(sockets)}',
      flush=True
    )

  except Exception as error:
    print(
      f'Socket discovery failed for {host}: {error}',
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
      f'Transport Layer discovery failed for {host}: {error}',
      flush=True
    )

  # Discovery del Data Link Layer (Livello 2).
  try:
    data_link_records = data_link_inspector.inspect_data_link()

    data_link_repository.save_data_link_data(
      node_id,
      data_link_records
    )

    print(
      f'Data Link Layer discovered: {len(data_link_records)} interfaces',
      flush=True
    )

  except Exception as error:
    print(
      f'Data Link Layer discovery failed for {host}: {error}',
      flush=True
    )

  # Discovery del Network / Internet Layer - ARP (Livello 3).
  try:
    arp_records = arp_inspector.inspect_arp()

    arp_repository.save_arp_data(
      node_id,
      arp_records
    )

    print(
      f'ARP table discovered: {len(arp_records)} entries',
      flush=True
    )

  except Exception as error:
    print(
      f'ARP table discovery failed for {host}: {error}',
      flush=True
    )

  # Discovery dell'Application Layer - Systemd Services (Livello 7).
  try:
    systemd_records = systemd_inspector.inspect_systemd()

    systemd_repository.save_systemd_services(
      node_id,
      systemd_records
    )

    print(
      f'Systemd services discovered: {len(systemd_records)} units',
      flush=True
    )

  except Exception as error:
    print(
      f'Systemd services discovery failed for {host}: {error}',
      flush=True
    )

  # Mostra il risultato della Node Discovery.
  print(
    json.dumps(node, indent=2)
  )

  return node