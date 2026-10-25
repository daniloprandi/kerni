# Modulo Parser per la normalizzazione dell'output di systemctl

def parse_systemd_services(lines):
  """
  Converte le linee grezze di systemctl in una lista di dizionari strutturati
  contenenti unità, stati e descrizione del servizio.
  """
  records = []
  
  for line in lines:
    parts = line.split(None, 4)
    if len(parts) >= 4:
      unit = parts[0]
      load_state = parts[1]
      active_state = parts[2]
      sub_state = parts[3]
      description = parts[4] if len(parts) > 4 else ''

      records.append({
        'unit': unit,
        'load_state': load_state,
        'active_state': active_state,
        'sub_state': sub_state,
        'description': description.strip()
      })
      
  return records