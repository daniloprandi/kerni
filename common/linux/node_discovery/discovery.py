from common.linux.node_discovery import hostname
from common.linux.node_discovery import ip
from common.linux.node_discovery import os
from common.linux.node_discovery import kernel
from common.linux.node_discovery import repository

from common.linux.tcp_ip.transport_layer import inspector

import json


def run(host):
  # Raccoglie le informazioni del nodo remoto tramite SSH.
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
    # Aggiorna le informazioni del nodo esistente.
    repository.update(node)

    # Imposta lo stato della discovery.
    node["status"] = "already_registered"
  else:
    # Inserisce il nuovo nodo nella CMDB.
    repository.insert(node)

    # Imposta lo stato della discovery.
    node["status"] = "registered"

  # Recupera il record del nodo appena registrato o aggiornato.
  node_record = repository.get_by_hostname(node["hostname"])

  # Estrae il node_id dal record.
  node_id = node_record[0]

  # Avvia automaticamente l'ispezione del Transport Layer.
  #
  # La discovery del nodo è quindi il punto di partenza
  # per la successiva raccolta delle connessioni TCP.
  try:
    inspector.inspect_transport_layer(host, node_id)
  except Exception as error:
    # Un errore nel Transport Layer non deve interrompere
    # la Node Discovery o il listener ICMP.
    print(
      f"Transport Layer discovery failed for {host}: {error}",
      flush=True
    )

  # Mostra il risultato della Node Discovery.
  print(json.dumps(node, indent=2))

  # Restituisce le informazioni del nodo.
  return node