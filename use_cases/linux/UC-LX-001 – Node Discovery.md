UC-LX-001 – Node Discovery

1. Obiettivo

Scopo

Il caso d'uso UC-LX-001 – Node Discovery descrive il processo con cui Kerni identifica automaticamente un nodo Linux remoto quando osserva un pacchetto ICMP proveniente dal nodo e sincronizza le informazioni raccolte con la Configuration Management Data Base (CMDB).

La discovery viene attivata dall'osservazione del traffico ICMP in ingresso verso Kerni. L'indirizzo IP sorgente del pacchetto identifica inizialmente il nodo remoto.

La procedura acquisisce:

hostname;

indirizzo IP principale;

sistema operativo;

versione del sistema operativo;

versione del kernel.

Le informazioni vengono ottenute dal nodo remoto tramite SSH.

Al termine della discovery viene verificata la presenza del nodo nella CMDB ed eseguita un'operazione di INSERT oppure UPDATE.

Il risultato viene prodotto in formato JSON.

2. Scenario

Avvio della procedura

La Node Discovery viene attivata automaticamente quando Kerni osserva un pacchetto ICMP destinato a Kerni e proveniente da un indirizzo IP remoto.

Esempio:

data-node
192.168.200.131
        |
        | ICMP
        v
Kerni
192.168.200.130

Kerni osserva:

PING: 192.168.200.131 -> 192.168.200.130

Il flusso esegue automaticamente:

osservazione del pacchetto ICMP;

identificazione del source_ip;

registrazione dell'evento in tcpip.ping;

avvio della Node Discovery sul nodo remoto;

acquisizione delle informazioni di sistema tramite SSH;

costruzione del modello dati;

verifica della presenza nella CMDB;

INSERT oppure UPDATE del nodo;

produzione dell'output JSON.

Non sono richiesti ulteriori interventi dell'utente.

ICMP inbound e outbound

La discovery viene attivata dal traffico ICMP in ingresso verso Kerni:

Nodo remoto -> Kerni
       |
       +-- possibile trigger della discovery

Il traffico generato da Kerni verso un nodo remoto non rappresenta invece la presentazione del nodo a Kerni:

Kerni -> Nodo remoto
       |
       +-- non attiva la discovery

3. Architettura

Attori

Attore

Responsabilità

Nodo remoto

Genera traffico ICMP e fornisce informazioni di sistema tramite SSH

Kerni

Osserva ICMP, coordina la discovery e sincronizza la CMDB

ICMP listener

Riceve pacchetti ICMP e identifica il nodo sorgente

Node Discovery

Coordina la raccolta delle informazioni del nodo remoto

SSH

Esegue comandi sul nodo remoto

Linux remoto

Fornisce le informazioni di sistema

PostgreSQL

Gestisce CMDB ed eventi ICMP

Componenti

Modulo

Responsabilità

backend/node_discovery_api/app.py

Avvio del servizio API

backend/node_discovery_api/routes/listener.py

Ascolto ICMP e avvio della discovery

common/linux/node_discovery/discovery.py

Orchestrazione della discovery remota

common/linux/node_discovery/hostname.py

Recupero hostname remoto

common/linux/node_discovery/ip.py

Recupero IP remoto

common/linux/node_discovery/os.py

Recupero sistema operativo remoto

common/linux/node_discovery/kernel.py

Recupero kernel remoto

common/linux/node_discovery/repository.py

Accesso alla CMDB

common/linux/remote/ssh.py

Esecuzione dei comandi SSH

Ogni modulo implementa una singola responsabilità.

Architettura del caso d'uso

Nodo remoto
     |
     | ICMP
     v
   Kerni
     |
     v
ICMP listener
     |
     | source_ip
     v
Node Discovery
     |
     +-- hostname.get(host)
     +-- ip.get(host)
     +-- os.get_name(host)
     +-- os.get_version(host)
     +-- kernel.get(host)
             |
             | SSH
             v
       Nodo remoto
             |
             v
       repository.py
             |
             v
         PostgreSQL
             |
             v
         JSON finale

L'architettura è organizzata in quattro livelli:

Observation: osservazione dell'evento ICMP;

Discovery: raccolta delle informazioni del nodo remoto;

Persistence: sincronizzazione con la CMDB;

Presentation: produzione dell'output JSON.

listener.py rileva l'evento e fornisce l'indirizzo IP sorgente. discovery.py coordina la raccolta delle informazioni senza implementare direttamente l'accesso al sistema operativo remoto o al database.

4. Flusso di esecuzione

Punto di ingresso

Il servizio viene avviato da systemd:

kerni.service
    |
    v
backend/node_discovery_api/app.py

L'applicazione avvia il listener ICMP, che rimane in ascolto dei pacchetti.

Ricezione del pacchetto

Quando Kerni riceve un pacchetto ICMP:

ICMP packet
    |
    v
listener
    |
    +-- source_ip
    +-- destination_ip

Esempio:

source_ip      = 192.168.200.131
destination_ip = 192.168.200.130

Il listener registra l'evento e utilizza source_ip per avviare la discovery.

Ruolo di discovery.py

La funzione run(host) coordina l'intero caso d'uso sul nodo remoto.

La funzione:

costruisce il modello dati;

richiama i moduli di discovery;

sincronizza la CMDB;

produce l'output finale.

Non accede direttamente ai dettagli del sistema operativo remoto e non implementa direttamente le query SQL.

Flusso

listener
   |
   +-- register_ping(source_ip, destination_ip)
   |
   +-- discovery.run(source_ip)
             |
             +-- hostname.get(host)
             +-- ip.get(host)
             +-- os.get_name(host)
             +-- os.get_version(host)
             +-- kernel.get(host)
             +-- repository.get_by_hostname()
             +-- repository.insert() / repository.update()
             +-- JSON finale

