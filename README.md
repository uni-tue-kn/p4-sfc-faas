# A Demonstrator for P4-SFC-Based Firewall-as-a-Service with Self-Service Portal Control

The present work is part of a federal project in Baden-Wuerttemberg, called **bwNET2020+**. The project is about strengthening and advancement of the **BelWue** network by examining possibilities to use recent technology advancements in order to achieve better flexibility and performance. Recent technoglogies that are considered here include Software-defined networking (**SDN**), Service Function Virtualization (**SFV**) and Service Function Chaining (**SFC**). Combined with recent advancements in network programmability through **P4**, powerful tools are available that gave rise to interesting possible use cases. The present work demonstrates how to leverage SFC and P4 to build a cloud-like infrastructure to implement the concept of **Firewall as a Service**. A self-service portal will be developed that allows (non-technical) users to easily configure and deploy a firewall for their site.

This repository contains all resources related to the thesis, including documentation,
code and configuration files. The repository is organized as follows.

* <a href="/SFC%20Orchestrator">SFC Orchestrator</a>: The SFC orchestrator places VNFs on hosts and computes paths for SFCs based on SFC configuration provided by customers. It is based on the orchestrator from Stephan Hinselmann.
* <a href="/Self%20Service%20Portal">Self Service Portal</a>: The Self Service Portal is a Webinterface for configuring SFCs in the "bwNETCloud". The frontend is written with Angular 9 and the Backend is based on Python Django. All files related to the Self Service Portal are organized in this folder.
* <a href="/Simulation%20Environment%20(GNS3)">Simulation Environment (GNS3)</a>: Documentation, configuration files and scripts related to the worked out virtual simulation environment / virtual testbed. Graphical Network Simulator (GNS3) is utilized for this purpose. 
* <a href="/P4%20Ingress%20Switch">P4 Ingress Switch</a>: The P4 program that represents data plane implementation of the P4 ingress switch that is part of the P4-SFC architecture.  


## Getting started
In order to run the demonstrator, multiple steps have to be covered. First, the (virtual) testbed has to be set up and configured properly. See <a href="/Simulation%20Environment%20(GNS3)">Simulation Environment (GNS3)</a>
for details. Once the testbed is set up and configured and the present repository is available on the orchestrator, follow these steps to run the demonstrator:

On the P4 ingress switch node, ...
1. run the bmv2 software switch: `sudo simple_switch_grpc --no-p4 -i 0@ens3 -i 1@ens4 -i 2@ens5 -i 3@ens7 --device-id 0 -- -- grpc-server-addr 192.168.123.50:50051`

On the orchestrator node, ...
1. run the keycloak docker container `docker start keycloak`

2. run the backend DRF application. In `/msc-steinert-sfc/Self Service Portal/backend/`, activate venv: `source ./venv/bin/activate`.
 Then, call `python3 manage.py runserver 192.168.122.100:8000`. Remember to set the following IP address correctly before, in file `backend/settings.py`:
    * OIDC_AUTH.'OIDC_ENDPOINT': 'http://CHANGEME:8080/auth/realms/Self%20Service%20Portal'  
    
3. run the frontend Angular application. In `/msc-steinert-sfc/Self Service Portal/frontend/` call `ng serve --host 192.168.122.100 --configuration=dev`.
 Remember to set the IP addresses for Keycloak and the baseApiUrl correctly in `src/environments/environment.dev.ts`.
4. run the orchestrator python program. In `/msc-steinert-sfc/SFC Orchestrator` call `python SFCOrchestrator.py`.
Alternatively, a dockerized version of the SFC Orchestrator is available. To build the image, cd into the folder
`SFC Orchestrator` and run `docker build --tag orchestrator:1.0 .`.
Then, the SFC Orchestrator can be started with `docker run --name sfc-orchestrator orchestrator:1.0`.
For stopping and deleting all containers on all VNF hosts, run `python SFCOrchestrator.py --CLEANUP`.
