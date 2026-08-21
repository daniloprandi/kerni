# Kerni

Kerni is a systems-oriented project built around a simple idea:

> A system that observes a system.

The goal is not only to observe the final behavior of an application, but to descend below the abstractions and understand what happens underneath.

Modern software hides many internal mechanisms behind layers of abstraction.

Kerni explores these layers:

```
Application
    ↓
Web server
    ↓
Application runtime
    ↓
Operating system
    ↓
Linux kernel
    ↓
Network stack
    ↓
System resources
```

The purpose is to make these hidden interactions visible.

---

# Descending below the abstractions

A simple operation such as a network request or a ping is not a single action.

Behind it there are multiple layers:

```
User action
    ↓
Application
    ↓
Python runtime
    ↓
Linux processes
    ↓
System calls
    ↓
Linux kernel
    ↓
Network stack
    ↓
Network interface
```

Kerni tries to follow this path and expose what happens between these layers.

---

# Architecture

Kerni is composed of components that observe different aspects of the operating system.

```
kerni/

├── backend/
│
│   └── node_discovery_api/
│
├── common/
│
│   └── linux/
│       │
│       ├── node_discovery/
│       │
│       └── tcp_ip/
│           │
│           ├── internet_layer/
│           │
│           └── transport_layer/
│
└── database/
```

---

# Node Discovery

Kerni can discover nodes by observing ICMP communication.

Example:

```
Node A
192.168.200.128

        ping

Kerni Node
192.168.200.130
```

The workflow:

```
ICMP packet
      ↓
Linux network stack
      ↓
Linux kernel
      ↓
ICMP listener
      ↓
Source / destination IP
      ↓
Node discovery
      ↓
SSH
      ↓
System information
      ↓
PostgreSQL
```

The discovered information includes:

- hostname
- IP address
- operating system
- kernel version

The observed communication is stored for analysis.

---

# Application stack

Kerni also explores the application execution path.

A request can travel through multiple abstraction layers:

```
HTTP request
      ↓
NGINX
      ↓
Gunicorn
      ↓
Flask application
      ↓
Python runtime
      ↓
Linux process
      ↓
Kernel
```

The objective is understanding what happens underneath each layer.

---

# Technologies

## Application

- Python
- Flask
- Gunicorn

## Infrastructure

- Docker
- Docker Compose
- systemd

## Operating System

- Linux
- SSH
- tcpdump

## Database

- PostgreSQL

---

# Networking

Current areas of observation:

## Internet Layer

- ICMP traffic
- ping detection
- node discovery triggers

## Transport Layer

- TCP connections
- UDP connections
- socket information
- connection states

The objective is to understand how network communication is represented inside Linux.

---

# Philosophy

Kerni is an exploration of the layers normally hidden by abstractions.

Instead of only asking:

```
"What does the application return?"
```

Kerni asks:

```
"What happened before the application returned something?"
```

From:

```
packet
 ↓
kernel
 ↓
process
 ↓
application
 ↓
database
```

the goal is to observe the complete path.

---

# License

Copyright 2026 Danilo Prandi

Licensed under the Apache License, Version 2.0.