from common.database import get_connection


def insert_all(processes, node_id):
  # Non fa nulla se non ci sono processi.
  if not processes:
    return

  # Apre una connessione al database.
  con = get_connection()

  try:
    with con.cursor() as cursor:
      for process in processes:
        cursor.execute(
          """
          INSERT INTO kernel.processes
          (
            node_id,
            pid,
            ppid,
            uid,
            username,
            cpu_ticks,
            cpu_percent,
            mem_percent,
            vsz,
            rss,
            tty,
            state,
            start,
            time,
            cmdline,
            detected_at
          )
          VALUES
          (
            %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s,
            CURRENT_TIMESTAMP
          )
          ON CONFLICT (node_id, pid)
          DO UPDATE SET
            ppid = EXCLUDED.ppid,
            uid = EXCLUDED.uid,
            username = EXCLUDED.username,
            cpu_ticks = EXCLUDED.cpu_ticks,
            cpu_percent = EXCLUDED.cpu_percent,
            mem_percent = EXCLUDED.mem_percent,
            vsz = EXCLUDED.vsz,
            rss = EXCLUDED.rss,
            tty = EXCLUDED.tty,
            state = EXCLUDED.state,
            start = EXCLUDED.start,
            time = EXCLUDED.time,
            cmdline = EXCLUDED.cmdline,
            detected_at = CURRENT_TIMESTAMP
          """,
          (
            node_id,
            process["pid"],
            process.get("ppid"),
            process.get("uid"),
            process.get("user"),
            process.get("cpu_ticks"),
            process.get("cpu_percent"),
            process.get("mem_percent"),
            process.get("vsz"),
            process.get("rss"),
            process.get("tty"),
            process.get("stat"),
            process.get("start"),
            process.get("time"),
            process.get("command")
          )
        )

    # Conferma le modifiche.
    con.commit()

  finally:
    # Chiude la connessione.
    con.close()