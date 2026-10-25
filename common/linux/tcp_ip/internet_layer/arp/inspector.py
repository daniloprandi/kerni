# Modulo Inspector (Punto d'ingresso logico per l'ispezione ARP)

from common.linux.tcp_ip.internet_layer.arp.files import arp_reader
from common.linux.tcp_ip.internet_layer.arp import parser


def inspect_arp():
  """
  Coordina il flusso di lettura da filesystem e la successiva 
  normalizzazione tramite parser dei dati ARP.
  """
  # 1. Recupera le righe grezze tramite il modulo I/O
  raw_lines = arp_reader.read_arp_table()
  
  # 2. Converte i dati grezzi in record strutturati tramite il parser
  arp_records = parser.parse_arp_table(raw_lines)
  
  return arp_records