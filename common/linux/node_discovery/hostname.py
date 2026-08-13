from common.linux.remote import ssh



def get(host):
  # Esegue il comando hostname sul nodo remoto.
  return ssh.execute(host, "hostname").strip()