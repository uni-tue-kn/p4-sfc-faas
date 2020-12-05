import simplejson
from tabulate import tabulate
import urllib3
import getmac
from inotify.adapters import Inotify
from BMv2Controller import BMv2Controller
from SFFManager import SFFManager
from VNFManager import VNFManager
from SFCProxyManager import SFCProxyManager
from VirtualizationManager import LxdContainerManager, LibvirtVmManager
#from VirtualInfrastructureManager import VirtualInfrastructureManager
from os import environ
from dotenv import load_dotenv
import argparse

load_dotenv()

# Add argument parser to provice a minimal CLI
parser = argparse.ArgumentParser()
parser.add_argument("--CLEANUP", help="Cleanup all Containers and VMs", action='store_true')
args = parser.parse_args()

class SFCOrchestrator:
    _infrastructure_config_path = environ.get('INFRASTRUCTURE_CONFIG_PATH')
    _switch_config_path = environ.get('SWITCH_CONFIG_PATH')
    _sfc_config_directory = environ.get('SFC_CONFIG_DIRECTORY')
    _sfc_config_filename = environ.get('SFC_CONFIG_FILENAME')
    _sfc_config_path = _sfc_config_directory + _sfc_config_filename

    # Hosts have their ID as key (ID = number of host, starting from 1)
    @property
    def hosts(self):
        return self._hosts

    # SFCs have the customer ID as key
    @property
    def sfcs(self):
        return self._sfcs

    @sfcs.setter
    def sfcs(self, value):
        self._sfcs = value

    # List of all requested VNFs
    @property
    def vnfs(self):
        return self._vnfs

    @vnfs.setter
    def vnfs(self, value):
        self._vnfs = value

    @property
    def label_stacks(self):
        return self._label_stacks

    @property
    def label_stacks_backwards(self):
        return self._label_stacks_backwards

    @property
    def switch_config(self):
        return self._switch_config

    def __init__(self):
        self._ingress_switch_controller = None
        self._container_manager = None
        self._vm_manager = None
        self._sff_manager = None
        self._sfc_proxy_manager = None
        self._vnf_manager = None

        # This property holds the computed label stacks for configured SFCs,
        # listed by user ID
        self._label_stacks = {}

        # This property holds the SFCs that have been configured in the Self Service Portal,
        # listed by user ID
        self._sfcs = {}

        # This property holds a list of all currently running VNFs
        self._vnfs = []

    def initialize(self):
        # Supply SFF Manager to administrate SFFs on VNF hosts
        sff_manager = SFFManager()
        if sff_manager is not None:
            self._sff_manager = sff_manager
            print('SFF Manager initialized: ' + str(sff_manager))
        else:
            print('No SFF manager supplied. No SFFs can be managed! Aborting...')
            exit(1)

        # Supply VNF Manager to administrate VNFs on VNF hosts
        vnf_manager = VNFManager()
        if vnf_manager is not None:
            self._vnf_manager = vnf_manager
            print('VNF Manager initialized: ' + str(vnf_manager))
        else:
            print('No VNF manager supplied. VNFs cannot be managed! Aborting...')
            exit(1)

        # Supply SFC Proxy Manager to SFC Proxies on VNF hosts
        sfc_proxy_manager = SFCProxyManager()
        if sfc_proxy_manager is not None:
            self._sfc_proxy_manager = sfc_proxy_manager
            print('SFC Proxy Manager initialized: ' + str(sfc_proxy_manager))
        else:
            print('No SFC Proxy manager supplied. No SFC Proxies can be managed! Aborting...')
            exit(1)

        # Supply Container Manager to create/delete Container on hosts
        container_manager = LxdContainerManager()
        if container_manager is not None:
            self._container_manager = container_manager
            print('Container Manager initialized: ' + str(container_manager))
        else:
            print('No container manager supplied. No Containers can be managed!')

        # Supply VM Manager to create/delete VMs on hosts
        vm_manager = LibvirtVmManager()
        if vm_manager is not None:
            self._vm_manager = vm_manager
            print('VM Manager initialized: ' + str(vm_manager))
        else:
            print('No VM manager supplied. No VMs can be managed!')

        # Read infrastructure config
        print('Reading infrastructure config file ' + str(self._infrastructure_config_path) + ' ...')
        self._hosts = self.read_json_config(file=self._infrastructure_config_path)
        if self.hosts != {}:
            print('Found the following available hosts, listed by host ID:\n {} \n'.format(
                simplejson.dumps(self.hosts, indent=4)))
        else:
            print('No infrastructure configuration given. No hosts to orchestrate - aborting ...')
            exit(1)

        # Read switch config
        print('Reading switch config file ' + str(self._switch_config_path) + ' ...')
        self._switch_config = self.read_json_config(file=self._switch_config_path)
        if self.switch_config != {}:
            print('Found the following switch configuration:\n {} \n'.format(
                simplejson.dumps(self.switch_config, indent=4)))
        else:
            print('No switch configuration given. Dry run. \n')

        ingress_switch_controller = BMv2Controller(
            switch_address=self._switch_config['ingress-switch']['p4runtime_address'],
            p4info_file_path=environ.get('P4INFO_PATH'),
            bmv2_file_path=environ.get('BMV2CONFIG_PATH'))
        if ingress_switch_controller is not None:
            self._ingress_switch_controller = ingress_switch_controller
            self._ingress_switch_controller.initialize()
            print('Ingress switch controller initialized: {} \n'.format(ingress_switch_controller))
        else:
            print('No ingress switch controller supplied. Dry run. \n')


    # Delete all running VMs and Containers
    def cleanup(self):
        for host in self.hosts:
            try:
                # Delete all running containers
                client = self.hosts[host]['lxd_connection']
                running_containers = client.containers.all()
                print('Number of running containers to delete on ' + str(self.hosts[host]['hostname']) + ': ' + str(
                    len(running_containers)))
                if running_containers:
                    for container in running_containers:
                        self._container_manager.delete_virtual_host(client, container.name)
                print('SUCCESS: Deleted all running containers on ' + str(self.hosts[host]['hostname']) + '\n')
            except:
                print("FAILURE! Cleanup was not successful!")
                exit(1)

    # Load configuration in json format and return as dictionary.
    def read_json_config(self, file):
        # Read json infrastructure configuration file
        with open(file, 'r') as file:
            try:
                config = simplejson.loads(file.read())
                file.close()
                return config
            except ValueError as e:
                print('Error occured while parsing file' + str(file) + ': ' +
                      str(e) + ". Aborting... ")
                exit(1)

    # Establish connection to lxd daemon and libvirt hypervisor on each host.
    # Save generated connection object in the 'self.hosts' dictionary
    def establish_connection_to_hosts(self):
        print('Establish connection to hosts:')
        for host in self.hosts:
            libvirt_daemon = self.hosts[host]['hypervisor']
            lxd_daemon = self.hosts[host]['lxd_daemon']

            try:
                if self._container_manager is not None:
                    lxd_connection = self._container_manager.connect(lxd_daemon)
                    self.hosts[host].update({'lxd_connection': lxd_connection})

                if self._vm_manager is not None:
                    libvirt_connection = self._vm_manager.connect(libvirt_daemon)
                    self.hosts[host].update({'libvirt_connection': libvirt_connection})

            except Exception as e:
                print(str(e))
                print('ERROR: Connection to host ' + self.hosts[host]['hostname'] + ' failed!' + '\n')
        print('\n')

    # Execute commands that are necessary on the hosts in order to
    # support MPLS forwarding of packets
    # TODO: Hardcoded MPLS route back to ingress switch
    #def bootstrap_mpls_on_host(self, host_id):
    def bootstrap_SFF(self, host_id):

        self._sff_manager.enable_mpls_kernel_module(self.hosts[host_id]['ip_address'], self.hosts[host_id]['username'])

        # Set MPLS routes to all other VNF hosts/other SFFs
        for host in self.hosts:
            self._sff_manager.write_mpls_forwarding_route(self.hosts[host_id]['ip_address'],
                                                                     self.hosts[host_id]['username'],
                                                                     self.hosts[host]['mpls_label'],
                                                                     self.hosts[host]['ip_address'],
                                                                     self.hosts[host_id]['net_iface_out'])

        # Set MPLS route to ingress switch
        self._sff_manager.write_mpls_forwarding_route(self.hosts[host_id]['ip_address'],
                                                                 self.hosts[host_id]['username'],
                                                                 self.switch_config['ingress-switch']['mpls_label'],
                                                                 self.switch_config['ingress-switch'][
                                                                     'cloud_ip_address'],
                                                                 self.hosts[host_id]['net_iface_out'])

        # Set MPLS route for own label to be delivered locally
        self._sff_manager.write_mpls_local_route(self.hosts[host_id]['ip_address'],
                                                            self.hosts[host_id]['username'],
                                                            self.hosts[host_id]['mpls_label'])

        print('Done bootstrapping. Host is able to deal with MPLS packets now.\n')

    # Get the host that hast most CPU or Memory resources available.
    # A very simple decision is made here that might not be ideal
    def get_least_occupied_host(self):
        max_vcpus = -1
        max_vmem = -1
        candidate = -1

        for host in self.hosts:
            if 'libvirt_connection' in self.hosts[host]:
                connection = self.hosts[host]['libvirt_connection']
                vcpus = connection.getMaxVcpus(None)

                # note: this only gets the free memory, but not the cached memory that can be used
                vmem = int(connection.getFreeMemory() / (1024 * 1024))

                if (vmem > max_vmem) | (vcpus > max_vcpus):
                    candidate = host
                    max_vcpus = vcpus
                    max_vmem = vmem
            else:
                print('ERROR: Libvirt connection to host ' + self.hosts[host]['hostname'] + ' not available!')

        if candidate == -1:
            print('ERROR: No host with libvirt is available for starting VNFs! Aborting... ')
            exit(1)
        return candidate

    # generate MPLS label for a vnf depending on the host and the number of
    # VNFs already running on this host
    def generate_vnf_label(self, host):
        host_label = self.hosts[host]['mpls_label']
        # host_label = self.generate_host_label(host)
        vnf_sequence_number = 0

        # Count how many VNFs are already running on the host.
        # The generated vnf_sequence_number is this value.
        if 'running_vms' in self.hosts[host]:
            vnf_sequence_number += len(self.hosts[host]['running_vms'])
        if 'running_containers' in self.hosts[host]:
            vnf_sequence_number += len(self.hosts[host]['running_containers'])

        vnf_label = int(host_label) + int(vnf_sequence_number)

        occupied_labels = [x['vnf_label'] for x in self.vnfs]
        while vnf_label in occupied_labels:
            print('Label {} already occupied. Try label {}'.format(vnf_label, vnf_label + 1))
            vnf_label += 1

        return vnf_label

    # Generate the backward MPLS label stacks for each SFC
    def generate_label_stacks_backwards(self):
        end_label = self.switch_config['ingress-switch']['mpls_label'] + self.switch_config['ingress-switch'][
            'ingress_port']
        label_stacks_backwards = {}
        for sfc_id in self.sfcs:
            label_stacks_backwards.update({sfc_id: []})
            for vnf_description in reversed(self.sfcs[sfc_id]['vnfs']):
                vnf = [x for x in self.vnfs if x['applicationName'] == vnf_description['applicationName']][0]
                # host_label = self.generate_host_label(vnf['vnf_host'])
                if vnf['bidirectional'] == 'TRUE':
                    host_label = self.hosts[vnf['vnf_host']]['mpls_label']
                    label_stacks_backwards[sfc_id].append(host_label)
                    label_stacks_backwards[sfc_id].append(vnf['vnf_label'])

            label_stacks_backwards[sfc_id].append(self.switch_config['ingress-switch']['mpls_label'])
            label_stacks_backwards[sfc_id].append(end_label)
        return label_stacks_backwards

    # Generate the backwards MPLS label stacks for each SFC
    def generate_label_stacks(self):
        end_label = self.switch_config['ingress-switch']['mpls_label'] + self.switch_config['ingress-switch'][
            'egress_port']
        label_stacks = {}
        for sfc_id in self.sfcs:
            label_stacks.update({sfc_id: []})
            for vnf_description in self.sfcs[sfc_id]['vnfs']:
                vnf = [x for x in self.vnfs if x['applicationName'] == vnf_description['applicationName']][0]
                # host_label = self.generate_host_label(vnf['vnf_host'])
                host_label = self.hosts[vnf['vnf_host']]['mpls_label']
                label_stacks[sfc_id].append(host_label)
                label_stacks[sfc_id].append(vnf['vnf_label'])
            label_stacks[sfc_id].append(self.switch_config['ingress-switch']['mpls_label'])
            label_stacks[sfc_id].append(end_label)
        return label_stacks

    # Watch SFC config file and react to changes in the SFC configuration json file,
    # e.g., newly added VNFs or removed VNFs
    def watch(self):
        print("--- Orchestator mode engaged. Watching for changes in SFC configuration at " + str(
            self._sfc_config_directory))
        i = Inotify()
        i.add_watch(str(self._sfc_config_directory))

        for event in i.event_gen(yield_nones=False):
            (_, type_name, path, filename) = event

            # if changes have been written to the file
            if 'IN_CLOSE_WRITE' in type_name and self._sfc_config_filename == filename:
                print("Write-event to {}{} registered {}, reevaluating...\n".format(path, filename, type_name))

                new_sfcs = self.read_json_config(file=self._sfc_config_path)
                print('New SFCs: {}\n'.format(simplejson.dumps(new_sfcs, indent=4)))

                deleted_sfcs = [x for x in self.sfcs if x not in new_sfcs]

                for sfc_id in deleted_sfcs:
                    print('Delete SFC {}:'.format(sfc_id))

                    if '/' in str(self.sfcs[sfc_id]['trafficType']['ipAddress']):
                        split = str(self.sfcs[sfc_id]['trafficType']['ipAddress']).split('/')
                        ip_address = split[0]
                        prefix_length = split[1]
                    else:
                        print('Traffic destination IP given without prefix! Aborting...')
                        exit(1)

                    # Traffic from customer
                    self._ingress_switch_controller.delete_mpls_sr_rule(self._label_stacks[sfc_id], 'src', ip_address,
                                                                       prefix_length)

                    label_stacks_backwards = self.generate_label_stacks_backwards()
                    # Traffic to customer
                    self._ingress_switch_controller.delete_mpls_sr_rule(label_stacks_backwards[sfc_id], 'dst',
                                                                       ip_address,
                                                                       prefix_length)

                self.apply_sfc_policies(new_sfcs)

                print("----- Orchestator mode engaged. Watching for changes in SFC configuration at {} ----- ".format(
                    self._sfc_config_directory))

    def get_ip_from_host_id(self, host):
        return str(self.hosts[host]['lxd_connection'].networks.get('lxdbr0').config['ipv4.address']).split('/')[0]

    # print an accessible status summary of all running VNFs and active SFCs
    def print_status_summary(self):

        # print status information of hosts
        column_headers = ["HOSTNAME", "RUNNING_CONTAINERS", "RUNNING_VMS", "MPLS_LABEL"]
        data = []

        for host in self.hosts:
            host_label = self.hosts[host]['mpls_label']
            # host_label = self.generate_host_label(host)
            if 'running_containers' in self.hosts[host]:
                if 'running_vms' in self.hosts[host]:
                    row_data = [str(self.hosts[host]['hostname']), str(self.hosts[host]['running_containers']),
                                str(self.hosts[host]['running_vms']), str(host_label)]
                else:
                    row_data = [str(self.hosts[host]['hostname']), str(self.hosts[host]['running_containers']), '[ ]', str(host_label)]
            else:
                row_data = [str(self.hosts[host]['hostname']), '[ ]', '[ ]', str(host_label)]
            row_data = [x.encode('utf-8') for x in row_data]
            data.append(row_data)

        print('\n | Host status summary: ')
        print(tabulate(data, headers=column_headers, tablefmt='grid') + '\n')

        # print status information of customers SFCs
        column_headers = ["CUSTOMER", "SERVICE FUNCTION CHAIN", "LABEL_STACK"]
        data = []

        for sfc_id in self.sfcs:
            row_data = [self.sfcs[sfc_id]['owner'].encode('utf-8'), [x['applicationName'].encode('utf-8') for x in self.sfcs[sfc_id]['vnfs']],
                         self.label_stacks[sfc_id]]
            data.append(row_data)

        # for customer in self.sfcs:
        #    row_data = [customer, [x['applicationName'] for x in self.sfcs[customer]], self.label_stacks[customer]]
        #    data.append(row_data)

        print('\n | Customer status summary: ')
        print(tabulate(data, headers=column_headers, tablefmt='grid') + '\n')

        # print status information of running VNFs
        column_headers = ["VNF", "MPLS_LABEL", "BIDIRECTIONAL?","IP ADDRESS", "OWNER"]
        data = []

        for vnf in self.vnfs:
            row_data = [vnf['applicationName'], vnf['vnf_label'], vnf['bidirectional'], vnf['ip_address'], vnf['owner']]
            data.append(row_data)

        print('\n | VNFs status summary: ')
        print(tabulate(data, headers=column_headers, tablefmt='grid') + '\n')

    # Apply the SFCs that are requested in the sfc_config
    def apply_sfc_policies(self, new_sfcs_config):
        # The sfc policy file does not need to be validated because it is generated by the
        # backend of the self-service portal
        self.sfcs = new_sfcs_config

        # Generate unordered list of all requested VNFs, independent of customer
        new_vnfs = []
        for sfc_id in self.sfcs:
            for vnf in self.sfcs[sfc_id]['vnfs']:
                new_vnfs.append(vnf)

        old_vnfs_names = [x['applicationName'] for x in self.vnfs]
        new_vnfs_names = [x['applicationName'] for x in new_vnfs]

        # Find out delta between new_vnfs_names and old_vnfs_names
        deleted_vnfs = [x for x in self.vnfs if x['applicationName'] not in new_vnfs_names]
        added_vnfs = [x for x in new_vnfs if x['applicationName'] not in old_vnfs_names]

        # Handle deleted VNFs
        for vnf in deleted_vnfs:
            print('Delete VNF {}'.format(vnf['applicationName']))
            self._vnf_manager.destroy_vnf(vnf, self.hosts[vnf['vnf_host']])
            # Delete VNF from local 'host' dict
            self.hosts[vnf['vnf_host']]['running_containers'] = [x for x in
                                                                 self.hosts[vnf['vnf_host']]['running_containers']
                                                                 if x != vnf['applicationName']]
            self._sff_manager.remove_mpls_label_route(self.hosts[vnf['vnf_host']]['ip_address'],
                                                                 self.hosts[vnf['vnf_host']]['username'],
                                                                 vnf['vnf_label'])
            self.vnfs.remove(vnf)

        # Handle added VNFs
        for vnf in added_vnfs:
            print('Launch VNF with ID {} with applicationName={}:'.format(vnf['id'], vnf['applicationName']))
            vnf_host = self.get_least_occupied_host()
            self._vnf_manager.launch_vnf(vnf, self.hosts[vnf_host])

            # Store the container in the hosts dictionary under "running_containers".
            # This helps to keep track of which Containers are running on which hosts
            if 'running_containers' in self.hosts[vnf_host]:
                self.hosts[vnf_host]['running_containers'].append(vnf['applicationName'])
            else:
                self.hosts[vnf_host].update({"running_containers": [vnf['applicationName']]})
            # Store the vnf host ID directly in the VNF, so that it is clear on which host the VNF is running
            vnf.update({"vnf_host": vnf_host})

            # Store the VNF MPLS label directly in the VNF
            vnf_label = self.generate_vnf_label(vnf_host)
            vnf.update({"vnf_label": vnf_label})

            # Store the VNF IP address directly in the VNF
            vnf_host_container_ip = self._container_manager.get_host_ip(self.hosts[vnf['vnf_host']]['lxd_connection'], vnf['applicationName'])
            vnf.update({"ip_address": vnf_host_container_ip})
            self.vnfs.append(vnf)

        # Generate the new label stacks
        self._label_stacks = self.generate_label_stacks()
        self._label_stacks_backwards = self.generate_label_stacks_backwards()

        # Populate the encapsulation rules to ingress switch
        if self._ingress_switch_controller is not None:
            # Write table rules for each SFC to ingress switch
            for sfc_id in self.sfcs:
                if '/' in str(self.sfcs[sfc_id]['trafficType']['ipAddress']):
                    split = str(self.sfcs[sfc_id]['trafficType']['ipAddress']).split('/')
                    ip_address = split[0]
                    prefix_length = split[1]
                else:
                    print('Traffic destination IP given without prefix! Aborting...')
                    exit(1)

                # Traffic from customer
                self._ingress_switch_controller.write_mpls_sr_rule(self._label_stacks[sfc_id], 'src', ip_address,
                                                                   prefix_length)

                # Traffic to customer
                self._ingress_switch_controller.write_mpls_sr_rule(self._label_stacks_backwards[sfc_id], 'dst', ip_address,
                                                                   prefix_length)
        else:
            print('No ingress switch controller supplied. Dry run.\n')

        # Populate MPLS routes to SFFs on VNF hosts and to VNF Proxies
        for vnf in self.vnfs:
            self._sff_manager.write_mpls_pop_label_route(self.hosts[vnf['vnf_host']]['ip_address'],
                                                                    self.hosts[vnf['vnf_host']]['username'],
                                                                    vnf['vnf_label'],
                                                                    vnf['ip_address'],
                                                                    'lxdbr0')  # TODO: HARDCODED NETWORK INTERFACE

            # TODO: NOT GOOD! CHANGE THE WAY TO GET SFC_ID. Might be available when using proper relations within the
            # VNF & SFC data models instead of string representations.
            correspondingSFC = -1
            # get SFC ID by VNF
            for sfcID in self.sfcs:
                if vnf['applicationName'] in str(self.sfcs[sfcID]['vnfs']):
                    correspondingSFC = sfcID
            if correspondingSFC == -1:
                print('No corresponding SFC has been found!!! Abort...')
                exit(1)

            self._sfc_proxy_manager.lxc_configure_sfc_proxy_mpls(self.hosts[vnf['vnf_host']]['ip_address'],
                                                                      self.hosts[vnf['vnf_host']]['username'],
                                                                      self.get_ip_from_host_id(vnf['vnf_host']),
                                                                      self.label_stacks[correspondingSFC],
                                                                      vnf['applicationName'],
                                                                      vnf['vnf_label'])

            if vnf['bidirectional'] == 'TRUE':
                self._sfc_proxy_manager.lxc_configure_sfc_proxy_mpls_backwards(
                    self.hosts[vnf['vnf_host']]['ip_address'],
                    self.hosts[vnf['vnf_host']]['username'],
                    self.get_ip_from_host_id(vnf['vnf_host']),
                    self._label_stacks_backwards[correspondingSFC],
                    vnf['applicationName'],
                    vnf['vnf_label'],
                    self.sfcs[correspondingSFC]['trafficType']['ipAddress'])

        self.print_status_summary()

    # Write static MPLS rules to ingress-switch and SFFs
    def write_static_mpls_rules(self):
        # Write forwarding rules to hosts with their respecitve mpls label and MAC address
        # for host in vnforchestrator.hosts:
        if self._ingress_switch_controller is not None:

            print('Write static MPLS rules to ingress switch:')

            # TODO: Hardcoded IPs
            # self._ingress_switch_controller.write_ipv4_lpm_rule('20.20.20.0', 24,
            #                                                     self.switch_config["ingress-switch"]
            #                                                     ["egress_nexthop"],
            #                                                     self.switch_config["ingress-switch"]
            #                                                     ["egress_port"])

            self._ingress_switch_controller.write_default_ipv4_lpm_rule(self.switch_config["ingress-switch"]
                                                                 ["egress_nexthop"],
                                                                 self.switch_config["ingress-switch"]
                                                                 ["egress_port"])

            self._ingress_switch_controller.write_ipv4_lpm_rule('10.10.10.0', 24,
                                                                self.switch_config["ingress-switch"]
                                                                ["ingress_nexthop"],
                                                                self.switch_config["ingress-switch"]
                                                                ["ingress_port"])


            # TODO: Hardcoded End Labels
            self._ingress_switch_controller.write_mpls_finish_rule(51, self.switch_config['ingress-switch']
            ['ingress_port'])
            self._ingress_switch_controller.write_mpls_finish_rule(52, self.switch_config['ingress-switch']
            ['egress_port'])

            for host in self.hosts:
                host_label = self.hosts[host]['mpls_label']
                self._ingress_switch_controller.write_mpls_forward_rule(host_label,
                                                                        str(self.hosts[host]['MAC_address']),
                                                                        self.switch_config['ingress-switch']
                                                                        ["cloud_port"])
            print('\n')

        for host in self.hosts:
            print('Write static MPLS rules to host {}:'.format(host))
            self.bootstrap_SFF(host)

    # If SFC config is present already, read and apply.
    # Otherwise, watch and orchestrate changes in the SFC config.
    def orchestrate(self):
        print('Read SFC config file ' + str(self._sfc_config_path) + ' ...')
        sfcs_config = self.read_json_config(file=self._sfc_config_path)

        if sfcs_config != {}:
            print('SFC Configuration found. Requested SFCs, listed by ID:\n {}\n'.format(simplejson.dumps(sfcs_config, indent=4)))
            self.apply_sfc_policies(sfcs_config)
        else:
            print('No SFCs configured yet.\n')

        # Watch SFC configuration for changes and react to changes
        self.watch()

def main():
    # Certificates are self signed, therefore disable warning.
    urllib3.disable_warnings()

    # Initialize SFCOrchestrator and load configuration.
    orchestrator = SFCOrchestrator()
    orchestrator.initialize()
    # Establish connections to configured hosts.
    orchestrator.establish_connection_to_hosts()

    if args.CLEANUP:
        print('----- Starting CLEANUP phase -----' + '\n')
        orchestrator.cleanup()
        print('----- Finishing CLEANUP phase -----')
    else:
        orchestrator.write_static_mpls_rules()

        # Read and watch the SFC policy file and apply policies
        orchestrator.orchestrate()

if __name__ == '__main__':
    main()
