import subprocess


def get():
  output = subprocess.check_output(
    ["hostname", "-I"],
    text=True
  ).strip()

  return output.split()[0]