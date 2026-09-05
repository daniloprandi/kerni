TRUNCATE TABLE cmdb.nodes RESTART IDENTITY CASCADE;

TRUNCATE TABLE tcpip.transport_connections RESTART IDENTITY CASCADE;

TRUNCATE TABLE tcpip.ping RESTART IDENTITY CASCADE;

--

SELECT * FROM cmdb.nodes
ORDER BY id ASC 

SELECT * FROM tcpip.transport_connections
ORDER BY id ASC 

SELECT * FROM tcpip.ping
ORDER BY id ASC 

--

SELECT
  n.id,
  n.hostname,
  n.os_name,
  p.src_ip,
  p.dest_ip,
  p.last_seen
FROM tcpip.ping p
join cmdb.nodes n
on p.src_ip = n.ip_addr
ORDER BY n.id;