# Importazione del lettore delle informazioni fisiche delle interfacce
from .files.interfaces import read_interfaces
# Importazione del lettore dei contatori delle statistiche di traffico
from .files.stats import read_dev_stats

# Funzione principale di parsing per unificare i dati di livello 2
def parse_data_link_layer():
  # Lettura dell'elenco delle interfacce e relativi indirizzi MAC / stati
  interfaces = read_interfaces()
  # Lettura delle metriche convertite in dizionario con chiave nome interfaccia
  stats = {s['iface']: s for s in read_dev_stats()}
  
  # Lista per raccogliere i record finali unificati
  parsed_results = []
  # Ciclo di unificazione per ogni interfaccia censita
  for iface in interfaces:
    # Estrazione del nome tecnico dell'interfaccia
    name = iface['iface']
    # Recupero delle statistiche corrispondenti o valori zero di fallback
    iface_stats = stats.get(name, {'rx_bytes': 0, 'tx_bytes': 0})
    
    # Costruzione dell'oggetto finale combinato
    parsed_results.append({
      'iface': name,
      'eth_addr': iface['eth_addr'],
      'state': iface['state'],
      'rx_bytes': iface_stats['rx_bytes'],
      'tx_bytes': iface_stats['tx_bytes']
    })
    
  # Restituisce la struttura dati pronta per essere salvata o ispezionata
  return parsed_results