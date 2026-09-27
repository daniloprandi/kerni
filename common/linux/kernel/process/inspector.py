import os
import time
from datetime import datetime


CLK_TCK = os.sysconf(os.sysconf_names["SC_CLK_TCK"])
PAGE_SIZE = os.sysconf("SC_PAGE_SIZE")


def _read_file(path):
  try:
    with open(path, "r") as file:
      return file.read()
  except (FileNotFoundError, PermissionError, ProcessLookupError):
    return None


def _get_process_info(pid):
  process_path = f"/proc/{pid}"

  status = _read_file(f"{process_path}/status")
  stat = _read_file(f"{process_path}/stat")
  cmdline = _read_file(f"{process_path}/cmdline")

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

  uid = status_data.get("Uid", "").split()

  if not uid:
    return None

  uid = uid[0]

  username = _get_username(uid)

  command = cmdline.replace("\x00", " ").strip()

  if not command:
    command = status_data.get("Name", pid)

  start_timestamp = _get_start_timestamp(start_time)

  return {
    "user": username,
    "pid": int(pid),
    "ppid": ppid,
    "cpu_ticks": utime + stime,
    "cpu_percent": 0.0,
    "mem_percent": _get_memory_percent(rss_pages),
    "vsz": vsize // 1024,
    "rss": (rss_pages * PAGE_SIZE) // 1024,
    "tty": _get_tty(process_path),
    "stat": state,
    "start": start_timestamp,
    "time": _format_cpu_time(utime + stime),
    "command": command
  }


def _get_username(uid):
  try:
    with open("/etc/passwd", "r") as file:
      for line in file:
        fields = line.rstrip("\n").split(":")

        if len(fields) >= 3 and fields[2] == uid:
          return fields[0]
  except (FileNotFoundError, PermissionError):
    pass

  return uid


def _get_memory_percent(rss_pages):
  meminfo = _read_file("/proc/meminfo")

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


def _get_tty(process_path):
  try:
    tty_path = os.readlink(f"{process_path}/fd/0")

    if tty_path.startswith("/dev/pts/"):
      return tty_path.replace("/dev/pts/", "pts/")

    if tty_path.startswith("/dev/tty"):
      return tty_path.replace("/dev/", "")

    return "?"

  except (FileNotFoundError, PermissionError, ProcessLookupError, OSError):
    return "?"


def _get_start_timestamp(start_time):
  uptime_data = _read_file("/proc/uptime")

  if uptime_data is None:
    return "?"

  uptime = float(uptime_data.split()[0])

  boot_time = time.time() - uptime
  process_start = boot_time + (start_time / CLK_TCK)

  return datetime.fromtimestamp(process_start).strftime("%H:%M")


def _format_cpu_time(cpu_ticks):
  total_seconds = cpu_ticks / CLK_TCK

  hours = int(total_seconds // 3600)
  minutes = int((total_seconds % 3600) // 60)
  seconds = int(total_seconds % 60)

  return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def inspect_processes(previous_processes=None, interval=1):
  processes = []

  for pid in os.listdir("/proc"):
    if not pid.isdigit():
      continue

    process = _get_process_info(pid)

    if process is not None:
      processes.append(process)

  if previous_processes is not None:
    previous_by_pid = {
      process["pid"]: process
      for process in previous_processes
    }

    for process in processes:
      previous = previous_by_pid.get(process["pid"])

      if previous is None:
        continue

      current_ticks = process["cpu_ticks"]
      previous_ticks = previous["cpu_ticks"]

      delta_ticks = current_ticks - previous_ticks

      process["cpu_percent"] = (
        delta_ticks / CLK_TCK
      ) / interval * 100

  processes.sort(
    key=lambda process: process["cpu_percent"],
    reverse=True
  )

  return processes