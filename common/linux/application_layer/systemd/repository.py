# Modulo di persistenza per i servizi Systemd (Application Layer)
from common.database import get_connection

def save_systemd_services(node_id, records):
  # Apre la connessione al database
  con = get_connection()
  cursor = con.cursor()
  try:
    # Salva ogni servizio systemd mappando correttamente le colonne del DB
    for record in records:
      cursor.execute(
        """
        INSERT INTO application.systemd_services (node_id, unit, load_state, active_state, sub_state, description)
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
    # Conferma la transazione
    con.commit()
  except Exception as e:
    # In caso di eccezione esegue il rollback dei dati
    con.rollback()
    raise e
  finally:
    # Chiude cursore e connessione per evitare resource leaks
    cursor.close()
    con.close()