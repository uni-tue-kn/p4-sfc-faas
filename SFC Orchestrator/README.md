# SFC Orchestrator

The SFC orchestrator is written in Python and places VNFs on hosts and computes paths for SFCs based on SFC configuration
 provided by customers. It is based on the orchestrator from Stephan Hinselmann but underwent a major refactoring and was 
partially redesigned for better usability and accessibility.

# Controller - P4 Runtime
In order to use the P4Runtime, instead of the "simple_switch", the "simple_switch_grpc"
has to be used. Instructions on how to install and use the simple_switch_grpc can be
found here: https://github.com/p4lang/behavioral-model/tree/master/targets/simple_switch_grpc

Important commands in a nutshell:

build and install PI (https://github.com/p4lang/PI): 

	./autogen.sh && ./configure --with-proto --without-internal-rpc --without-cli --without-bmv2 && make && sudo make install && sudo ldconfig

build bmv2 (https://github.com/p4lang/behavioral-model): 

	./autogen.sh && ./configure --with-pi && make

build simple_switch_grpc (https://github.com/p4lang/behavioral-model/tree/master/targets/simple_switch_grpc): 

	cd targets/simple_switch_grpc && ./autogen.sh && ./configure && make

compile p4 program so that P4Runtime can use it:

    p4c -b bmv2 --p4runtime-files ingress-switch.p4info.txt ingress-switch.p4 -o ingress-switch.bmv2
    
start simple_switch_grpc:

    sudo simple_switch_grpc --no-p4 -i 0@ens3 -i 1@ens4 -i 2@ens5 -- --grpc-server-addr 127.0.0.1:50051

start controller:

    python ./controller/bmv2-controller/controller.py --p4info ~/msc-steinert-sfc/Simulation\ Environment\ \(GNS3\)/P4\ Software\ Switch\ BMv2/ingress-switch.p4info.txt --bmv2-json ~/msc-steinert-sfc/Simulation\ Environment\ \(GNS3\)/P4\ Software\ Switch\ BMv2/ingress-switch.bmv2/ingress-switch.json

## Refactoring
This section documents problematic parts in the given implementation, reasons for refactoring and proposed/implemented changes.

---
* Issue: To enable starting of configured VNFS within a container, the container template needs to be configured appropriately and 
multiple manual configuration steps are necessary (entry in /etc/fstab, entry in /etc/exports, creation of systemd service file).
This process is not very accessible I could not even get it to work without the preconfigured container template.
* Implemented Solution: Changed "Launch services" phase. Now, the VNF scripts are copied to the running container and started with the pylxd library.
This reduces the number of manual configuration steps to **zero** and removes the dependency on NFS.
---
* Issue: A lot of connections are opened for interaction with the containers/VMs.
* Implemented Solution: Maintain connections to containers/VMs to reuse them instead of opening a new
connection for every operation.
--- 
* Issue: Code seems to be messy and not easily understandable/usable.
* Proposed solution: Change architecture of orchestrator from script-based to object-oriented.
---
* Issue: Configuration of the orchestrator is scattered around in the code with hardcoded values
for directory paths, IP addresses etc.
* Proposed solution: Configuration of variable values should be possible in one place, e.g. via a .env file or
via command-line parameters. The following values should be configurable:
    
    * Infrastructure information (which/how many hosts)
    * P4 Switch address
    * RSA keys for connecting with the hosts
    * SFC configuration file
---
* Issue: Data-plane control is done manually and seperate from the orchestrator.
* Implemented solution: Data-plane control is performed automatically by the orchestrator, i.e. configuration
of the P4 ingress switch, depending on the configured SFCs.
---
* Issue: Data is scattered around in different lists, that are accessed by an index depending on the host.
The host/VNF mapping is done in a complicated and error-prone way.
* Proposed solution: Hold all the important data in one place (dictionary) where it is easily available
and the host/VNF mapping is clear and easily accessible.

