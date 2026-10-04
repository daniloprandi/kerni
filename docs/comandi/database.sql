
psql -h 192.168.200.131 -U kerni -d kernidata
pw kerni 

--


TRUNCATE TABLE cmdb.nodes RESTART IDENTITY CASCADE;
TRUNCATE TABLE tcpip.transport_connections RESTART IDENTITY CASCADE;
TRUNCATE TABLE tcpip.ping RESTART IDENTITY CASCADE;

--

SELECT * FROM cmdb.nodes
ORDER BY id ASC 

SELECT * FROM tcpip.ping
ORDER BY id ASC 
WHERE src_ip::text like '%.128%' -- s1
--WHERE src_ip::text like '%.131%' -- data node
--WHERE src_ip::text like '%.133%' -- void-node

SELECT * FROM tcpip.transport_connections
--WHERE src_ip::text like '%.128%' -- s1
--WHERE src_ip::text like '%.131%' -- data node
WHERE src_ip::text like '%.133%' -- void-node
--ORDER BY

--

===============================================================================
CONTEGGIO RECORD
===============================================================================

SELECT 'cmdb.nodes' AS tabella, COUNT(*) FROM cmdb.nodes
UNION ALL
SELECT 'tcpip.ping', COUNT(*) FROM tcpip.ping
UNION ALL
SELECT 'kernel.processes', COUNT(*) FROM kernel.processes
UNION ALL
SELECT 'kernel.sockets', COUNT(*) FROM kernel.sockets
UNION ALL
SELECT 'tcpip.transport_connections', COUNT(*) FROM tcpip.transport_connections;

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

SELECT MIN(id), MAX(id)
FROM tcpip.transport_connections;