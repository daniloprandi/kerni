# Modulo di sistema per la verifica dei percorsi
import os

# Funzione per leggere le metriche cumulative di rete da /proc/net/dev
def read_dev_stats():
  # Percorso del file di testo del kernel contenente i contatori di rete
  dev_file = '/proc/net/dev'
  # Verifica la presenza del file /proc/net/dev nel sistema
  if not os.path.exists(dev_file):
    # Se il file non esiste restituisce una lista vuota
    return []
  
  # Lista contenente le statistiche elaborate per ciascuna interfaccia
  stats = []
  try:
    # Apertura del file /proc/net/dev in sola lettura
    with open(dev_file, 'r') as f:
      # Lettura di tutte le righe del file
      lines = f.readlines()
      # Scarta le prime due righe che contengono solo intestazioni di colonna
      for line in lines[2:]:
        # Separazione del nome dell'interfaccia dai valori mediante il carattere ':'
        parts = line.strip().split(':')
        # Salta la riga se non rispetta il formato atteso (interfaccia: dati)
        if len(parts) < 2:
          continue
        # Estrazione e pulizia del nome dell'interfaccia
        iface_name = parts[0].strip()
        # Separazione di tutti i contatori numerici delimitati da spazi
        values = parts[1].strip().split()
        # Verifica la presenza di almeno 9 campi (RX bytes in pos 0, TX bytes in pos 8)
        if len(values) >= 9:
          # Aggiunta del dizionario con i contatori convertiti in interi
          stats.append({
            'iface': iface_name,
            'rx_bytes': int(values[0]),
            'tx_bytes': int(values[8])
          })
  except Exception:
    # Ignora eventuali errori di I/O restituendo le metriche lette finora
    pass
    
  # Restituisce l'insieme delle statistiche estratte da /proc/net/dev
  return stats