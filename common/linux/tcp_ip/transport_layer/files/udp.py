import os
from pathlib import Path


def read():

  # Get the proc filesystem root.
  proc_path = os.getenv("PROC_PATH", "/proc")

  # Define the UDP IPv4 table.
  udp_file = Path(proc_path) / "net" / "udp"

  # Check if the file exists.
  if not udp_file.exists():
    return []

  # Read all lines.
  with udp_file.open("r") as file:
    lines = file.readlines()

  # Return the raw file content.
  return lines