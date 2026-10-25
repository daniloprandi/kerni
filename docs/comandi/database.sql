
psql -h 192.168.200.131 -U kerni -d kernidata
pw kerni 

--

TRUNCATE TABLE cmdb.nodes RESTART IDENTITY CASCADE;
TRUNCATE TABLE tcpip.transport_connections RESTART IDENTITY CASCADE;
TRUNCATE TABLE tcpip.ping RESTART IDENTITY CASCADE;
TRUNCATE TABLE tcpip.network_interfaces RESTART IDENTITY CASCADE;
TRUNCATE TABLE kernel.sockets RESTART IDENTITY CASCADE;
TRUNCATE TABLE kernel.processes RESTART IDENTITY CASCADE;


SELECT id, hostname, ip_addr
FROM cmdb.nodes
ORDER BY id;

--

SELECT * FROM cmdb.nodes
ORDER BY id ASC 

--

SELECT * FROM tcpip.ping
ORDER BY id ASC 
--WHERE src_ip::text like '%.128%' -- s1
--WHERE src_ip::text like '%.131%' -- data node
--WHERE src_ip::text like '%.133%' -- void-node

--

SELECT * FROM tcpip.transport_connections
WHERE src_ip::text like '%.200.1%' -- s1
--WHERE src_ip::text like '%.131%' -- data node 
--WHERE src_ip::text like '%.133%' -- void-node
--WHERE src_ip::text like '%.135%' -- test-automation-node
--where username = 'testuser'
--ORDER BY

--

SELECT * FROM tcpip.network_interfaces

SELECT * FROM kernel.sockets

--

SELECT * FROM kernel.processes

--

SELECT 'cmdb.nodes' AS tabella, COUNT(*) FROM cmdb.nodes
UNION ALL
SELECT 'tcpip.ping', COUNT(*) FROM tcpip.ping
UNION ALL
SELECT 'kernel.processes', COUNT(*) FROM kernel.processes
UNION ALL
SELECT 'kernel.sockets', COUNT(*) FROM kernel.sockets
UNION ALL
SELECT 'tcpip.transport_connections', COUNT(*) FROM tcpip.transport_connections
UNION ALL
SELECT 'tcpip.transport_connections', COUNT(*) FROM tcpip.network_interfaces;


SELECT src_ip, COUNT(*) AS count
FROM tcpip.transport_connections
GROUP BY src_ip
ORDER BY src_ip;

--

SELECT proto, COUNT(*)
FROM tcpip.transport_connections
WHERE node_id = 10001
GROUP BY proto
ORDER BY proto;

--

SELECT
  proto,
  src_ip,
  src_port,
  dst_ip,
  dst_port,
  state,
  inode,
  detected_at
FROM tcpip.transport_connections
WHERE node_id = 10001
  AND detected_at = (
    SELECT MAX(detected_at)
    FROM tcpip.transport_connections
    WHERE node_id = 10001
  )
ORDER BY proto, inode;