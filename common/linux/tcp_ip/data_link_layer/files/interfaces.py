# Modulo di sistema per interagire con il filesystem
import os

# Funzione per accedere ai file virtuali delle interfacce in /sys/class/net/
def read_interfaces():
  # Percorso della directory virtuale del kernel contenente le schede di rete
  net_path = '/sys/class/net'
  # Verifica che la directory /sys/class/net esista nel sistema in esecuzione
  if not os.path.exists(net_path):
    # Restituisce una lista vuota se la directory non viene trovata
    return []
  
  # Lista per memorizzare i dizionari delle interfacce lette
  interfaces = []
  # Scansione di ogni voce (interfaccia) presente nella cartella /sys/class/net/
  for iface in os.listdir(net_path):
    # Costruzione del percorso assoluto per la singola interfaccia di rete
    iface_path = os.path.join(net_path, iface)
    
    # Valore predefinito per l'indirizzo MAC in caso di assenza o errore
    eth_addr = '00:00:00:00:00:00'
    # Percorso del file virtuale contenente l'indirizzo MAC
    mac_file = os.path.join(iface_path, 'address')
    # Controlla se il file 'address' esiste per l'interfaccia corrente
    if os.path.exists(mac_file):
      try:
        # Apertura in lettura del file del MAC address
        with open(mac_file, 'r') as f:
          # Lettura del contenuto e rimozione degli spazi o a capo finali
          eth_addr = f.read().strip()
      except Exception:
        # In caso di errore durante la lettura mantiene il valore predefinito
        pass

    # Valore predefinito per lo stato operativo dell'interfaccia
    state = 'unknown'
    # Percorso del file virtuale contenente lo stato operativo (operstate)
    state_file = os.path.join(iface_path, 'operstate')
    # Controlla se il file 'operstate' esiste per l'interfaccia corrente
    if os.path.exists(state_file):
      try:
        # Apertura in lettura del file dello stato operativo
        with open(state_file, 'r') as f:
          # Lettura dello stato (es. 'up', 'down') senza spazi di contorno
          state = f.read().strip()
      except Exception:
        # In caso di errore mantiene lo stato predefinito 'unknown'
        pass

    # Aggiunge i dati letti dell'interfaccia alla lista di destinazione
    interfaces.append({
      'iface': iface,
      'eth_addr': eth_addr,
      'state': state
    })
    
  # Restituisce la struttura dati completa con tutte le interfacce rilevate
  return interfaces