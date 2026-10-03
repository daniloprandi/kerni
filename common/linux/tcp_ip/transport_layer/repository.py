from common.database import get_connection


def insert_all(connections):
  # Non fa nulla se non ci sono connessioni.
  if not connections:
    return

  con = get_connection()

  try:
    with con.cursor() as cursor:
      for connection in connections:
        cursor.execute(
          """
          INSERT INTO tcpip.transport_connections
          (
            node_id,
            proto,
            src_ip,
            src_port,
            dst_ip,
            dst_port,
            state,
            uid,
            username,
            inode
          )
          VALUES
          (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
          )
          """,
          (
            connection["node_id"],
            connection["proto"],
            connection.get("src_ip"),
            connection.get("src_port"),
            connection.get("dst_ip"),
            connection.get("dst_port"),
            connection["state"],
            connection["uid"],
            connection["username"],
            connection["inode"]
          )
        )

    con.commit()

  finally:
    con.close()