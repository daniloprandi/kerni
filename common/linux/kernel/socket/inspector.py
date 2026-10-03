import re

from common.linux.remote import ssh


SOCKET_PATTERN = re.compile(
  r"^socket:\[(\d+)\]$"
)


def inspect_sockets(host):
  # Costruisce l'host SSH remoto.
  ssh_host = f"dprandi@{host}"

  # Cerca tutti i socket aperti sul nodo remoto.
  output = ssh.execute(
    ssh_host,
    r"""
    for pid in /proc/[0-9]*; do
      for fd in "$pid"/fd/*; do
        target=$(readlink "$fd" 2>/dev/null)

        case "$target" in
          socket:\[*\])
            inode=$(echo "$target" | tr -cd '0-9')
            echo "${pid##*/} ${fd##*/} $inode"
            ;;
        esac
      done
    done
    """
  )

  sockets = []

  for line in output.splitlines():
    fields = line.split()

    if len(fields) != 3:
      continue

    pid, fd, inode = fields

    if not SOCKET_PATTERN.match(f"socket:[{inode}]"):
      continue

    sockets.append(
      {
        "pid": int(pid),
        "fd": int(fd),
        "inode": int(inode)
      }
    )

  return sockets


def inspect_socket_inode(host, inode):
  # Costruisce l'host SSH remoto.
  ssh_host = f"dprandi@{host}"

  # Cerca il processo e il file descriptor associati all'inode.
  output = ssh.execute(
    ssh_host,
    f"""
    for pid in /proc/[0-9]*; do
      for fd in "$pid"/fd/*; do
        target=$(readlink "$fd" 2>/dev/null)

        if [ "$target" = "socket:[{inode}]" ]; then
          echo "${{pid##*/}} ${{fd##*/}} {inode}"
        fi
      done
    done
    """
  )

  matches = []

  for line in output.splitlines():
    fields = line.split()

    if len(fields) != 3:
      continue

    pid, fd, socket_inode = fields

    matches.append(
      {
        "pid": int(pid),
        "fd": int(fd),
        "inode": int(socket_inode)
      }
    )

  return matches