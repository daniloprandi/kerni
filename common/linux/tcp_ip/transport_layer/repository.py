# Transport Layer Repository.

# Stores the Transport Layer connections into PostgreSQL.

from common.database import get_connection


# Store multiple Transport Layer connections.
def insert_all(connections):

  # Nothing to store.
  if not connections:
    return

  # Open the database connection.
  con = get_connection()

  # Create the database cursor.
  cursor = con.cursor()

  # Store every connection.
  for connection in connections:

    # Insert the Transport Layer connection.
    cursor.execute("""

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

        inode,

        type,

        flags,

        path
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

        %s,

        %s,

        %s,

        %s
      )

    """, (

      connection["node_id"],

      connection["proto"],

      connection.get("src_ip"),
      connection.get("src_port"),

      connection.get("dst_ip"),
      connection.get("dst_port"),

      connection["state"],

      connection["uid"],

      connection["username"],

      connection["inode"],

      connection.get("type"),

      connection.get("flags"),

      connection.get("path")

    ))

  # Commit the transaction.
  con.commit()

  # Close the cursor.
  cursor.close()

  # Close the database connection.
  con.close()