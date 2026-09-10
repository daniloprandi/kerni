# UC-LX-002 – Transport Layer Discovery

## 1. Obiettivo

### Scopo

Il caso d'uso UC-LX-002 – Transport Layer Discovery descrive il processo con cui Kerni, a seguito della Node Discovery di un nodo Linux remoto, identifica e raccoglie le informazioni relative alle connessioni e ai socket presenti nel sistema operativo remoto.

L'ispezione viene eseguita automaticamente dopo che il nodo è stato identificato e associato al relativo `node_id` nella CMDB.

Il processo utilizza SSH per accedere al nodo remoto e leggere le tabelle esposte dal kernel Linux attraverso il filesystem `/proc`.

Le informazioni vengono raccolte dalle seguenti sorgenti:

/proc/net/tcp
/proc/net/tcp6
/proc/net/udp
/proc/net/udp6
/proc/net/raw
/proc/net/raw6
/proc/net/unix

I dati grezzi vengono successivamente interpretati dai parser del Transport Layer e trasformati nel modello `Connection`.

Le connessioni rilevate vengono quindi associate al nodo tramite `node_id` e salvate nella tabella `tcpip.transport_connections`.

Il caso d'uso conserva ogni rilevazione nel database.

Non viene effettuata una sostituzione delle rilevazioni precedenti: ogni nuova ispezione produce un nuovo insieme di record, permettendo di mantenere lo storico delle osservazioni.

---

## 2. Scenario

### Avvio della procedura

La Transport Layer Discovery viene avviata automaticamente al termine della Node Discovery.

Il flusso complessivo parte dall'osservazione di un pacchetto ICMP proveniente da un nodo remoto.

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

Il flusso diventa:

ICMP
  |
  v
Node Discovery
  |
  v
cmdb.nodes
  |
  | node_id
  v
Transport Layer Discovery
  |
  v
SSH
  |
  v
