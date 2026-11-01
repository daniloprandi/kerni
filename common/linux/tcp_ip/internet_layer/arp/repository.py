# Modulo di persistenza per la tabella ARP (Internet Layer)
from common.database import get_connection


def save_arp_data(node_id, records):
  # Non elimina dati esistenti quando la raccolta è vuota o fallita.
  if not records:
    return

  con = get_connection()
  cursor = con.cursor()
  try:
    # Sostituisce lo snapshot ARP del nodo in modo atomico.
    cursor.execute(
      "DELETE FROM tcpip.arp_table WHERE node_id = %s",
      (node_id,)
    )

    # Inserisce le nuove entry ARP.
    for record in records:
      cursor.execute(
        """
        INSERT INTO tcpip.arp_table
          (node_id, ip_addr, mac_addr, iface, flags)
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

    # Conferma insieme eliminazione e inserimento.
    con.commit()
  except Exception:
    # Ripristina lo snapshot precedente in caso di errore.
    con.rollback()
    raise
  finally:
    cursor.close()
    con.close()