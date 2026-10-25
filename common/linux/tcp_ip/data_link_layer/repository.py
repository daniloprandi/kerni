# Importazione della funzione per ottenere la connessione al database
from common.database import get_connection

# Funzione per salvare le interfacce rilevate nella tabella PostgreSQL
def save_data_link_data(node_id, data_link_records):
  # Creazione dell'oggetto di connessione verso il database
  conn = get_connection()
  # Creazione del cursore per eseguire i comandi SQL
  cursor = conn.cursor()
  try:
    # Scansione di ciascun record presente nella lista da inserire
    for record in data_link_records:
      # Esecuzione della query di INSERT con i nuovi campi abbreviati
      cursor.execute('''
        INSERT INTO tcpip.network_interfaces 
        (node_id, iface, eth_addr, state, rx_bytes, tx_bytes)
        VALUES (%s, %s, %s, %s, %s, %s)
      ''', (
        node_id,
        record['iface'],
        record['eth_addr'],
        record['state'],
        record['rx_bytes'],
        record['tx_bytes']
      ))
    # Conferma la transazione scrivendo le modifiche nel DB
    conn.commit()
  except Exception as e:
    # In caso di errore annulla tutte le modifiche pendenti della transazione
    conn.rollback()
    # Rilancia l'eccezione per la gestione a livello superiore
    raise e
  finally:
    # Chiusura del cursore SQL
    cursor.close()
    # Rilascio e chiusura della connessione al database
    conn.close()