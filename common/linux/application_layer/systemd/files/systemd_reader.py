# Modulo I/O per l'esecuzione del comando di sistema systemctl
import subprocess


def read_systemd_services():
  """
  Esegue il comando systemctl per elencare tutti i servizi configurati e attivi,
  restituendo le linee di output grezze.
  """
  try:
    result = subprocess.run(
      ['systemctl', 'list-units', '--type=service', '--all', '--no-pager', '--no-legend'],
      capture_output=True,
      text=True,
      check=True
    )
    return result.stdout.splitlines()
  except Exception as error:
    print(f'Failed to execute systemctl: {error}', flush=True)
    return []