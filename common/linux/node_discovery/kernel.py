from common.linux.remote import ssh


def get(host):
  # Esegue il comando per ottenere la versione del kernel sul nodo remoto.
  return ssh.execute(host, "uname -r").strip()