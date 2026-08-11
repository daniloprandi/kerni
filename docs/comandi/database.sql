TRUNCATE TABLE cmdb.nodes RESTART IDENTITY CASCADE;

TRUNCATE TABLE tcpip.transport_connections RESTART IDENTITY CASCADE;

--

SELECT * FROM cmdb.nodes
ORDER BY id ASC 

SELECT * FROM tcpip.transport_connections
ORDER BY id ASC 
