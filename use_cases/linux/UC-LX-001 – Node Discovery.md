1. Obiettivo
Scopo

Il caso d'uso UC-LX-001 – Node Discovery descrive il processo con cui Kerni identifica automaticamente un nodo Linux e sincronizza le informazioni raccolte con la Configuration Management Data Base (CMDB).

La procedura acquisisce:

hostname;
indirizzo IP principale;
sistema operativo;
versione del sistema operativo;
versione del kernel.

Al termine della discovery verifica la presenza del nodo nella CMDB ed esegue un'operazione di INSERT o UPDATE.

Il risultato viene restituito in formato JSON.

2. Scenario
Avvio della procedura

La Node Discovery può essere avviata:

manualmente;
tramite uno scheduler.

L'esecuzione inizia con:

python test_node_discovery.py

Il flusso esegue automaticamente le seguenti operazioni:

identifica il nodo;
acquisisce le informazioni di sistema;
costruisce il modello dati;
verifica la presenza nella CMDB;
registra o aggiorna il nodo;
produce l'output JSON.

Non sono richiesti ulteriori interventi dell'utente.

3. Architettura
Attori
Attore	Responsabilità
Amministratore	Avvia la procedura
Runtime Python	Esegue l'applicazione
Node Discovery	Coordina il flusso
Linux	Fornisce le informazioni di sistema
PostgreSQL	Gestisce la CMDB

Ogni componente opera esclusivamente nel proprio livello di responsabilità.

Componenti
Modulo	Responsabilità
test_node_discovery.py	Punto di ingresso
discovery.py	Orchestrazione
hostname.py	Hostname
ip.py	Indirizzo IP
os.py	Sistema operativo
kernel.py	Kernel
repository.py	Accesso alla CMDB

Ogni modulo implementa una singola responsabilità.

Architettura del caso d'uso
                 Amministratore
                        │
                        ▼
        python test_node_discovery.py
                        │
                        ▼
           test_node_discovery.py
                        │
                        ▼
               discovery.run()
                        │
        ┌───────────────┼────────────────┐
        │               │                │
        ▼               ▼                ▼
  hostname.py       ip.py         os.py / kernel.py
        │               │                │
        └───────────────┼────────────────┘
                        ▼
                 repository.py
                        │
                        ▼
                  PostgreSQL
                        │
                        ▼
                  JSON finale

L'architettura è organizzata in tre livelli:

Discovery, per la raccolta delle informazioni.
Persistence, per la sincronizzazione con la CMDB.
Presentation, per la produzione dell'output JSON.

discovery.py coordina il flusso senza implementare direttamente né la discovery né l'accesso al database.

4. Flusso di esecuzione
Punto di ingresso

L'esecuzione inizia con:

python test_node_discovery.py

Python crea un nuovo processo e carica il modulo principale.

Il file contiene esclusivamente il punto di ingresso:

from common.linux.node_discovery.discovery import run

def main():
    run()

if __name__ == "__main__":
    main()
Importazione della procedura

La prima istruzione importa:

from common.linux.node_discovery.discovery import run

Python carica discovery.py e rende disponibile la funzione run().

Il modulo principale conosce solo l'interfaccia della procedura.

Avvio della discovery

La funzione main() richiama:

run()

Da questo momento il controllo passa completamente a discovery.py.

Ruolo di discovery.py

discovery.py coordina l'intero caso d'uso.

La funzione run():

costruisce il modello dati;
richiama i moduli di discovery;
sincronizza la CMDB;
produce l'output finale.

Non accede direttamente né al sistema operativo né al database.

Flusso della procedura
run()

│
├── hostname.get()
├── ip.get()
├── os.get_name()
├── os.get_version()
├── kernel.get()
├── repository.get_by_hostname()
├── repository.insert() / repository.update()
└── json.dumps() → print()

Ogni funzione implementa una singola responsabilità.

run() coordina esclusivamente il flusso di esecuzione.

Secondo me questa struttura è già molto più vicina a un Software Architecture Document: il lettore segue le macrofasi del sistema (obiettivo → scenario → architettura → esecuzione), invece di attraversare decine di micro-capitoli. I dettagli implementativi rimangono presenti, ma sono organizzati secondo la logica dell'architettura anziché della sequenza delle istruzioni Python.

5. Costruzione del modello dati
Il modello del nodo

La prima attività di run() consiste nella costruzione del modello dati condiviso tra tutti i moduli della procedura.

