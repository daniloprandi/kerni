from common.database import get_connection


def get_by_hostname(hostname):

  con = get_connection()
  cur = con.cursor()

  cur.execute(
    """
    SELECT id
    FROM cmdb.nodes
    WHERE hostname = %s
    """,
    (hostname,)
  )

  node = cur.fetchone()

  cur.close()
  con.close()

  return node


def insert(node):

  con = get_connection()
  cur = con.cursor()

  cur.execute(
    """
    INSERT INTO cmdb.nodes
    (
      hostname,
      ip_addr,
      os_name,
      os_v,
      kernel_v,
      status,
      registered_at,
      last_seen,
      domain_id
    )
    VALUES
    (
      %s,
      %s,
      %s,
      %s,
      %s,
      'ONLINE',
      NOW(),
      NOW(),
      1
    )
    """,
    (
      node["hostname"],
      node["ip_addr"],
      node["os_name"],
      node["os_v"],
      node["kernel_v"]
    )
  )

  con.commit()

  cur.close()
  con.close()


def update(node):

  con = get_connection()
  cur = con.cursor()

  cur.execute(
    """
    UPDATE cmdb.nodes
    SET
      ip_addr = %s,
      os_name = %s,
      os_v = %s,
      kernel_v = %s,
      status = 'ONLINE',
      last_seen = NOW()
    WHERE hostname = %s
    """,
    (
      node["ip_addr"],
      node["os_name"],
      node["os_v"],
      node["kernel_v"],
      node["hostname"]
    )
  )

  con.commit()

  cur.close()
  con.close()