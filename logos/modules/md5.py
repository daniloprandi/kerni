import hashlib


def onion_to_md5(onion_address):
  return hashlib.md5(
    onion_address.encode("utf-8")
  ).hexdigest()

