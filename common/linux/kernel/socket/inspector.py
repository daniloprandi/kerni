import os
import re

SOCKET_PATTERN = re.compile(r"socket:\[(\d+)\]")

def inspect_process_sockets(pid):
  sockets = []

  fd_path = f"/proc/{pid}/fd"

  try:
    file_descriptors = os.listdir(fd_path)
  except (FileNotFoundError, PermissionError, ProcessLookupError):
    return sockets

  for fd in file_descriptors:
    link_path = f"{fd_path}/{fd}"

    try:
      target = os.readlink(link_path)
    except (FileNotFoundError, PermissionError, ProcessLookupError, OSError):
      continue

    match = SOCKET_PATTERN.match(target)

    if not match:
      continue

    inode = int(match.group(1))

    sockets.append({
      "pid": int(pid),
      "fd": int(fd),
      "inode": inode
    })

  return sockets


def inspect_socket_inode(inode):
  matches = []

  for pid in os.listdir("/proc"):
    if not pid.isdigit():
      continue

    fd_path = f"/proc/{pid}/fd"

    try:
      file_descriptors = os.listdir(fd_path)
    except (FileNotFoundError, PermissionError, ProcessLookupError):
      continue

    for fd in file_descriptors:
      link_path = f"{fd_path}/{fd}"

      try:
        target = os.readlink(link_path)
      except (FileNotFoundError, PermissionError, ProcessLookupError, OSError):
        continue

      if target == f"socket:[{inode}]":
        matches.append({
          "pid": int(pid),
          "fd": int(fd),
          "inode": int(inode)
        })

  return matches