# Modulo di persistenza per la tabella ARP (Internet Layer)
from common.database import get_connection

def save_arp_data(node_id, records):
  # Ottiene la connessione attiva al database
  con = get_connection()
  cursor = con.cursor()
  try:
    # Itera sui record ARP mappando correttamente le colonne del DB
    for record in records:
      cursor.execute(
        """
        INSERT INTO tcpip.arp_table (node_id, ip_addr, mac_addr, iface, flags)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
          node_id,
          record.get('ip_addr') or record.get('ip_address'),
          record.get('mac_addr') or record.get('mac_address'),
          record.get('iface') or record.get('interface'),
          record.get('flags')
        )
      )
    # Finalizza la transazione con il commit
    con.commit()
  except Exception as e:
    # Annulla la transazione in caso di fallimento
    con.rollback()
    raise e
  finally:
    # Rilascia le risorse aperte
    cursor.close()
    con.close()