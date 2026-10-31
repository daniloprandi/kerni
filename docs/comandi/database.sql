
psql -h 192.168.200.131 -U kerni -d kernidata
pw kerni 

SELECT 
    n.id,
    n.hostname,
    
    -- Layer 2: Network Interfaces & Stats
    ni.interface AS net_interface,
    ni.ip_address AS net_ip,
    ni.mac_address AS net_mac,
    ist.rx_bytes,
    ist.tx_bytes,
    ist.rx_errors,
    ist.tx_errors,
    
    -- Layer 2/3: ARP Table
    arp.ip_address AS arp_target_ip,
    arp.mac_address AS arp_target_mac,
    
    -- Layer 3: Routing Table
    rt.destination AS route_destination,
    rt.gateway AS route_gateway,
    rt.netmask AS route_netmask,
    
    -- Layer 4: Transport Connections
    tc.proto AS transport_proto,
    tc.src_ip AS conn_src_ip,
    tc.src_port AS conn_src_port,
    tc.dst_ip AS conn_dst_ip,
    tc.dst_port AS conn_dst_port,
    tc.state AS conn_state,
    
    -- Kernel Layer: Processes
    p.pid AS process_pid,
    p.name AS process_name,
    
    -- Application Layer: Systemd Services
    s.unit AS systemd_service,
    s.active_state AS systemd_state

FROM cmdb.nodes n
LEFT JOIN tcpip.network_interfaces ni ON n.id = ni.node_id
LEFT JOIN tcpip.interface_stats ist ON ni.node_id = ist.node_id AND ni.interface = ist.interface
LEFT JOIN tcpip.arp_table arp ON n.id = arp.node_id
LEFT JOIN tcpip.routing_table rt ON n.id = rt.node_id
LEFT JOIN tcpip.transport_connections tc ON n.id = tc.node_id
LEFT JOIN kernel.processes p ON n.id = p.node_id
LEFT JOIN application.systemd_services s ON n.id = s.node_id

ORDER BY n.id

limit 100;

--------------------------------------------------------------------------------
-- 1. RESET AMBIENTE DI TEST (TRUNCATE)
--------------------------------------------------------------------------------
-- Pulisce tutte le tabelle rispettando i vincoli di chiave esterna
TRUNCATE TABLE application.systemd_services RESTART IDENTITY CASCADE;
TRUNCATE TABLE tcpip.transport_connections RESTART IDENTITY CASCADE;
TRUNCATE TABLE tcpip.ping RESTART IDENTITY CASCADE;
TRUNCATE TABLE tcpip.network_interfaces RESTART IDENTITY CASCADE;
TRUNCATE TABLE kernel.sockets RESTART IDENTITY CASCADE;
TRUNCATE TABLE kernel.processes RESTART IDENTITY CASCADE;
TRUNCATE TABLE tcpip.arp_table RESTART IDENTITY CASCADE;
TRUNCATE TABLE cmdb.nodes RESTART IDENTITY CASCADE;


--------------------------------------------------------------------------------
-- 2. ISPEZIONI DI BASE ORDINATE SECONDO LO STACK
--------------------------------------------------------------------------------

-- [0] INVENTARIO / CMDB (Anagrafica Nodo)
SELECT id, hostname, ip_addr, last_seen
FROM cmdb.nodes
ORDER BY id ASC;

-- [1] LINK LAYER / DATA LINK LAYER (Livello 2 - Interfacce e MAC)
SELECT * 
FROM tcpip.network_interfaces;

-- [2] INTERNET / NETWORK LAYER (Livello 3 - ARP e ICMP/Ping)
SELECT * 
FROM tcpip.arp_table;

SELECT * 
FROM tcpip.ping
ORDER BY id ASC;
-- Filtri opzionali per IP sorgente:
-- WHERE src_ip::text LIKE '%.128%' -- s1
-- WHERE src_ip::text LIKE '%.131%' -- data node
-- WHERE src_ip::text LIKE '%.133%' -- void-node

-- [3] TRANSPORT LAYER (Livello 4 - Connessioni TCP/UDP e Socket di Kernel)
SELECT * 
FROM tcpip.transport_connections
-- Filtri opzionali per IP sorgente:
-- WHERE src_ip::text LIKE '%.200.1%' -- s1
-- WHERE src_ip::text LIKE '%.131%' -- data node 
-- WHERE src_ip::text LIKE '%.133%' -- void-node
-- WHERE src_ip::text LIKE '%.135%' -- test-automation-node
-- WHERE username = 'testuser'
;

SELECT * 
FROM kernel.sockets;

-- [4] KERNEL PROCESSES & [5] APPLICATION LAYER (Processi e Servizi Systemd)
SELECT * 
FROM kernel.processes;

SELECT * 
FROM application.systemd_services;


--------------------------------------------------------------------------------
-- 3. STATISTICHE E RIEPILOGHI (COUNTS ORDINATI)
--------------------------------------------------------------------------------

-- Conteggio complessivo dei record organizzato per layer
SELECT '0. cmdb.nodes' AS layer_tabelle, COUNT(*) FROM cmdb.nodes
UNION ALL
SELECT '1. tcpip.network_interfaces (Link)', COUNT(*) FROM tcpip.network_interfaces
UNION ALL
SELECT '2. tcpip.arp_table (Internet)', COUNT(*) FROM tcpip.arp_table
UNION ALL
SELECT '2. tcpip.ping (Internet)', COUNT(*) FROM tcpip.ping
UNION ALL
SELECT '3. tcpip.transport_connections (Transport)', COUNT(*) FROM tcpip.transport_connections
UNION ALL
SELECT '3. kernel.sockets (Transport)', COUNT(*) FROM kernel.sockets
UNION ALL
SELECT '4. kernel.processes (Process)', COUNT(*) FROM kernel.processes
UNION ALL
SELECT '5. application.systemd_services (Application)', COUNT(*) FROM application.systemd_services;

-- Distribuzione delle connessioni di trasporto raggruppate per IP sorgente
SELECT src_ip, COUNT(*) AS count
FROM tcpip.transport_connections
GROUP BY src_ip
ORDER BY src_ip;

-- Conteggio delle connessioni per protocollo su uno specifico nodo (es. node_id = 10001)
SELECT proto, COUNT(*)
FROM tcpip.transport_connections
WHERE node_id = 10001
GROUP BY proto
ORDER BY proto;


--------------------------------------------------------------------------------
-- 4. QUERY AVANZATE E SNAPSHOT TEMPORALI
--------------------------------------------------------------------------------

-- Estrae l'ultimo snapshot temporale disponibile per le connessioni di trasporto del nodo 10001
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