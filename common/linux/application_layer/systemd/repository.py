# Modulo Repository per la persistenza dei servizi systemd su database PostgreSQL

from common.database import get_connection


def save_systemd_services(node_id, services):
  """
  Salva i servizi systemd rilevati all'interno della tabella relazionale 
  dedicata nel database PostgreSQL (application.systemd_services).
  """
  con = get_connection()
  cursor = con.cursor()
  
  try:
    for svc in services:
      cursor.execute('''
        INSERT INTO application.systemd_services 
        (node_id, unit, load_state, active_state, sub_state, description)
        VALUES (%s, %s, %s, %s, %s, %s)
      ''', (
        node_id,
        svc['unit'],
        svc['load_state'],
        svc['active_state'],
        svc['sub_state'],
        svc['description']
      ))
      
    con.commit()
    
  except Exception as e:
    con.rollback()
    raise e
    
  finally:
    cursor.close()
    con.close()