# Importazione della funzione di parsing del layer data link
from .parser import parse_data_link_layer

# Interfaccia pubblica del modulo d'ispezione per il livello 2
def inspect_data_link():
  # Richiama l'elaborazione dei dati e ne restituisce il risultato finale
  return parse_data_link_layer()