node = {
    "hostname": hostname.get(),
    "ip_addr": ip.get(),
    "os_name": os.get_name(),
    "os_v": os.get_version(),
    "kernel_v": kernel.get(),
    "status": ""
}

Ogni valore viene ottenuto richiamando un modulo specializzato. Il dizionario node rappresenta il modello dati del caso d'uso e accompagna l'intera procedura, dalla discovery alla sincronizzazione con la CMDB.

Struttura del modello
Campo	Descrizione
hostname	Nome del nodo
ip_addr	Indirizzo IP principale
os_name	Sistema operativo
os_v	Versione del sistema operativo
kernel_v	Versione del kernel
status	Stato della sincronizzazione

Il modello mantiene un formato stabile durante tutta l'esecuzione. I moduli leggono o aggiornano i campi senza modificarne la struttura.

Ordine di costruzione

Le informazioni vengono acquisite nel seguente ordine:

hostname.get()
      ↓
ip.get()
      ↓
os.get_name()
      ↓
os.get_version()
      ↓
kernel.get()

Ogni funzione completa un campo del dizionario fino alla costruzione del modello finale.

Evoluzione del modello

Durante l'esecuzione il contenuto del dizionario cresce progressivamente.

Dopo il recupero dell'hostname:

{
    "hostname": "s1",
    "ip_addr": ...,
    "os_name": ...,
    "os_v": ...,
    "kernel_v": ...,
    "status": ""
}

Dopo il recupero dell'indirizzo IP:

{
    "hostname": "s1",
    "ip_addr": "192.168.200.128",
    "os_name": ...,
    "os_v": ...,
    "kernel_v": ...,
    "status": ""
}

Al termine della discovery:

{
    "hostname": "s1",
    "ip_addr": "192.168.200.128",
    "os_name": "Linux",
    "os_v": "6.8.0-60-generic",
    "kernel_v": "6.8.0-60-generic",
    "status": ""
}

Il modello è ora pronto per la sincronizzazione con la CMDB.

6. Discovery del nodo
Architettura della discovery

La discovery raccoglie le informazioni del sistema operativo attraverso moduli indipendenti.

                 discovery.run()
                        │
        ┌───────────────┼────────────────┐
        │               │                │
        ▼               ▼                ▼
 hostname.py        ip.py        os.py / kernel.py

Ogni modulo implementa una sola responsabilità e restituisce un valore al chiamante. discovery.py coordina il flusso senza conoscere i dettagli implementativi.

Recupero dell'hostname

La procedura richiama:

hostname.get()

Il modulo espone una sola funzione:

def get():
    return socket.gethostname()

Flusso di esecuzione:

discovery.run()
        │
        ▼
hostname.get()
        │
        ▼
socket.gethostname()
        │
        ▼
Sistema Operativo Linux
        │
        ▼
Hostname
        │
        ▼
run()

L'hostname identifica il nodo durante la sincronizzazione con la CMDB.

Recupero dell'indirizzo IP

La procedura richiama:

ip.get()

Il modulo esegue il comando Linux:

output = subprocess.check_output(
    ["hostname", "-I"],
    text=True
).strip()

return output.split()[0]

Flusso di esecuzione:

discovery.run()
        │
        ▼
     ip.get()
        │
        ▼
subprocess.check_output()
        │
        ▼
hostname -I
        │
        ▼
Sistema Operativo Linux
        │
        ▼
Output
        │
        ▼
Python

Il comando può restituire più indirizzi. Il modulo seleziona il primo e lo assegna a node["ip_addr"].

Recupero del sistema operativo

La procedura richiama:

os.get_name()

che utilizza:

platform.system()

per ottenere il nome del sistema operativo.

La versione viene recuperata tramite:

os.get_version()

che richiama:

platform.release()

Entrambi i valori vengono salvati nel modello del nodo.

Recupero della versione del kernel

La procedura richiama:

kernel.get()

Il modulo utilizza la libreria platform per ottenere la versione del kernel e aggiorna node["kernel_v"].

La separazione tra os.py e kernel.py mantiene indipendenti le responsabilità dei moduli, anche se utilizzano la stessa libreria.

Modello dati completato

Al termine della discovery il dizionario contiene tutte le informazioni necessarie alla sincronizzazione.

node = {
    "hostname": "s1",
    "ip_addr": "192.168.200.128",
    "os_name": "Linux",
    "os_v": "6.8.0-60-generic",
    "kernel_v": "6.8.0-60-generic",
    "status": ""
}

La fase successiva verifica la presenza del nodo nella CMDB ed esegue l'operazione di persistenza appropriata.