from common.linux.node_discovery import hostname
from common.linux.node_discovery import ip
from common.linux.node_discovery import os
from common.linux.node_discovery import kernel
from common.linux.node_discovery import repository
import json


def run():

  node = {
    "hostname": hostname.get(),
    "ip_addr": ip.get(),
    "os_name": os.get_name(),
    "os_v": os.get_version(),
    "kernel_v": kernel.get(),
    "status": ""
  }

  if repository.get_by_hostname(node["hostname"]):
    repository.update(node)
    node["status"] = "already_registered"
  else:
    repository.insert(node)
    node["status"] = "registered"

  print(json.dumps(node, indent=2))

  return node