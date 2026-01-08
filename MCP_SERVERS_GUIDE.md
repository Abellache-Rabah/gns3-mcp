# MCP Servers & Shared Folder Guide
# Guide des Serveurs MCP et Dossier Partagé

---

## 🇬🇧 English Version

### 1. Overview
This project consists of 7 **Model Context Protocol (MCP)** servers that effectively act as a "Network Team" for an AI agent. Each server handles a specific domain of network engineering. There is also a `shared` folder containing common utilities and the source of truth.

### 2. The Servers

#### **Auditor** (Security)
*   **What it does:** Performs security compliance checks and vulnerability scanning.
*   **How it works:**
    *   **Compliance:** Checks device configurations against a set of "Golden Rules" (e.g., "passwords must be encrypted", "HTTP server disabled").
    *   **Vulnerabilities:** Simulates a CVE database lookup to check if a specific OS version has known security flaws.
    *   **Tools:** `check_compliance`, `scan_vulnerabilities`.

#### **Deployer** (Execution)
*   **What it does:** Deploys configurations to network devices and allows for rollbacks.
*   **How it works:**
    *   **Connection:** Uses the `shared` library to open Telnet connections to GNS3 routers (or Linux hosts).
    *   **Logic:** Can calculate diffs between running and candidate configs locally before deploying. Supports a `dry_run` mode to preview changes.
    *   **Tools:** `deploy_config` (simulates or real push via Telnet), `get_config_diff`, `rollback`.

#### **IPAM** (IP Address Management)
*   **What it does:** Manages IP addresses and subnets.
*   **How it works:**
    *   **Storage:** Maintains an internal registry (simulated database) of subnets and assigned IP addresses.
    *   **Logic:** Calculates subnet utilization and finds the next available IP for allocation.
    *   **Tools:** `allocate_ip`, `get_subnet_usage`, `list_subnets`.

#### **Librarian** (Knowledge Base)
*   **What it does:** Acts as the single Source of Truth (SoT) and documentation center.
*   **How it works:**
    *   **Inventory:** Reads `shared/inventory.yaml` to provide device details.
    *   **Topology:** Reads `shared/topology_physical.yaml` to provide the physical cabling map.
    *   **RAG:** Performs keyword-based search on a mock internal documentation database (e.g., "OSPF Config Guide", "Link Failure SOP").
    *   **Tools:** `search_docs`, `get_device_info`, `list_devices`.

#### **Observer** (Monitoring)
*   **What it does:** Monitors the live state of the network.
*   **How it works:**
    *   **Live Check:** Connects to devices (via Telnet/SSH) to run commands like `ping` or `show ip interface brief`.
    *   **Validation:** Parses raw CLI output into structured data to determine if interfaces are UP or DOWN.
    *   **Tools:** `check_reachability` (ping tests), `get_interface_health` (status/protocol check), `detect_link_failures`.

#### **TrafficGen** (Validation)
*   **What it does:** Simulates and measures network traffic.
*   **How it works:**
    *   **Simulation:** Mocks the behavior of tools like `iperf3`. In a real scenario, it would SSH into a source client and a target server to run bandwidth tests.
    *   **Logic:** Returns success/failure logic based on verified bandwidth capability.
    *   **Tools:** `start_traffic_server`, `run_traffic_test` (client side).

#### **Verifier** (Design & Analysis)
*   **What it does:** Statically analyzes configurations **before** they are deployed.
*   **How it works:**
    *   **Batfish:** Connects to a Batfish service to parse vendor-specific configurations (Cisco, Juniper, etc.) and check for syntax errors or undefined references.
    *   **Host Validation:** Validates Linux `netplan` or interface files using syntactical checks.
    *   **Tools:** `verify_device_config` (uses Batfish), `verify_host_config`.

### 3. The Shared Folder (`shared/`)
This folder acts as the "Glue" layer for the ecosystem. It contains:

*   **`gns3_utils.py`**: A Python library used by `Deployer` and `Observer`. It handles the low-level socket/Telnet communication with the GNS3 simulation nodes, abstracting away the complexity of connecting to `localhost` ports.
*   **`inventory.yaml`**: The **Logical Inventory**. It defines which devices exist, their management IP/Port (for GNS3), and their groups (e.g., `cisco_ios`, `linux`).
*   **`topology_physical.yaml`**: The **Physical Topology** (Ground Truth). It defines how devices are actually cabled together (Device A Port X <-> Device B Port Y).

---

## 🇫🇷 Version Française

### 1. Vue d'ensemble
Ce projet se compose de 7 serveurs **Model Context Protocol (MCP)** qui agissent ensemble comme une "Équipe Réseau" pour un agent IA. Chaque serveur gère un domaine spécifique de l'ingénierie réseau. Il y a aussi un dossier `shared` (partagé) contenant des utilitaires communs et la source de vérité.

