# Modulo di persistenza per i servizi Systemd (Application Layer)
from common.database import get_connection


def save_systemd_services(node_id, records):
  # Non elimina dati esistenti quando la raccolta è vuota o fallita.
  if not records:
    return

  con = get_connection()
  cursor = con.cursor()
  try:
    # Sostituisce lo snapshot dei servizi del nodo in modo atomico.
    cursor.execute(
      "DELETE FROM application.systemd_services WHERE node_id = %s",
      (node_id,)
    )

    # Inserisce i servizi rilevati.
    for record in records:
      cursor.execute(
        """
        INSERT INTO application.systemd_services
          (node_id, unit, load_state, active_state, sub_state, description)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
          node_id,
          record.get('unit') or record.get('unit_name'),
          record.get('load_state'),
          record.get('active_state'),
          record.get('sub_state'),
          record.get('description')
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