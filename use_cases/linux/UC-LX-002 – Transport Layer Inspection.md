1. Obiettivo

Il caso d'uso UC-LX-002 – Transport Layer Inspection descrive il processo con cui Kerni acquisisce le informazioni del livello di trasporto di un nodo Linux.

La procedura legge direttamente le tabelle pubblicate dal kernel nel filesystem virtuale /proc/net, identifica tutte le connessioni attive, le associa al nodo registrato nella CMDB e ne memorizza lo stato.

I protocolli analizzati sono:

TCP IPv4
TCP IPv6
UDP IPv4
UDP IPv6
RAW IPv4
RAW IPv6
UNIX Domain Socket

L'accesso diretto a /proc/net permette di osservare lo stato del kernel senza utilizzare strumenti esterni come netstat o ss.

2. Scenario
Contesto operativo

Dopo la registrazione del nodo tramite UC-LX-001 – Node Discovery, Kerni può acquisire informazioni sempre più dettagliate sul sistema.

Il Transport Layer Inspector rappresenta il componente dedicato all'osservazione delle connessioni di rete mantenute dal kernel Linux.

La procedura:

identifica il nodo;
verifica la registrazione nella CMDB;
legge le tabelle del Transport Layer;
interpreta le connessioni;
associa ogni connessione al nodo;
memorizza i risultati nel database;
restituisce un documento JSON.

L'intera procedura viene eseguita automaticamente.

3. Architettura
Attori
Attore	Responsabilità
Amministratore	Avvia l'ispezione
Nodo Linux	Espone le informazioni tramite /proc/net
Kernel Linux	Aggiorna le tabelle delle connessioni
CMDB	Memorizza le connessioni associate al nodo

Ogni componente opera nel proprio livello di responsabilità.

Componenti
Modulo	Responsabilità
test_transport_layer.py	Punto di ingresso
inspector.py	Coordinamento della procedura
tcp.py, tcp6.py, udp.py, udp6.py, raw.py, raw6.py, unix.py	Lettura delle tabelle /proc/net
Parser	Interpretazione delle connessioni
Repository Transport Layer	Persistenza delle connessioni
Repository Node Discovery	Identificazione del nodo

Ogni componente implementa una singola responsabilità e comunica attraverso interfacce semplici.

