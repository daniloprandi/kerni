# Modulo Parser per la normalizzazione dei dati ARP grezzi

def parse_arp_table(lines):
  """
  Converte le linee grezze lette da /proc/net/arp in una lista 
  di dizionari strutturati e normalizzati.
  """
  records = []
  
  # Verifica che siano presenti almeno le intestazioni e una riga di dati
  if not lines or len(lines) <= 1:
    return records

  # Scandisce le righe saltando l'intestazione (prima riga)
  for line in lines[1:]:
    parts = line.split()
    # Una riga ARP valida di /proc/net/arp contiene almeno 6 colonne principali
    if len(parts) >= 6:
      records.append({
        'ip_addr': parts[0],   # Indirizzo IP del nodo noto
        'mac_addr': parts[3],  # Indirizzo MAC (hardware address)
        'iface': parts[5],     # Interfaccia di rete associata
        'flags': parts[2]      # Flag di stato della voce ARP
      })
      
  return records