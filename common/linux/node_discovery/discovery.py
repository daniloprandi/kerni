from common.linux.node_discovery import hostname
from common.linux.node_discovery import ip
from common.linux.node_discovery import os
from common.linux.node_discovery import kernel
from common.linux.node_discovery import repository
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

  # Verifica se il nodo è già registrato.
  if repository.get_by_hostname(node["hostname"]):
    repository.update(node)
    node["status"] = "already_registered"
  else:
    repository.insert(node)
    node["status"] = "registered"

  # Mostra il risultato della discovery.
  print(json.dumps(node, indent=2))

  return node