Architettura del caso d'uso
                 Amministratore
                        │
                        ▼
         test_transport_layer.py
                        │
                        ▼
              inspector.run()
                        │
                        ▼
         inspect_transport_layer()
                        │
        ┌───────────────┴───────────────┐
        ▼                               ▼
 Node Discovery                  /proc/net/*
        │                               │
        ▼                               ▼
 Identificazione nodo        Lettura tabelle Linux
        └───────────────┬───────────────┘
                        ▼
               Parsing connessioni
                        ▼
            Associazione al nodo
                        ▼
          Salvataggio nella CMDB
                        ▼
              Restituzione JSON

L'architettura è suddivisa in quattro livelli:

Discovery, per identificare il nodo.
Acquisizione, per leggere le tabelle del kernel.
Elaborazione, per interpretare le connessioni.
Persistence, per aggiornare la CMDB.

inspect_transport_layer() coordina il flusso senza implementare direttamente la lettura dei file o l'accesso al database.

4. Flusso di esecuzione
Punto di ingresso

L'esecuzione inizia con:

python test_transport_layer.py

Python crea un nuovo processo ed esegue il modulo principale.

Il file contiene esclusivamente il punto di ingresso dell'applicazione.

import json

from common.linux.tcp_ip.transport_layer.inspector import run


def main():

  # Run the Transport Layer inspection.
  result = run()

  # Print the inspection result.
  print(json.dumps(result, indent=2))


if __name__ == "__main__":
  main()

La logica del caso d'uso è completamente delegata a inspector.py.

Importazione del coordinatore

La prima istruzione significativa è:

from common.linux.tcp_ip.transport_layer.inspector import run

Il modulo principale importa la funzione run(), che rappresenta il punto di accesso pubblico del sottosistema Transport Layer.

Il file di avvio conosce solo l'interfaccia della procedura, non la sua implementazione.

Avvio della procedura

La funzione main() esegue due operazioni:

result = run()

print(json.dumps(result, indent=2))

La prima richiama il coordinatore dell'ispezione.

La seconda converte il risultato in JSON e lo visualizza sul terminale.

Ruolo di run()

L'interfaccia pubblica di inspector.py è costituita dalla funzione:

def run():

  # Execute the inspection.
  return inspect_transport_layer()

run() non implementa alcuna logica di ispezione. Espone un punto di ingresso stabile e delega l'intera procedura a inspect_transport_layer().

Coordinamento dell'ispezione

inspect_transport_layer() rappresenta il centro del caso d'uso.

La funzione coordina le seguenti operazioni:

inspect_transport_layer()

        │
        ▼
Recupero hostname
        ▼
Ricerca del nodo
        ▼
Lettura tabelle /proc/net
        ▼
Parsing delle connessioni
        ▼
Associazione al nodo
        ▼
Salvataggio nel database
        ▼
Restituzione del risultato

Ogni fase viene delegata a un componente specializzato. La funzione mantiene esclusivamente il controllo del flusso di esecuzione.

Identificazione del nodo

La procedura recupera l'hostname e verifica che il nodo sia registrato nella CMDB.

hostname_value = hostname.get()

node = node_repository.get_by_hostname(
    hostname_value
)

Se il nodo non è presente, la procedura termina immediatamente.

if node is None:
    return {
        "error": "Node not registered."
    }

Questa verifica introduce una dipendenza funzionale con UC-LX-001 – Node Discovery: il Transport Layer Inspector può operare solo su nodi già registrati.

Preparazione dell'ispezione

Verificata la presenza del nodo, viene inizializzata la struttura dati che conterrà tutte le connessioni.

connections = []

Questa lista rappresenta il modello condiviso della procedura. Ogni protocollo contribuirà ad aggiungere le proprie connessioni alla stessa collezione.

run()
    │
    ▼
inspect_transport_layer()
    │
    ▼
hostname.get()
    │
    ▼
node_repository.get_by_hostname()
    │
    ▼
Nodo registrato?
 ┌───────────────┐
 │      NO       │────► Fine procedura
 └───────────────┘
        │
       SI
        ▼
connections = []
        │
        ▼
Inizio lettura del Transport Layer

Da questo punto inizia la fase di acquisizione delle informazioni dal kernel Linux.

5. Acquisizione delle informazioni dal Transport Layer
Il filesystem virtuale /proc

Il Transport Layer Inspector acquisisce le informazioni direttamente dal filesystem virtuale /proc.

A differenza di strumenti come netstat o ss, Kerni non esegue programmi esterni. Legge le strutture dati esposte dal kernel Linux, ottenendo una rappresentazione aggiornata dello stato delle connessioni.

Le tabelle analizzate si trovano nella directory:

/proc/net

La struttura principale è la seguente:

/proc
 └── net
      ├── tcp
      ├── tcp6
      ├── udp
      ├── udp6
      ├── raw
      ├── raw6
      └── unix

Ogni file rappresenta una vista del Transport Layer mantenuta dal kernel. Il contenuto viene aggiornato automaticamente quando una connessione viene aperta, modificata o chiusa.

Moduli di lettura

Ogni tabella è gestita da un modulo dedicato.

Modulo	Tabella
tcp.py	/proc/net/tcp
tcp6.py	/proc/net/tcp6
udp.py	/proc/net/udp
udp6.py	/proc/net/udp6
raw.py	/proc/net/raw
raw6.py	/proc/net/raw6
unix.py	/proc/net/unix

Tutti i moduli seguono lo stesso schema implementativo.

def read():

    proc_path = os.getenv("PROC_PATH", "/proc")

    tcp_file = Path(proc_path) / "net" / "tcp"

    if not tcp_file.exists():
        return []

    with tcp_file.open("r") as file:
        lines = file.readlines()

    return lines

La funzione:

individua la directory /proc;
costruisce il percorso del file;
verifica che il file esista;
restituisce tutte le righe della tabella.

La lettura termina qui. Il modulo non interpreta il contenuto del file.

Configurazione tramite PROC_PATH

Il percorso del filesystem viene determinato dinamicamente.

proc_path = os.getenv("PROC_PATH", "/proc")

Se la variabile PROC_PATH non è definita, viene utilizzata /proc.

Questa scelta rende il componente indipendente dall'ambiente di esecuzione. Nel progetto Kerni il filesystem dell'host può essere montato all'interno di un container Docker senza modificare il codice dell'applicazione.

Coordinamento della lettura

Terminata l'identificazione del nodo, inspect_transport_layer() avvia la lettura delle tabelle.

connections.extend(
    parse_transport(
        tcp.read(),
        "TCP"
    )
)

connections.extend(
    parse_transport6(
        tcp6.read(),
        "TCP6"
    )
)

connections.extend(
    parse_transport(
        udp.read(),
        "UDP"
    )
)

connections.extend(
    parse_transport6(
        udp6.read(),
        "UDP6"
    )
)

Lo stesso schema viene applicato alle tabelle RAW e UNIX Domain Socket.

Ogni protocollo segue sempre la stessa pipeline:

File Linux
      │
      ▼
read()
      │
      ▼
Lista di righe
      │
      ▼
Parser
      │
      ▼
Lista di connessioni
      │
      ▼
connections.extend()

Cambiano solamente il modulo di lettura e il parser utilizzato. L'algoritmo rimane invariato.

Aggregazione dei risultati

Ogni parser restituisce una lista di connessioni.

Il coordinatore utilizza:

connections.extend(...)

per aggiungere i risultati alla stessa collezione.

L'evoluzione della struttura dati è la seguente.

connections

[]

        │

        ▼

TCP

[TCP...]

        │

        ▼

TCP6

[TCP..., TCP6...]

        │

        ▼

UDP

[TCP..., TCP6..., UDP...]

        │

        ▼

RAW

[...]

        │

        ▼

UNIX

[Tutte le connessioni]

Al termine della fase di acquisizione tutte le connessioni del nodo sono disponibili in un unico modello dati.

6. Parsing delle connessioni
Separazione tra acquisizione ed elaborazione

I moduli della directory files leggono esclusivamente le tabelle del kernel.

L'interpretazione delle informazioni è demandata ai parser.

Questa separazione isola due responsabilità distinte:

accesso al filesystem;
conversione delle informazioni.

Il flusso architetturale è il seguente.

Kernel Linux

      │

      ▼

/proc/net/*

      │

      ▼

Moduli read()

      │

      ▼

Parser

      │

      ▼

Oggetti Python

      │

      ▼

Lista connections

Ogni livello utilizza esclusivamente il risultato prodotto dal livello precedente.

Parser disponibili

Il Transport Layer utilizza tre parser.

Parser	Responsabilità
parse_transport()	TCP, UDP e RAW IPv4
parse_transport6()	TCP, UDP e RAW IPv6
parse_unix()	UNIX Domain Socket

Ogni parser riceve le righe della tabella già lette dai moduli read(). Nessuno accede direttamente al filesystem.

Interpretazione delle tabelle

Il parser elimina l'intestazione della tabella.

lines = lines[1:]

Successivamente crea la lista dei risultati.

connections = []

Infine analizza ogni riga.

for line in lines:

Ogni iterazione rappresenta una connessione pubblicata dal kernel Linux.

Conversione dei dati

Le tabelle del kernel utilizzano rappresentazioni esadecimali.

I parser convertono tali valori mediante funzioni dedicate.

Tra le principali:

parse_ip()
parse_ip6()
parse_port()
parse_endpoint()
parse_endpoint6()

Ad esempio, un indirizzo IPv4 viene convertito tramite:

def parse_ip(ip):

    ip_bytes = bytes.fromhex(ip)

    ip_bytes = ip_bytes[::-1]

    return socket.inet_ntoa(ip_bytes)

Le porte vengono convertite con:

int(port, 16)

Il risultato è una rappresentazione direttamente utilizzabile dall'applicazione.

Il parser esegue inoltre la normalizzazione dell'identificativo dell'utente Linux proprietario della connessione.

Il kernel espone esclusivamente il campo UID. Tramite il modulo common.linux.users.user il parser risolve l'identificativo numerico nel corrispondente username utilizzando le informazioni del sistema operativo.

Ad esempio:

UID

1000

↓

username

dprandi

L'oggetto della connessione contiene quindi sia il valore originale del kernel (uid) sia la relativa rappresentazione leggibile (username). Questa normalizzazione rende il modello dati più comprensibile senza perdere l'informazione originaria.

Costruzione del modello delle connessioni

Terminata la conversione, il parser costruisce un oggetto Python per ogni connessione.

Le informazioni principali comprendono:

protocollo;
endpoint sorgente;
endpoint destinazione;
stato;
UID;
username (Linux associato all'UID);
inode.

Ogni oggetto viene aggiunto alla lista:

connections.append({

    ...

})

Al termine dell'elaborazione il parser restituisce:

return connections

Il coordinatore unisce progressivamente i risultati di tutti i protocolli nella lista condivisa connections.

Parsing delle UNIX Domain Socket

Le UNIX Domain Socket utilizzano una struttura diversa dalle connessioni IP.

Il parser estrae:

tipo del socket;
stato;
inode;
flag;
percorso del file.

Il percorso viene ricostruito quando presente.

path = None

if len(fields) > 7:
    path = " ".join(fields[7:])

Poiché non utilizzano indirizzi IP, i campi relativi agli endpoint vengono impostati a None.

Traduzione degli stati

I parser convertono i codici numerici del kernel in valori descrittivi.

Per TCP:

01 → ESTABLISHED
02 → SYN_SENT
03 → SYN_RECV
0A → LISTEN

Per le UNIX Domain Socket vengono convertiti:

tipo del socket;
stato della connessione.

Questa conversione rende il modello dati indipendente dalla codifica interna del kernel e più leggibile per il resto dell'applicazione.

Al termine di questa fase, inspect_transport_layer() dispone di una collezione omogenea contenente tutte le connessioni rilevate sul nodo. La fase successiva arricchisce ogni connessione con il node_id e ne gestisce la persistenza nella CMDB.

7. Persistenza nella CMDB
Associazione delle connessioni al nodo

Al termine del parsing, inspect_transport_layer() dispone di una collezione contenente tutte le connessioni rilevate sul sistema.

Ogni connessione descrive lo stato del Transport Layer ma non è ancora associata al nodo Linux che l'ha generata.

L'associazione avviene tramite l'identificativo recuperato durante la fase iniziale della procedura.

for connection in connections:

    connection["node_id"] = node[0]

La stessa operazione viene applicata a ogni elemento della collezione.

Questa fase crea il collegamento tra il livello di osservabilità e il modello inventariale della CMDB.

Relazione tra nodo e connessioni

L'identificativo del nodo diventa una chiave comune per tutte le connessioni osservate.

Nodo Linux

    │

    ▼

node_id = 12

    │

    ├───────────────┐
    │               │
    ▼               ▼

Connessione A   Connessione B

node_id=12      node_id=12

La CMDB può così distinguere connessioni appartenenti a nodi differenti senza modificare il modello delle connessioni.

Arricchimento del modello dati

Prima dell'associazione una connessione contiene esclusivamente le informazioni ricavate dal kernel.

{

  "proto": "TCP",

  "src_ip": "192.168.200.10",
  "src_port": 443,

  "dst_ip": "192.168.200.25",
  "dst_port": 53214,

  "state": "ESTABLISHED",

  "uid": 1000,

  "username": "dprandi",

  "inode": 84562,

  "type": None,

  "flags": None,

  "path": None

}

Dopo l'associazione viene aggiunto node_id.

{

  "node_id": 12,

  "proto": "TCP",

  "src_ip": "192.168.200.10",
  "src_port": 443,

  "dst_ip": "192.168.200.25",
  "dst_port": 53214,

  "state": "ESTABLISHED",

  "uid": 1000,

  "username": "dprandi",

  "inode": 84562,

  "type": None,

  "flags": None,

  "path": None

}

Il modello contiene ora tutte le informazioni necessarie alla persistenza.

Persistenza delle connessioni

La procedura delega la scrittura al repository dedicato.

repository.insert_all(connections)

inspect_transport_layer() non costruisce query SQL e non comunica direttamente con PostgreSQL.

Il repository rappresenta l'unico punto di accesso alla CMDB e centralizza tutte le operazioni di persistenza.

Conclusione della sincronizzazione

La fase termina quando tutte le connessioni risultano associate al nodo e consegnate al repository.

connections

      │

      ▼

Associazione node_id

      │

      ▼

repository.insert_all()

      │

      ▼

Database

      │

      ▼

Connessioni memorizzate

A questo punto il caso d'uso dispone di una rappresentazione persistente dello stato del Transport Layer del nodo.

8. Output, architettura complessiva e conclusioni
Restituzione del risultato

Terminata la persistenza, inspect_transport_layer() restituisce il risultato dell'ispezione.

return {
    "connections": connections
}

L'utilizzo di un oggetto contenitore rende l'interfaccia facilmente estendibile con nuove informazioni, come statistiche o dati diagnostici.

Produzione del documento JSON

Il controllo ritorna alla funzione run() e successivamente al programma principale.

result = run()

print(
    json.dumps(
        result,
        indent=2
    )
)

json.dumps() serializza la struttura Python e produce il documento JSON visualizzato sul terminale.

L'opzione indent=2 migliora esclusivamente la leggibilità dell'output.

Struttura del risultato

L'output contiene tutte le connessioni raccolte durante l'ispezione.

{
  "connections": [

    {
      "node_id": 12,
      "proto": "TCP",
      "src_ip": "192.168.200.128",
      "src_port": 22,
      "dst_ip": "192.168.200.15",
      "dst_port": 53210,
      "state": "ESTABLISHED",
      "uid": 0,
      "username": "root",
      "inode": 35120,
      "type": null,
      "flags": null,
      "path": null
    },

    {
      "node_id": 12,
      "proto": "UNIX",
      "src_ip": null,
      "src_port": null,
      "dst_ip": null,
      "dst_port": null,
      "state": "CONNECTED",
      "uid": 0,
      "username": "root",
      "inode": 48291,
      "type": "STREAM",
      "flags": "00010000",
      "path": "/run/systemd/private"
    }

  ]
}

Il formato uniforme permette ai componenti successivi di elaborare connessioni TCP, UDP, RAW e UNIX Domain Socket senza conoscere il formato originario delle tabelle del kernel.

Flusso complessivo
                     Amministratore

                           │

                           ▼

          python test_transport_layer.py

                           │

                           ▼

               test_transport_layer.py

                           │

                           ▼

                       main()

                           │

                           ▼

                         run()

                           │

                           ▼

            inspect_transport_layer()

                           │

          ┌────────────────┴────────────────┐

          ▼                                 ▼

hostname.get()                node_repository.get_by_hostname()

          │                                 │

          └────────────────┬────────────────┘

                           ▼

                 Nodo registrato?

                  │              │

                 NO             SI

                  │              ▼

                  │       Lettura /proc/net/*

                  │              │

                  │      ┌───────┼──────────────┐

                  │      ▼       ▼              ▼

                  │    Reader   Parser   connections

                  │              │

                  │              ▼

                  │      Associazione node_id

                  │              │

                  │              ▼

                  │   repository.insert_all()

                  │              │

                  └────► return {"connections": ...}

                                 │

                                 ▼

                            json.dumps()

                                 │

                                 ▼

                               print()

Il diagramma evidenzia una pipeline composta da acquisizione, elaborazione e persistenza, con responsabilità chiaramente separate.

Analisi dell'architettura

L'architettura del caso d'uso è organizzata in livelli indipendenti.

test_transport_layer.py costituisce il punto di ingresso.
inspector.py coordina il flusso.
I moduli read() acquisiscono le informazioni dal kernel.
I parser convertono le tabelle del kernel in oggetti Python.
Il repository gestisce la persistenza nella CMDB.

Ogni componente implementa una singola responsabilità e comunica attraverso interfacce semplici. Questa separazione riduce l'accoppiamento e facilita manutenzione ed estensione del sistema.

Benefici della soluzione

L'architettura offre i seguenti vantaggi:

accesso diretto alle informazioni del kernel senza strumenti esterni;
separazione tra acquisizione, parsing e persistenza;
modello dati uniforme per tutti i protocolli del Transport Layer;
associazione esplicita tra connessioni e nodo tramite node_id;
integrazione diretta con la CMDB di Kerni.
Conclusioni

UC-LX-002 – Transport Layer Inspection realizza l'acquisizione dello stato del livello di trasporto di un nodo Linux attraverso il filesystem virtuale /proc/net.

La procedura identifica il nodo, legge le tabelle del kernel, interpreta le connessioni, le associa alla CMDB e restituisce un documento JSON contenente una rappresentazione strutturata del Transport Layer.

L'architettura mantiene separati acquisizione, elaborazione e persistenza, consentendo di estendere il sistema con nuovi protocolli o nuove sorgenti di osservazione senza modificare il flusso generale dell'applicazione.