### 2. Les Serveurs

#### **Auditor** (Sécurité)
*   **Ce qu'il fait :** Effectue des vérifications de conformité de sécurité et des scans de vulnérabilités.
*   **Comment ça marche :**
    *   **Conformité :** Vérifie les configurations des équipements par rapport à des "Règles d'Or" (ex: "les mots de passe doivent être chiffrés").
    *   **Vulnérabilités :** Simule une recherche dans une base CVE pour voir si une version d'OS a des failles connues.
    *   **Outils :** `check_compliance` (vérifier conformité), `scan_vulnerabilities` (scanner vulnérabilités).

#### **Deployer** (Déploiement)
*   **Ce qu'il fait :** Déploie les configurations sur les équipements et permet les retours en arrière (rollback).
*   **Comment ça marche :**
    *   **Connexion :** Utilise la librairie `shared` pour ouvrir des connexions Telnet vers les routeurs GNS3.
    *   **Logique :** Calcule les différences ("diffs") entre la configuration actuelle et la nouvelle avant de déployer. Permet un mode `dry_run` pour prévisualiser.
    *   **Outils :** `deploy_config` (pousse la config), `get_config_diff`, `rollback`.

#### **IPAM** (Gestion des Adresses IP)
*   **Ce qu'il fait :** Gère les adresses IP et les sous-réseaux.
*   **Comment ça marche :**
    *   **Stockage :** Maintient un registre interne (base de données simulée) de sous-réseaux et d'IP assignées.
    *   **Logique :** Calcule l'utilisation des sous-réseaux et trouve la prochaine IP disponible.
    *   **Outils :** `allocate_ip` (allouer IP), `get_subnet_usage`, `list_subnets`.

#### **Librarian** (Base de Connaissances)
*   **Ce qu'il fait :** Agit comme Source de Vérité (SoT) et centre de documentation.
*   **Comment ça marche :**
    *   **Inventaire :** Lit `shared/inventory.yaml` pour fournir les détails des équipements.
    *   **Topologie :** Lit `shared/topology_physical.yaml` pour fournir le plan de câblage physique.
    *   **RAG :** Effectue une recherche par mots-clés dans une base documentaire interne simulée (ex: "Guide OSPF").
    *   **Outils :** `search_docs` (chercher doc), `get_device_info`, `list_devices`.

#### **Observer** (Monitoring)
*   **Ce qu'il fait :** Surveille l'état réel du réseau.
*   **Comment ça marche :**
    *   **Vérification Live :** Se connecte aux équipements (Telnet/SSH) pour lancer des commandes comme `ping` ou `show ip interface brief`.
    *   **Validation :** Analyse la sortie CLI pour déterminer si les interfaces sont "UP" ou "DOWN".
    *   **Outils :** `check_reachability` (test de ping), `get_interface_health` (santé d'interface), `detect_link_failures`.

#### **TrafficGen** (Génération de Trafic)
*   **Ce qu'il fait :** Simule et mesure du trafic réseau.
*   **Comment ça marche :**
    *   **Simulation :** Imite le comportement d'outils comme `iperf3`. Dans un scénario réel, il se connecterait en SSH pour lancer des tests de bande passante.
    *   **Logique :** Retourne un succès ou échec basé sur la capacité vérifiée.
    *   **Outils :** `start_traffic_server`, `run_traffic_test`.

#### **Verifier** (Design & Analyse)
*   **Ce qu'il fait :** Analyse statiquement les configurations **avant** qu'elles ne soient déployées.
*   **Comment ça marche :**
    *   **Batfish :** Se connecte à un service Batfish pour parser les configurations (Cisco, Juniper, etc.) et vérifier les erreurs de syntaxe.
    *   **Validation Hôte :** Valide les fichiers `netplan` ou interfaces Linux.
    *   **Outils :** `verify_device_config` (via Batfish), `verify_host_config`.

### 3. Le Dossier Partagé (`shared/`)
Ce dossier sert de "colle" pour l'écosystème. Il contient :

*   **`gns3_utils.py`** : Une librairie Python utilisée par `Deployer` et `Observer`. Elle gère la communication bas-niveau (socket/Telnet) avec les nœuds GNS3, masquant la complexité des ports `localhost`.
*   **`inventory.yaml`** : L'**Inventaire Logique**. Il définit quels appareils existent, leurs IP/Ports de gestion, et leurs groupes.
*   **`topology_physical.yaml`** : La **Topologie Physique**. Elle définit comment les appareils sont physiquement câblés (Appareil A Port X <-> Appareil B Port Y).
