import csv
import subprocess
import time


# Tor SOCKS5 proxy
TOR_PROXY = "127.0.0.1:9150"


def collect_onion(onion):
  # Costruisce l'URL partendo dall'Onion address
  url = f"http://{onion}"

  # Salva il momento di inizio della richiesta
  start = time.time()

  # Esegue la richiesta HTTP passando attraverso Tor
  result = subprocess.run(
    [
      "curl",
      "--socks5-hostname",
      TOR_PROXY,
      "-i",
      "-s",
      "--max-time",
      "30",
      url
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
  )

  # Calcola il tempo impiegato dalla richiesta
  response_time = time.time() - start

  # Restituisce i dati raccolti
  return {
    "onion": onion,
    "response_time": response_time,
    "headers": result.stdout,
    "error": result.stderr
  }

# Apre il file CSV contenente gli Onion address
with open("data/onions.csv", newline="") as file:
  reader = csv.DictReader(file)

  # Analizza ogni Onion address presente nel CSV
  for row in reader:
    onion = row["onion"].strip()

    print(f"[*] Onion: {onion}")

    # Esegue la raccolta dei dati
    observation = collect_onion(onion)

    # Mostra il tempo di risposta
    print(f"Response time: {observation['response_time']:.2f}s")

    # Mostra gli header HTTP ricevuti
    print(observation["headers"])

    # Mostra eventuali errori restituiti da curl
    print(f"Error: {observation['error']}")

    print("-" * 60)