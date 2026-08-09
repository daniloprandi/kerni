import os
from pathlib import Path


def read():

  # Get the proc filesystem root.
  proc_path = os.getenv("PROC_PATH", "/proc")

  # Define the Unix Domain Socket table.
  unix_file = Path(proc_path) / "net" / "unix"

  # Check if the file exists.
  if not unix_file.exists():
    return []

  # Read all lines.
  with unix_file.open("r") as file:
    lines = file.readlines()

  # Return the raw file content.
  return lines