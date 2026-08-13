from common.linux.remote import ssh


def get(host):
  # Esegue il comando per ottenere l'IP sul nodo remoto.
  output = ssh.execute(host, "hostname -I").strip()

  # Restituisce il primo indirizzo IP.
  return output.split()[0]