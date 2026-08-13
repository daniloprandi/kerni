import subprocess
import re


command = [
    "tcpdump",
    "-i", "any",
    "-n",
    "-l",
    "icmp",
]

process = subprocess.Popen(
    command,
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    text=True
)

for line in process.stdout:
    match = re.search(
        r"IP (\d+\.\d+\.\d+\.\d+) > (\d+\.\d+\.\d+\.\d+): ICMP",
        line
    )

    if match:
        src_ip = match.group(1)
        dest_ip = match.group(2)

        print(f"PING: {src_ip} -> {dest_ip}", flush=True)