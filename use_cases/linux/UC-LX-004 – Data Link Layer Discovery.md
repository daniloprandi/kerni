# UC-LX-004 – Data Link Layer Discovery

## 1. Panoramica
* **ID:** UC-LX-004
* **Modulo:** `common/linux/tcp_ip/data_link_layer`
* **Livello OSI:** Livello 2 (Data Link Layer)
* **Stato:** Implementato e Operativo

## 2. Obiettivo
Rilevare dinamicamente a runtime tutte le interfacce di rete fisiche e virtuali presenti sul sistema operativo Linux target, estraendo i relativi indirizzi MAC, lo stato operativo e le statistiche di traffico di basso livello (`rx_bytes`, `tx_bytes`), garantendone la persistenza all'interno del database relazionale PostgreSQL.

## 3. Architettura e Componenti Coinvolti
* **Orchestratore (`node_discovery.py`):** Gestisce il flusso sequenziale della telemetria globale[cite: 1].
* **I/O Layer (`files/`):** Si interfaccia direttamente con i file di pseudo-kernel del sistema operativo (`/sys/class/net/` e `/proc/net/dev`) attuando il principio Unix "everything is a file".
* **Parser (`parser.py`):** Trasforma i dati grezzi letti dal kernel in strutture dati normalizzate (dizionari Python).
* **Inspector (`inspector.py`):** Coordina la logica di ispezione del livello 2.
* **Repository (`repository.py`):** Gestisce la persistenza tramite query SQL parametrizzate verso la tabella `tcpip.network_interfaces`.

## 4. Processo Step-by-Step (Flusso Esecutivo)

### Step 1: Intercettazione dell'Evento (Trigger)
1. Il modulo di ascolto dei pacchetti ICMP (`ping.py`) monitora il traffico di rete[cite: 1].
2. Al ricevimento del **terzo pacchetto ICMP Echo Request** proveniente dal nodo target, il sistema attiva automaticamente la procedura di discovery richiamando l'orchestratore[cite: 1].

### Step 2: Inizializzazione dell'Orchestratore (`node_discovery.py`)
1. L'orchestratore riceve l'indirizzo IP dell'host e provvede a registrare o aggiornare le informazioni anagrafiche di base del nodo all'interno della CMDB (`cmdb.nodes`).
2. Viene recuperato l'identificativo univoco del nodo (`node_id`) indispensabile per associare i dati relazionali delle interfacce.

### Step 3: Ispezione del File System Virtuale (`files/`)
1. L'inspector individua dinamicamente tutte le interfacce di rete presenti leggendo il contenuto della directory `/sys/class/net/` tramite `os.listdir()`.
2. Per ciascuna interfaccia rilevata, il sotto-modulo di I/O legge in modo sicuro:
   * L'indirizzo MAC dal file `/sys/class/net/<iface>/address`.
   * Lo stato operativo dal file `/sys/class/net/<iface>/operstate`.
   * I contatori dei byte ricevuti e trasmessi leggendo le metriche di traffico da `/proc/net/dev`.

### Step 4: Normalizzazione dei Dati (`parser.py`)
1. Il parser riceve i flussi di dati grezzi prelevati dai file di sistema.
2. I dati vengono puliti, convertiti nei tipi corretti e strutturati in una lista di record uniformi pronti per essere inseriti nel database.

### Step 5: Persistenza su Database (`repository.py`)
1. Il repository apre una connessione sicura con PostgreSQL utilizzando le credenziali e le funzioni condivise del modulo `common.database`.
2. Viene eseguita un'operazione batch tramite query SQL parametrizzate per inserire i dati nella tabella `tcpip.network_interfaces`:
   * Campi registrati: `node_id`, `iface`, `eth_addr`, `state`, `rx_bytes`, `tx_bytes`.
3. La transazione viene confermata (`commit()`) e le risorse di connessione vengono rilasciate in modo sicuro tramite i blocchi `finally`.

## 5. Gestione degli Errori e Resilienza
* **Isolamento dei Fault:** Eventuali errori riscontrati durante la lettura delle interfacce o durante la scrittura nel repository vengono intercettati da blocchi `try-except` dedicati all'interno dell'orchestratore.
* **Continuità della Pipeline:** Un'eccezione sul Data Link Layer viene registrata nei log di sistema ma **non blocca** l'esecuzione degli altri livelli di telemetria (come i processi, i socket o il transport layer), garantendo la massima resilienza operativa al demone `kerni.service`.