/proc/net/*
  |
  v
Parser
  |
  v
Connection model
  |
  v
Repository
  |
  v
tcpip.transport_connections

Non sono richiesti ulteriori interventi dell'utente.

### Relazione con la Node Discovery

La Transport Layer Discovery non identifica autonomamente il nodo.

La Node Discovery ha già il compito di:

source_ip
    |
    v
SSH
    |
    v
hostname / IP / OS / kernel
    |
    v
cmdb.nodes
    |
    v
node_id

Il `node_id` ottenuto dalla CMDB viene utilizzato dalla Transport Layer Discovery per associare ogni connessione al nodo corretto.

---

## 3. Architettura

### Attori

| Attore | Responsabilità |
|---|---|
| Nodo remoto | Fornisce le informazioni relative ai propri socket e connessioni |
| Kerni | Coordina l'ispezione del Transport Layer |
| Node Discovery | Identifica il nodo e recupera il `node_id` |
| SSH | Esegue i comandi sul nodo remoto |
| Linux `/proc` | Espone le informazioni relative ai socket del kernel |
| Transport Layer Inspector | Coordina raccolta e parsing |
| Parser | Interpreta le tabelle `/proc` |
| Repository | Persiste le connessioni |
| PostgreSQL | Conserva lo storico delle osservazioni |

### Componenti

common/linux/node_discovery/discovery.py

Coordina la Node Discovery e avvia l'ispezione del Transport Layer.

common/linux/tcp_ip/transport_layer/inspector.py

Coordina la raccolta delle informazioni dal nodo remoto.

common/linux/tcp_ip/transport_layer/parser.py

Interpreta i dati ottenuti dalle tabelle `/proc`.

common/linux/tcp_ip/transport_layer/models.py

Definisce il modello `Connection`.

common/linux/tcp_ip/transport_layer/repository.py

Salva le connessioni nel database.

common/linux/tcp_ip/transport_layer/files/

Contiene i moduli responsabili della lettura delle singole tabelle Linux:

tcp.py
tcp6.py
udp.py
udp6.py
raw.py
raw6.py
unix.py

Ogni componente implementa una responsabilità specifica.

---

## 4. Avvio della Transport Layer Discovery

Al termine della Node Discovery viene recuperato il record del nodo dalla CMDB.

Il repository restituisce il relativo identificativo:

repository.get_by_hostname()
        |
        v
     node_id

Esempio:

hostname = s1
ip_addr  = 192.168.200.128
node_id  = 10003

Il `node_id` viene quindi passato all'Inspector:

host
 |
 v
inspect_transport_layer(host, node_id)

Il flusso diventa:

discovery.run(host)
        |
        v
repository.get_by_hostname()
        |
        v
      node_id
        |
        v
inspector.inspect_transport_layer()

Questo permette di mantenere separati i due concetti:

Node Discovery
    |
    +-- identifica il nodo

Transport Layer Discovery
    |
    +-- identifica le connessioni del nodo

---

## 5. Connessione SSH

L'Inspector costruisce l'host SSH del nodo remoto.

Esempio:

dprandi@192.168.200.128

La connessione viene utilizzata per eseguire comandi sul sistema remoto.

Per la raccolta TCP viene eseguito:

cat /proc/net/tcp

Per IPv6:

cat /proc/net/tcp6

Lo stesso meccanismo viene utilizzato per le altre tabelle.

Il flusso è:

Kerni
  |
  | SSH
  v
Nodo remoto
  |
  +-- /proc/net/tcp
  +-- /proc/net/tcp6
  +-- /proc/net/udp
  +-- /proc/net/udp6
  +-- /proc/net/raw
  +-- /proc/net/raw6
  +-- /proc/net/unix

L'Inspector non interpreta direttamente il contenuto delle tabelle.

I dati vengono invece passati ai parser dedicati.

---

## 6. Raccolta delle informazioni

### TCP

La prima sorgente analizzata è:

/proc/net/tcp

Il contenuto viene ottenuto tramite SSH:

ssh.execute(
    ssh_host,
    "cat /proc/net/tcp"
)

Successivamente viene passato al parser:

parse_transport(
    tcp_data.splitlines(),
    "TCP"
)

### TCP IPv6

La seconda sorgente è:

/proc/net/tcp6

Il flusso è:

/proc/net/tcp6
       |
       v
SSH
       |
       v
parse_transport6()
       |
       v
Connection

Il protocollo viene identificato come:

TCP6

### UDP

La tabella UDP viene letta attraverso:

/proc/net/udp

Il contenuto viene interpretato dal parser del Transport Layer con identificatore:

UDP

### UDP IPv6

Per IPv6 viene utilizzata:

/proc/net/udp6

Il protocollo viene identificato come:

UDP6

### RAW

L'Inspector legge inoltre:

/proc/net/raw

e passa il contenuto al parser con identificatore:

RAW

### RAW IPv6

La corrispondente tabella IPv6 è:

/proc/net/raw6

Il protocollo viene identificato come:

RAW6

### UNIX

Infine viene analizzata:

/proc/net/unix

Il contenuto viene passato al parser UNIX:

parse_unix(
    unix_data.splitlines(),
    "UNIX"
)

Il protocollo viene identificato come:

UNIX

---

## 7. Costruzione del modello Connection

I dati provenienti dalle diverse tabelle vengono trasformati dai parser in oggetti compatibili con il modello `Connection`.

Il risultato può essere rappresentato come:

/proc/net/*
      |
      v
    Parser
      |
      v
  Connection

Il modello può contenere informazioni come:

node_id
proto

src_ip
src_port

dst_ip
dst_port

state

uid
username

inode

type
flags
path

detected_at

I campi dipendono dal tipo di socket osservato e dalle informazioni disponibili nella relativa tabella `/proc`.

Il parser separa quindi:

raccolta del dato

da:

interpretazione del dato

e da:

persistenza del dato

---

## 8. Associazione al nodo

Dopo che tutte le connessioni sono state raccolte e interpretate, ogni elemento viene associato al nodo osservato.

Il flusso è:

connections
     |
     v
for connection
     |
     v
connection["node_id"] = node_id

Esempio:

Nodo:
    node_id = 10003

Connessione:
    proto = TCP
    src_ip = 192.168.200.128
    src_port = 22

diventa:

node_id = 10003
proto = TCP
src_ip = 192.168.200.128
src_port = 22

Questa associazione permette di identificare a quale nodo appartiene ogni osservazione.

---

## 9. Persistenza delle connessioni

Una volta completata la raccolta, l'Inspector passa le connessioni al repository:

connections
     |
     v
repository.insert_all()
     |
     v
PostgreSQL

Il repository inserisce i dati nella tabella:

tcpip.transport_connections

Esempio concettuale:

tcpip.transport_connections

+---------+-------+-----------------+----------+-----------------+----------+
| node_id | proto | src_ip          | src_port | dst_ip          | dst_port |
+---------+-------+-----------------+----------+-----------------+----------+
| 10003   | TCP   | 192.168.200.128 | 22       | ...             | ...      |
| 10003   | TCP   | 127.0.0.1       | 5432     | ...             | ...      |
| 10003   | UDP   | 0.0.0.0         | 53       | ...             | ...      |
+---------+-------+-----------------+----------+-----------------+----------+

---

## 10. Conservazione dello storico

Una caratteristica fondamentale del caso d'uso è la conservazione delle osservazioni precedenti.

La Transport Layer Discovery non considera la tabella come una semplice rappresentazione dello stato corrente.

Ogni esecuzione rappresenta invece una nuova osservazione del sistema.

Esempio:

Prima ispezione
      |
      v
197 connessioni
      |
      v
INSERT

Successivamente:

Seconda ispezione
      |
      v
198 connessioni
      |
      v
INSERT

Il database conserva entrambe le osservazioni.

tcpip.transport_connections

snapshot 1
   |
   +-- connessioni osservate

snapshot 2
   |
   +-- connessioni osservate

snapshot 3
   |
   +-- connessioni osservate

Non viene effettuato:

DELETE

e non viene effettuato un aggiornamento delle vecchie connessioni per sostituirle con quelle nuove.

Questo permette a Kerni di costruire successivamente analisi temporali sul comportamento del nodo.

---

## 11. Esecuzione completa

Il flusso completo del caso d'uso è:

Nodo remoto
     |
     | ICMP
     v
Kerni
     |
     v
ICMP Listener
     |
     v
source_ip
     |
     v
Node Discovery
     |
     +-- hostname
     +-- IP
     +-- OS
     +-- kernel
     |
     v
cmdb.nodes
     |
     v
node_id
     |
     v
Transport Layer Inspector
     |
     | SSH
     v
Nodo remoto
     |
     +-- /proc/net/tcp
     +-- /proc/net/tcp6
     +-- /proc/net/udp
     +-- /proc/net/udp6
     +-- /proc/net/raw
     +-- /proc/net/raw6
     +-- /proc/net/unix
     |
     v
Parser
     |
     v
Connection model
     |
     v
node_id
     |
     v
repository.insert_all()
     |
     v
tcpip.transport_connections
     |
     v
Storico

---

## 12. Esempio completo

Consideriamo:

data-node
192.168.200.131

che invia un ping a:

Kerni
192.168.200.130

Kerni osserva:

PING: 192.168.200.131 -> 192.168.200.130

La Node Discovery identifica il nodo:

hostname: data-node
ip_addr: 192.168.200.131

e recupera:

node_id: 10005

A questo punto viene avviata automaticamente la Transport Layer Discovery:

node_id = 10005
host = 192.168.200.131

L'Inspector esegue:

SSH
 |
 +-- cat /proc/net/tcp
 |
 +-- cat /proc/net/tcp6
 |
 +-- cat /proc/net/udp
 |
 +-- cat /proc/net/udp6
 |
 +-- cat /proc/net/raw
 |
 +-- cat /proc/net/raw6
 |
 +-- cat /proc/net/unix

I dati vengono interpretati:

raw /proc data
      |
      v
    Parser
      |
      v
 Connections
      |
      v
 node_id = 10005
      |
      v
 PostgreSQL

Il risultato viene quindi memorizzato in:

tcpip.transport_connections

---

## 13. Risultato del caso d'uso

Il caso d'uso UC-LX-002 – Transport Layer Discovery è completato quando:

- Kerni ha identificato il nodo remoto;
- il nodo è associato a un `node_id`;
- l'Inspector ha effettuato la connessione SSH;
- le tabelle `/proc/net/*` previste sono state raccolte;
- i dati sono stati interpretati dai parser;
- le connessioni sono state associate al `node_id`;
- le connessioni sono state inserite in PostgreSQL;
- la nuova osservazione è stata conservata nello storico.

Il risultato finale può essere rappresentato come:

Nodo
  |
  v
node_id
  |
  v
Transport Layer inspection
  |
  v
/proc/net/*
  |
  v
Parser
  |
  v
Connection
  |
  v
Repository
  |
  v
tcpip.transport_connections

---

## 14. Architettura complessiva del caso d'uso

                         Nodo remoto
                              |
                              | ICMP
                              v
                            Kerni
                              |
                              v
                       ICMP Listener
                              |
                              | source_ip
                              v
                       Node Discovery
                              |
                 +------------+------------+
                 |            |            |
                 v            v            v
             hostname       IP           OS
                 \            |            /
                  \           |           /
                   +----------+----------+
                              |
                              v
                         SSH Discovery
                              |
                              v
                          cmdb.nodes
                              |
                              | node_id
                              v
                 Transport Layer Inspector
                              |
                              | SSH
                              v
                        Nodo remoto
                              |
        +----------+----------+----------+----------+
        |          |          |          |          |
        v          v          v          v          v
      TCP/TCP6   UDP/UDP6   RAW/RAW6    UNIX
        |          |          |          |
        +----------+----------+----------+
                              |
                              v
                           Parser
                              |
                              v
                      Connection model
                              |
                              v
                         node_id
                              |
                              v
                    repository.insert_all()
                              |
                              v
                tcpip.transport_connections
                              |
                              v
                         Storico

---

## 15. Principio architetturale

Il caso d'uso mantiene la separazione delle responsabilità introdotta dalla Node Discovery.

ICMP Listener
     |
     +-- osserva il traffico

Node Discovery
     |
     +-- identifica il nodo

Transport Inspector
     |
     +-- coordina l'ispezione

/proc readers
     |
     +-- leggono i dati Linux

Parser
     |
     +-- interpretano i dati

Model
     |
     +-- rappresenta una connessione

Repository
     |
     +-- persiste i dati

PostgreSQL
     |
     +-- conserva lo storico

In questo modo nessun componente deve occuparsi direttamente di tutte le fasi del processo.

Il principio architetturale è la separazione tra osservazione, discovery, raccolta, interpretazione e persistenza.

### Flusso sintetico

ICMP
 ↓
Node Discovery
 ↓
node_id
 ↓
SSH
 ↓
Linux /proc
 ↓
Parser
 ↓
Connection
 ↓
Repository
 ↓
PostgreSQL
 ↓
Historical observations
