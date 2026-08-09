import os
from pathlib import Path


def read():

  # Get the proc filesystem root.
  proc_path = os.getenv("PROC_PATH", "/proc")

  # Define the TCP IPv4 table.
  tcp_file = Path(proc_path) / "net" / "tcp"

  # Check if the file exists.
  if not tcp_file.exists():
    return []

  # Read all lines.
  with tcp_file.open("r") as file:
    lines = file.readlines()

  # Return the raw file content.
  return lines