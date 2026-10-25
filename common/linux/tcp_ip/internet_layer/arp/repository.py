# Modulo Repository per la persistenza dei dati ARP su database PostgreSQL

from common.database import get_connection


def save_arp_data(node_id, arp_records):
  """
  Salva i record ARP rilevati all'interno della tabella relazionale 
  dedicata nel database PostgreSQL (tcpip.arp_table).
  """
  # Ottiene la connessione standard condivisa dal modulo di database
  con = get_connection()
  cursor = con.cursor()
  
  try:
    # Esegue l'inserimento ciclico o batch dei record associati al nodo
    for record in arp_records:
      cursor.execute('''
        INSERT INTO tcpip.arp_table 
        (node_id, ip_addr, mac_addr, iface, flags)
        VALUES (%s, %s, %s, %s, %s)
      ''', (
        node_id,
        record['ip_addr'],
        record['mac_addr'],
        record['iface'],
        record['flags']
      ))
      
    # Conferma definitiva della transazione sul database
    con.commit()
    
  except Exception as e:
    # Annulla le modifiche in caso di errore critico (rollback)
    con.rollback()
    raise e
    
  finally:
    # Chiusura sicura del cursore e rilascio della connessione
    cursor.close()
    con.close()