# Modulo I/O per la lettura della tabella ARP dal filesystem virtuale del kernel

def read_arp_table():
  """
  Legge la tabella ARP direttamente dal file di pseudo-kernel /proc/net/arp.
  Restituisce una lista di stringhe grezze corrispondenti alle righe del file.
  """
  try:
    # Apertura e lettura sicura del file di sistema secondo la filosofia Linux
    with open('/proc/net/arp', 'r') as f:
      return f.readlines()
  except Exception as error:
    # Gestione protetta dell'errore di I/O senza interrompere il demone
    print(f'Failed to read /proc/net/arp: {error}', flush=True)
    return []