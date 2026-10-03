import base64
import json
import os

from common.linux.remote import ssh


REMOTE_PROCESS_INSPECTOR = r'''
import os
import json
import time
from datetime import datetime


CLK_TCK = os.sysconf(os.sysconf_names["SC_CLK_TCK"])
PAGE_SIZE = os.sysconf("SC_PAGE_SIZE")


def read_file(path):
  try:
    with open(path, "r") as file:
      return file.read()
  except (FileNotFoundError, PermissionError, ProcessLookupError):
    return None


def get_username(uid):
  try:
    with open("/etc/passwd", "r") as file:
      for line in file:
        fields = line.rstrip("\n").split(":")

        if len(fields) >= 3 and fields[2] == str(uid):
          return fields[0]

  except (FileNotFoundError, PermissionError):
    pass

  return str(uid)


def get_memory_percent(rss_pages):
  meminfo = read_file("/proc/meminfo")

  if meminfo is None:
    return 0.0

  total_memory = 0

  for line in meminfo.splitlines():
    if line.startswith("MemTotal:"):
      total_memory = int(line.split()[1]) * 1024
      break

  if total_memory == 0:
    return 0.0

  rss_bytes = rss_pages * PAGE_SIZE

  return (rss_bytes / total_memory) * 100


def get_tty(process_path):
  try:
    tty_path = os.readlink(f"{process_path}/fd/0")

    if tty_path.startswith("/dev/pts/"):
      return tty_path.replace("/dev/pts/", "pts/")

    if tty_path.startswith("/dev/tty"):
      return tty_path.replace("/dev/", "")

    return "?"

  except (
    FileNotFoundError,
    PermissionError,
    ProcessLookupError,
    OSError
  ):
    return "?"


def get_start_timestamp(start_time):
  uptime_data = read_file("/proc/uptime")

  if uptime_data is None:
    return "?"

  uptime = float(uptime_data.split()[0])
  boot_time = time.time() - uptime
  process_start = boot_time + (start_time / CLK_TCK)

  return datetime.fromtimestamp(process_start).strftime("%H:%M")


def format_cpu_time(cpu_ticks):
  total_seconds = cpu_ticks / CLK_TCK

  hours = int(total_seconds // 3600)
  minutes = int((total_seconds % 3600) // 60)
  seconds = int(total_seconds % 60)

  return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def get_process_info(pid):
  process_path = f"/proc/{pid}"

  status = read_file(f"{process_path}/status")
  stat = read_file(f"{process_path}/stat")
  cmdline = read_file(f"{process_path}/cmdline")

  if status is None or stat is None:
    return None

  status_data = {}

  for line in status.splitlines():
    key, separator, value = line.partition(":")

    if separator:
      status_data[key] = value.strip()

  stat_end = stat.rfind(")")

  if stat_end == -1:
    return None

  stat_data = stat[stat_end + 2:].split()

  if len(stat_data) < 22:
    return None

  state = stat_data[0]
  ppid = int(stat_data[1])
  utime = int(stat_data[11])
  stime = int(stat_data[12])
  start_time = int(stat_data[19])
  vsize = int(stat_data[20])
  rss_pages = int(stat_data[21])

  uid_fields = status_data.get("Uid", "").split()

  if not uid_fields:
    return None

  uid = int(uid_fields[0])
  username = get_username(uid)

  command = ""

  if cmdline is not None:
    command = cmdline.replace("\x00", " ").strip()

  if not command:
    command = status_data.get("Name", str(pid))

  start_timestamp = get_start_timestamp(start_time)
  cpu_ticks = utime + stime

  return {
    "user": username,
    "uid": uid,
    "pid": int(pid),
    "ppid": ppid,
    "name": status_data.get("Name"),
    "cpu_ticks": cpu_ticks,
    "cpu_percent": 0.0,
    "mem_percent": get_memory_percent(rss_pages),
    "vsz": vsize // 1024,
    "rss": (rss_pages * PAGE_SIZE) // 1024,
    "tty": get_tty(process_path),
    "stat": state,
    "start": start_timestamp,
    "time": format_cpu_time(cpu_ticks),
    "command": command
  }


def inspect_processes():
  processes = []

  for pid in os.listdir("/proc"):
    if not pid.isdigit():
      continue

    process = get_process_info(pid)

    if process is not None:
      processes.append(process)

  processes.sort(key=lambda process: process["pid"])

  print(json.dumps(processes))


inspect_processes()
'''


def inspect_processes(host):
  # Costruisce l'host SSH remoto.
  ssh_host = f"dprandi@{host}"

  # Codifica lo script remoto.
  encoded_script = base64.b64encode(
    REMOTE_PROCESS_INSPECTOR.encode()
  ).decode()

  # Esegue lo script sul nodo remoto.
  output = ssh.execute(
    ssh_host,
    f"echo {encoded_script} | base64 -d | python3"
  )

  # Converte il risultato JSON in una lista Python.
  processes = json.loads(output)

  # Ordina i processi per PID.
  processes.sort(
    key=lambda process: process["pid"]
  )

  return processes