from common.linux.remote import ssh


def get_name(host):
  # Esegue il comando per ottenere il sistema operativo sul nodo remoto.
  return ssh.execute(host, "uname -s").strip()


def get_version(host):
  # Esegue il comando per ottenere la versione del sistema operativo.
  return ssh.execute(host, "uname -r").strip()