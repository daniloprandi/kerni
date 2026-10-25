# Modulo Inspector (Punto d'ingresso logico per i servizi systemd)

from common.linux.application_layer.systemd.files import systemd_reader
from common.linux.application_layer.systemd import parser


def inspect_systemd():
  """
  Coordina l'esecuzione del comando di sistema e la normalizzazione
  tramite il parser dei servizi systemd.
  """
  raw_lines = systemd_reader.read_systemd_services()
  return parser.parse_systemd_services(raw_lines)