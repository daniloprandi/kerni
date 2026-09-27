import os
import re


# Riconosce i link simbolici dei file descriptor associati ai socket.
# Esempio:
# socket:[16931]
SOCKET_PATTERN = re.compile(r"^socket:\[(\d+)\]$")


def inspect_process_sockets(pid):
  """
  Trova tutti i socket aperti da un processo.

  Relazione:
    PID -> FD -> inode
  """

  sockets = []

  # Directory contenente i file descriptor del processo.
  fd_path = f"/proc/{pid}/fd"

  try:
    file_descriptors = os.listdir(fd_path)
  except (
    FileNotFoundError,
    PermissionError,
    ProcessLookupError,
  ):
    return sockets

  # Analizza ogni file descriptor.
  for fd in file_descriptors:
    link_path = f"{fd_path}/{fd}"

    try:
      # Legge a cosa punta il file descriptor.
      target = os.readlink(link_path)
    except (
      FileNotFoundError,
      PermissionError,
      ProcessLookupError,
      OSError,
    ):
      continue

    # Verifica se il file descriptor punta a un socket.
    match = SOCKET_PATTERN.match(target)

    if not match:
      continue

    # Estrae l'inode dal valore socket:[inode].
    inode = int(match.group(1))

    # Registra la relazione processo -> FD -> inode.
    sockets.append(
      {
        "pid": int(pid),
        "fd": int(fd),
        "inode": inode,
      }
    )

  return sockets


def inspect_socket_inode(inode):
  """
  Cerca quale processo possiede un determinato socket inode.

  Relazione:
    inode -> PID -> FD
  """

  matches = []

  # /proc contiene una directory per ogni processo.
  proc_path = "/proc"

  for pid in os.listdir(proc_path):

    # Ignora le directory che non rappresentano PID.
    if not pid.isdigit():
      continue

    # Directory dei file descriptor del processo.
    fd_path = f"{proc_path}/{pid}/fd"

    try:
      file_descriptors = os.listdir(fd_path)
    except (
      FileNotFoundError,
      PermissionError,
      ProcessLookupError,
    ):
      continue

    # Analizza i file descriptor del processo.
    for fd in file_descriptors:
      link_path = f"{fd_path}/{fd}"

      try:
        # Legge il target del file descriptor.
        target = os.readlink(link_path)
      except (
        FileNotFoundError,
        PermissionError,
        ProcessLookupError,
        OSError,
      ):
        continue

      # Cerca il socket con l'inode richiesto.
      if target != f"socket:[{inode}]":
        continue

      # Abbiamo trovato il processo e il FD
      # proprietari del socket.
      matches.append(
        {
          "pid": int(pid),
          "fd": int(fd),
          "inode": int(inode),
        }
      )

  return matches