# Modulo di persistenza per il Data Link Layer (Interfacce di rete)
from common.database import get_connection


def save_data_link_data(node_id, records):
  # Non sostituisce lo snapshot se la raccolta non ha prodotto dati.
  # In questo modo un errore del collector non cancella dati validi.
  if not records:
    return

  con = get_connection()
  cursor = con.cursor()
  try:
    # Sostituisce lo snapshot del nodo nella stessa transazione.
    cursor.execute(
      "DELETE FROM tcpip.network_interfaces WHERE node_id = %s",
      (node_id,)
    )

    # Inserisce lo snapshot appena raccolto.
    for record in records:
      cursor.execute(
        """
        INSERT INTO tcpip.network_interfaces
          (node_id, iface, eth_addr, state, rx_bytes, tx_bytes)
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

    # Conferma insieme eliminazione e inserimento.
    con.commit()
  except Exception:
    # Ripristina anche i record eliminati se l'inserimento fallisce.
    con.rollback()
    raise
  finally:
    cursor.close()
    con.close()