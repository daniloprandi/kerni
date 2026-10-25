1. Overview & Objectives

This use case defines the telemetry collection mechanism for the Application Layer and System Management (Layer 7) within the Kerni monitoring framework. The primary goal is to programmatically inspect, parse, and persist the state of all system units managed by systemd on monitored Linux nodes, providing full-stack visibility into active daemons, databases, network services, and operational utilities.

2. Architecture & Layer Separation

Following Kerni's strict modular, layer-based philosophy, the systemd discovery feature is split into dedicated, single-responsibility components under common/linux/application_layer/systemd/:

I/O (files/systemd_reader.py): Interacts with the operating system initialization subsystem by safely executing the native systemctl command to retrieve raw unit listings.

Parser (parser.py): Sanitizes and structures raw text lines into normalized Python dictionaries containing attributes such as unit, load_state, active_state, sub_state, and description.

Inspector (inspector.py): Acts as the orchestration entry point for the module, coordinating I/O reading and data parsing.

Repository (repository.py): Handles transaction management and database persistence, securely inserting records into the PostgreSQL schema dedicated to application telemetry.

3. Step-by-Step Execution Workflow

Step 1: Low-Level System Read

Component: common/linux/application_layer/systemd/files/systemd_reader.py

Action: Executes the systemctl command via Python's subprocess module:

subprocess.run([
    'systemctl',
    'list-units',
    '--type=service',
    '--all',
    '--no-pager',
    '--no-legend'
], capture_output=True, text=True, check=True)


Error Handling: Wrapped in a try-except block to gracefully handle command failures, logging the exception and returning an empty list to prevent daemon crashes.

Step 2: Data Normalization and Parsing

Component: common/linux/application_layer/systemd/parser.py

Action: The function parse_systemd_services(lines) processes the raw output:

Iterates through each line of the systemctl output.

Splits the row into columns to extract key attributes: unit, load_state, active_state, sub_state, and description.

Validates structural integrity before appending records to the clean output list.

Step 3: Module Orchestration (Inspection)

Component: common/linux/application_layer/systemd/inspector.py

Action: The function inspect_systemd() invokes the reader to fetch raw output and passes it to the parser, returning the final structured collection of service records.

Step 4: Database Persistence

Component: common/linux/application_layer/systemd/repository.py

Action: The function save_systemd_services(node_id, services) acquires a shared connection via get_connection(), opens a cursor, and executes batch or iterative INSERT statements into application.systemd_services. It manages transactions with automatic commit and rollback on failure.

4. Database Schema

Persistence relies on the project-standard PostgreSQL schema and table:

CREATE SCHEMA IF NOT EXISTS application;

CREATE TABLE IF NOT EXISTS application.systemd_services (
    id SERIAL PRIMARY KEY,
    node_id INTEGER NOT NULL,
    unit VARCHAR(255) NOT NULL,
    load_state VARCHAR(64),
    active_state VARCHAR(64),
    sub_state VARCHAR(64),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


5. Pipeline Integration (node_discovery.py)

The systemd module is integrated into the central orchestrator run(host) function as the final step of the node discovery pipeline:

  # Discovery dell'Application Layer - Systemd Services (Livello 7).
  try:
    systemd_records = systemd_inspector.inspect_systemd()

    systemd_repository.save_systemd_services(
      node_id,
      systemd_records
    )

    print(
      f'Systemd services discovered: {len(systemd_records)} units',
      flush=True
    )

  except Exception as error:
    print(
      f'Systemd services discovery failed for {host}: {error}',
      flush=True
    )