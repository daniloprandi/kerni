# Modulo di persistenza per il Data Link Layer (Interfacce di rete)
from common.database import get_connection

def save_data_link_data(node_id, records):
  # Ottiene la connessione attiva al database
  con = get_connection()
  cursor = con.cursor()
  try:
    # Itera sui record e inserisce i dati gestendo i fallback delle chiavi
    for record in records:
      cursor.execute(
        """
        INSERT INTO tcpip.network_interfaces (node_id, iface, eth_addr, state, rx_bytes, tx_bytes)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
          node_id,
          record.get('iface') or record.get('interface_name') or record.get('name'),
          record.get('eth_addr') or record.get('mac_address'),
          record.get('state'),
          record.get('rx_bytes', 0),
          record.get('tx_bytes', 0)
        )
      )
    # Esegue il commit delle modifiche transazionali
    con.commit()
  except Exception as e:
    # Effettua il rollback in caso di errore SQL
    con.rollback()
    raise e
  finally:
    # Chiude in modo sicuro cursore e connessione
    cursor.close()
    con.close()