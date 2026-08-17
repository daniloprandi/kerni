================================================================================
================================================================================

                                TEST KERNI
                         RIAVVIO E DISCOVERY AUTOMATICA

================================================================================
================================================================================


###############################################################################
# 1. KERNI-NODE
###############################################################################

-- avvio la VM kerni-node

-- apro VS Code e mi collego in SSH a kerni-node

cd /var/www/kerni

-- verifico il repository

git pull

-- attivo il virtual environment

source .venv/bin/activate


###############################################################################
# 2. VERIFICA RETE DI KERNI
###############################################################################

-- verifico l'indirizzo IP di Kerni

ip addr show ens33

-- verifico il gateway

ip route

-- verifico che Kerni raggiunga data-node

ping -c 3 192.168.200.131

-- si popolano le tabella nodes e ping

###############################################################################
# 3. VERIFICA SSH VERSO DATA-NODE
###############################################################################

-- verifico che Kerni possa raggiungere data-node via SSH

ssh data-node hostname

-- verifico anche utilizzando direttamente l'IP

ssh 192.168.200.131 hostname

-- risultato atteso:

data-node


###############################################################################
# 4. VERIFICA SERVIZIO KERNI
###############################################################################

-- verifico che il servizio sia attivo

sudo systemctl status kerni.service --no-pager

-- risultato atteso:

Active: active (running)

-- se non è attivo:

sudo systemctl restart kerni.service

-- ricontrollo:

sudo systemctl status kerni.service --no-pager


###############################################################################
# 5. VERIFICA LOG DI KERNI
###############################################################################

-- apro il log in tempo reale

sudo journalctl -u kerni.service -f

-- NON eseguo nessun comando di discovery manualmente.


###############################################################################
# 6. DATA-NODE
###############################################################################

-- avvio la VM data-node

-- apro VS Code e mi collego in SSH a data-node

-- verifico il suo IP

ip addr show

-- verifico il suo hostname

hostname


###############################################################################
# 7. DATA-NODE SI PRESENTA A KERNI
###############################################################################

-- da data-node eseguo SOLO questo:

ping -c 3 192.168.200.130


###############################################################################
# 8. VERIFICA SU KERNI
###############################################################################

-- torno al terminale di kerni-node

-- nel journal devo vedere:

PING: 192.168.200.131 -> 192.168.200.130


-- e successivamente la discovery:

{
  "hostname": "data-node",
  "ip_addr": "192.168.200.131",
  "os_name": "Linux",
  "os_v": "...",
  "kernel_v": "...",
  "status": "registered"
}


###############################################################################
# 9. VERIFICA TCP/IP PING
###############################################################################

-- nel database eseguo:

SELECT
  id,
  src_ip,
  dest_ip,
  last_seen
FROM tcpip.ping
ORDER BY id;


-- deve comparire:

192.168.200.131 -> 192.168.200.130


###############################################################################
# 10. VERIFICA CMDB
###############################################################################

-- nel database eseguo:

SELECT
  id,
  hostname,
  ip_addr,
  os_name,
  os_v,
  kernel_v,
  status,
  last_seen
FROM cmdb.nodes
ORDER BY id;


-- deve comparire:

data-node
192.168.200.131
Linux
6.8.0-136-generic


###############################################################################
# 11. TEST DEL SECONDO PING
###############################################################################

-- da data-node eseguo nuovamente:

ping -c 3 192.168.200.130


-- Kerni deve rispondere:

"status": "already_registered"


-- NON deve creare un secondo nodo data-node.


###############################################################################
# 12. VERIFICA LAST_SEEN
###############################################################################

-- nel database:

SELECT
  id,
  hostname,
  ip_addr,
  last_seen
FROM cmdb.nodes
WHERE ip_addr = '192.168.200.131';


-- eseguo nuovamente il ping da data-node:

ping -c 3 192.168.200.130


-- rieseguo la query e verifico che last_seen sia aggiornato.


###############################################################################
# 13. TEST DEL PING DAL GATEWAY / ALTRO HOST
###############################################################################

-- se Kerni riceve un ping da un altro dispositivo, ad esempio:

192.168.200.1 -> 192.168.200.130

-- verifico il comportamento nel journal:

sudo journalctl -u kerni.service -n 50 --no-pager


-- IMPORTANTE:
-- un host che pinga Kerni ma non è un nodo Linux configurato per la
-- discovery può generare un errore SSH.
--
-- Questo caso NON deve far morire il listener ICMP.


###############################################################################
# RISULTATO FINALE
###############################################################################

Il test è SUPERATO se:

1. kerni.service è ACTIVE (running)

2. Kerni raggiunge data-node via SSH

3. data-node raggiunge Kerni via ping

4. Kerni vede:

   PING: 192.168.200.131 -> 192.168.200.130

5. tcpip.ping contiene il ping

6. la discovery raccoglie:

   hostname
   IP
   OS
   kernel

7. cmdb.nodes contiene data-node

8. un secondo ping produce:

   already_registered

9. last_seen viene aggiornato

10. un ping proveniente da un host non scopribile
    NON deve terminare il thread listen_for_ping()


================================================================================
================================================================================

                              FINE TEST KERNI

================================================================================
================================================================================