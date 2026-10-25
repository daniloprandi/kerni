1. Overview & Objectives

This use case defines the telemetry collection mechanism for the Network / Internet Layer (Layer 3) within the Kerni monitoring framework. The primary goal is to programmatically inspect, parse, and persist the Linux kernel's Address Resolution Protocol (ARP) table (/proc/net/arp), enabling continuous mapping of local network neighbors, IP-to-MAC associations, and associated network interfaces for each monitored node.

2. Architecture & Layer Separation

Following Kerni's strict modular, layer-based philosophy, the ARP discovery feature is split into dedicated, single-responsibility components under common/linux/tcp_ip/internet_layer/arp/:

I/O (files/arp_reader.py): Directly interacts with the Linux pseudo-filesystem to retrieve raw text lines from /proc/net/arp.

Parser (parser.py): Sanitizes and structures raw lines into structured Python dictionaries containing normalized attributes (ip_addr, mac_addr, iface, flags).

Inspector (inspector.py): Acts as the orchestration entry point for the module, coordinating I/O reading and data parsing.

Repository (repository.py): Handles transaction management and database persistence, securely inserting records into the PostgreSQL schema.

3. Step-by-Step Execution Workflow

Step 1: Low-Level System Read

Component: common/linux/tcp_ip/internet_layer/arp/files/arp_reader.py

Action: The function read_arp_table() opens /proc/net/arp in read mode and extracts all text lines.

Error Handling: Wrapped in a try-except block to gracefully catch filesystem errors or missing pseudo-files, logging the exception and returning an empty list to prevent daemon crashes.

Step 2: Data Normalization and Parsing

Component: common/linux/tcp_ip/internet_layer/arp/parser.py

Action: The function parse_arp_table(lines) processes the raw text:

Validates that the input contains data beyond the header row.

Splits each line by whitespace columns.

Filters rows to ensure structural validity (minimum column requirements).

Maps raw columns to structured keys: ip_addr (column 0), flags (column 2), mac_addr (column 3), and iface (column 5).

Step 3: Module Orchestration (Inspection)

Component: common/linux/tcp_ip/internet_layer/arp/inspector.py

Action: The function inspect_arp() invokes the reader to fetch raw lines, passes them to the parser, and returns the resulting clean array of ARP records.

Step 4: Database Persistence

Component: common/linux/tcp_ip/internet_layer/arp/repository.py

Action: The function save_arp_data(node_id, arp_records) acquires a shared connection via get_connection(), opens a cursor, and executes batch or iterative INSERT statements into tcpip.arp_table. It handles transaction committing and rolling back in case of SQL failures.

4. Database Schema

Persistence relies on the project-standard PostgreSQL table:

CREATE TABLE IF NOT EXISTS tcpip.arp_table (
    id SERIAL PRIMARY KEY,
    node_id INTEGER NOT NULL,
    ip_addr VARCHAR(45) NOT NULL,
    mac_addr VARCHAR(17) NOT NULL,
    iface VARCHAR(64) NOT NULL,
    flags VARCHAR(32),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


5. Pipeline Integration (node_discovery.py)

The ARP module is integrated into the central orchestrator run(host) function. It executes sequentially right after the Data Link Layer discovery:

  # Discovery del Network / Internet Layer - ARP (Livello 3).
  try:
    arp_records = arp_inspector.inspect_arp()

    arp_repository.save_arp_data(
      node_id,
      arp_records
    )

    print(
      f'ARP table discovered: {len(arp_records)} entries',
      flush=True
    )

  except Exception as error:
    print(
      f'ARP table discovery failed for {host}: {error}',
      flush=True
    )


Fault isolation (try-except) ensures that any runtime interruption during ARP inspection will be caught locally without impacting other telemetry layers or stopping the orchestrator.