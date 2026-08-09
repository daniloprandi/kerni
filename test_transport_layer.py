import json

from common.linux.tcp_ip.transport_layer.inspector import run


def main():

  # Run the Transport Layer inspection.
  result = run()

  # Print the inspection result.
  print(json.dumps(result, indent=2))


if __name__ == "__main__":
  main()