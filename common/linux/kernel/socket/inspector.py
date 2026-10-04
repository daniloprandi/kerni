import re

from common.linux.remote import ssh


SOCKET_PATTERN = re.compile(
  r"^socket:\[(\d+)\]$"
)


def inspect_sockets(host):

  ssh_host = f"dprandi@{host}"

  # Inode -> PID/FD
  socket_map = {}

  # ---------------------------------------------------------
  # 1. Cerca i socket attraverso /proc/[pid]/fd/*
  # ---------------------------------------------------------

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

  for line in output.splitlines():

    fields = line.split()

    if len(fields) != 3:
      continue

    pid, fd, inode = fields

    if not SOCKET_PATTERN.match(f"socket:[{inode}]"):
      continue

    socket_map[int(inode)] = {
      "pid": int(pid),
      "fd": int(fd),
    }

  # ---------------------------------------------------------
  # 2. Cerca anche gli inode direttamente in /proc/net/*
  # ---------------------------------------------------------

  net_output = ssh.execute(
    ssh_host,
    r"""
    for file in \
      /proc/net/tcp \
      /proc/net/tcp6 \
      /proc/net/udp \
      /proc/net/udp6 \
      /proc/net/raw \
      /proc/net/raw6
    do
      if [ -r "$file" ]; then
        awk 'NR > 1 {print $10}' "$file"
      fi
    done

    if [ -r /proc/net/unix ]; then
      awk 'NR > 1 {print $7}' /proc/net/unix
    fi
    """
  )

  # Aggiunge gli inode che non erano visibili
  # attraverso /proc/[pid]/fd/*.
  for line in net_output.splitlines():

    line = line.strip()

    if not line.isdigit():
      continue

    inode = int(line)

    if inode <= 0:
      continue

    if inode not in socket_map:
      socket_map[inode] = {
        "pid": None,
        "fd": None,
      }

  # ---------------------------------------------------------
  # 3. Costruisce il risultato finale
  # ---------------------------------------------------------

  sockets = []

  for inode, data in socket_map.items():

    sockets.append(
      {
        "pid": data["pid"],
        "fd": data["fd"],
        "inode": inode,
      }
    )

  return sockets


def inspect_socket_inode(host, inode):

  ssh_host = f"dprandi@{host}"

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
        "inode": int(socket_inode),
      }
    )

  return matches