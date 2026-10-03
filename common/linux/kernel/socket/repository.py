from common.database import get_connection


def insert_all(sockets, node_id):
  # Non fa nulla se non ci sono socket.
  if not sockets:
    return

  # Apre una connessione al database.
  con = get_connection()

  try:
    with con.cursor() as cursor:
      for socket in sockets:
        cursor.execute(
          """
          INSERT INTO kernel.sockets
          (
            node_id,
            inode,
            pid,
            fd,
            type,
            flags,
            path,
            detected_at
          )
          VALUES
          (
            %s, %s, %s, %s, %s, %s, %s,
            CURRENT_TIMESTAMP
          )
          ON CONFLICT (node_id, inode)
          DO UPDATE SET
            pid = EXCLUDED.pid,
            fd = EXCLUDED.fd,
            detected_at = CURRENT_TIMESTAMP
          """,
          (
            node_id,
            socket["inode"],
            socket["pid"],
            socket["fd"],
            socket.get("type"),
            socket.get("flags"),
            socket.get("path")
          )
        )

    con.commit()

  finally:
    con.close()