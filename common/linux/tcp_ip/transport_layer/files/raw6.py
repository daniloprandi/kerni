import os
from pathlib import Path


def read():

  # Get the proc filesystem root.
  proc_path = os.getenv("PROC_PATH", "/proc")

  # Define the RAW IPv6 table.
  raw_file = Path(proc_path) / "net" / "raw6"

  # Check if the file exists.
  if not raw_file.exists():
    return []

  # Read all lines.
  with raw_file.open("r") as file:
    lines = file.readlines()

  # Return the raw file content.
  return lines