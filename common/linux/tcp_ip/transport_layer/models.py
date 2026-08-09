# Transport Layer Models.

from dataclasses import dataclass


# Transport Layer connection.
@dataclass
class Connection:

  node_id: int

  proto: str

  src_ip: str | None
  src_port: int | None

  dst_ip: str | None
  dst_port: int | None

  state: str

  uid: int

  username: str | None

  inode: int

  type: str | None = None

  flags: str | None = None

  path: str | None = None