5. Costruzione del modello dati

Modello del nodo

run(host) costruisce il modello dati:

node = {
  "hostname": hostname.get(host),
  "ip_addr": ip.get(host),
  "os_name": os.get_name(host),
  "os_v": os.get_version(host),
  "kernel_v": kernel.get(host),
  "status": ""
}

Il dizionario node accompagna la procedura dalla discovery alla sincronizzazione con la CMDB.

Struttura

Campo

Descrizione

hostname

Nome del nodo remoto

ip_addr

Indirizzo IP del nodo remoto

os_name

Sistema operativo

os_v

Versione del sistema operativo

kernel_v

Versione del kernel

status

Stato della sincronizzazione

Ordine di costruzione

hostname.get(host)
      |
      v
ip.get(host)
      |
      v
os.get_name(host)
      |
      v
os.get_version(host)
      |
      v
kernel.get(host)

Esempio:

{
  "hostname": "s1",
  "ip_addr": "192.168.200.128",
  "os_name": "Linux",
  "os_v": "6.8.0-136-generic",
  "kernel_v": "6.8.0-136-generic",
  "status": "registered"
}

6. Discovery del nodo

Architettura

discovery.run(host)
        |
        +-----------------------+
        |                       |
        v                       v
 hostname.py                 ip.py
        |                       |
        +-----------+-----------+
                    |
                    v
              os.py / kernel.py
                    |
                    v
                   SSH
                    |
                    v
              Nodo remoto

Ogni modulo implementa una sola responsabilità e restituisce un valore al chiamante.

Recupero hostname

hostname.get(host)

Il modulo utilizza:

hostname.get(host)
        |
        v
ssh.execute(host, "hostname")
        |
        v
Nodo remoto

Recupero IP

ip.get(host)

Il modulo esegue il comando necessario sul nodo remoto tramite SSH e restituisce l'indirizzo IP.

Recupero sistema operativo

os.get_name(host)
os.get_version(host)

I valori vengono ottenuti dal nodo remoto tramite SSH e salvati nel modello.

Recupero kernel

kernel.get(host)

Il modulo recupera la versione del kernel dal nodo remoto tramite SSH e aggiorna node["kernel_v"].

Modello completato

node
 |
 +-- hostname
 +-- ip_addr
 +-- os_name
 +-- os_v
 +-- kernel_v
 +-- status

7. Sincronizzazione con la CMDB

Una volta completata la raccolta, repository.py verifica se il nodo è già presente.

node
 |
 v
repository.get_by_hostname()
 |
 +-- presente
 |      |
 |      v
 |  repository.update()
 |      |
 |      v
 |  status = already_registered
 |
 +-- assente
        |
        v
    repository.insert()
        |
        v
    status = registered

Nuovo nodo

Se il nodo non è presente:

ICMP
 |
 v
source_ip
 |
 v
discovery
 |
 v
SSH
 |
 v
repository.insert()
 |
 v
cmdb.nodes

Risultato:

"status": "registered"

Nodo già registrato

Se il nodo è già presente:

discovery
 |
 v
repository.update()
 |
 v
cmdb.nodes

Risultato:

"status": "already_registered"

La procedura evita quindi la creazione di duplicati.

8. Gestione degli errori

Un pacchetto ICMP ricevuto non garantisce che il nodo sia immediatamente raggiungibile via SSH.

Esempio:

Nodo remoto
    |
    | ICMP
    v
Kerni
    |
    | SSH
    v
errore

Un errore di discovery non deve interrompere il listener ICMP.

Il listener deve:

registrare l'evento ICMP;

tentare la discovery;

gestire un eventuale errore;

continuare ad ascoltare nuovi pacchetti.

Il fallimento della discovery di un singolo nodo non deve compromettere l'osservazione degli altri nodi.

9. Esempio completo

Data-node

data-node
192.168.200.131
        |
        | ICMP
        v
Kerni
192.168.200.130

Kerni osserva:

PING: 192.168.200.131 -> 192.168.200.130

Il flusso diventa:

data-node
    |
    | ICMP
    v
Kerni
    |
    +-- tcpip.ping
    |
    +-- discovery.run("192.168.200.131")
              |
              +-- hostname
              +-- IP
              +-- OS
              +-- kernel
                      |
                      v
                     SSH
                      |
                      v
                  data-node
                      |
                      v
                 repository.py
                      |
                      v
                  cmdb.nodes

Output:

{
  "hostname": "data-node",
  "ip_addr": "192.168.200.131",
  "os_name": "Linux",
  "os_v": "6.8.0-136-generic",
  "kernel_v": "6.8.0-136-generic",
  "status": "registered"
}

Un successivo ping dello stesso nodo produce:

{
  "hostname": "data-node",
  "ip_addr": "192.168.200.131",
  "os_name": "Linux",
  "os_v": "6.8.0-136-generic",
  "kernel_v": "6.8.0-136-generic",
  "status": "already_registered"
}

10. Risultato del caso d'uso

Il caso d'uso UC-LX-001 è completato quando:

Kerni osserva un pacchetto ICMP proveniente da un nodo remoto;

identifica il source_ip;

registra l'evento ICMP;

utilizza l'indirizzo IP come destinazione della discovery SSH;

acquisisce hostname, IP, sistema operativo e kernel;

costruisce il modello del nodo;

verifica la presenza nella CMDB;

esegue INSERT oppure UPDATE;

produce il risultato della discovery;

mantiene attivo il listener anche in caso di errore della discovery di un singolo nodo.

Il percorso complessivo è:

ICMP inbound
     |
     v
Identificazione del nodo
     |
     v
SSH
     |
     v
Node Discovery
     |
     v
Modello dati
     |
     v
CMDB
     |
     v
JSON