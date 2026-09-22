from modules.md5 import onion_to_md5


with open("data/onion_black_list.csv", "r") as file:
  onions = [line.strip() for line in file if line.strip()]

for o in onions:
  onion_hash = onion_to_md5(o)
  print(f"Onion: {o}")
  print(f"MD5:   {onion_hash}")
  print("-" * 50)