from VirtualizationManager import LxdContainerManager
from VirtualizationManager import LibvirtVmManager
import simplejson
from os import environ
from dotenv import load_dotenv

class VNFManager:
    _lxd_config_path = environ.get('LXD_CONFIG_PATH')

    def __init__(self):
        self._container_manager = LxdContainerManager()
        self._vm_manager = LibvirtVmManager()

    # TODO ! FIX CHAIN AND GENERALLY IMPROVE THIS METHOD!
    def generate_firewall_script(self, firewallRules):

        script_string = '#!/bin/bash \n'

        for rule in firewallRules:
            # parse direction
            if rule['direction'] == 'IN':
                chain = 'FORWARD'
            elif rule['direction'] == 'OUT':
                chain = 'FORWARD'
            else:
                chain = 'FORWARD'

            # parse protocol
            if rule['protocol'] == 'TCP':
                protocol = 'tcp'
            elif rule['protocol'] == 'UDP':
                protocol = 'udp'
            elif rule['protocol'] == 'ICMP':
                protocol = 'icmp'

            dport = rule['port']

            if rule['policy'] == 'ALLOW':
                policy = 'ACCEPT'
            else:
                policy = 'DROP'

            if (protocol == 'tcp') | (protocol == 'udp'):
                rule_string = 'iptables -A {} -p {} --dport {} -j {} \n'.format(chain, protocol, dport, policy)
            elif protocol == 'icmp':
                rule_string = 'iptables -A {} -p {} -j {} \n'.format(chain, protocol, policy)
            script_string += rule_string

        return script_string

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

    # Launch virtualized host (container or VM) that runs the VNF
    def launch_vnf_host(self, vnf, host):

        print('Launch virtualizated VNF host {} on host {} ... '.format(vnf['virtualization'],
                                                                        host['hostname'])),

        if vnf['virtualization'] == "container":

            # Adjust container configuration
            lxd_config = self.read_json_config(self._lxd_config_path)
            lxd_config['config']['limits.cpu'] = str(vnf['vcpus'])
            lxd_config['config']['limits.memory'] = str(vnf['vmemory']) + "GB"

            # Start Container
            success = self._container_manager.create_virtual_host(host['lxd_connection'], lxd_config,
                                                                  vnf['applicationName'])
            if success:
                print('DONE.')
            else:
                print('Failed to create Container <' + vnf['applicationName'] + '> on host ' + str(
                    host['hostname'] + "! Aborting ..."))
                exit(1)

        elif vnf['virtualization'] == 'vm':
            print('ERROR: VM Virtualization is not supported yet. Aborting ...')
            exit(1)

    # Launch VNF in a virtualized host (container or VM)
    # as systemd service
    def launch_vnf(self, vnf, host):
        # Set filenames and paths of the VNF bash script and the VNF service file
        vnf_script_string = 'VNFs/' + vnf['serviceType'] + '/' + vnf['serviceType'] + '.sh'
        vnf_script = open(vnf_script_string).read()
        vnf_service_file_string = 'VNFs/' + vnf['serviceType'] + '/' + vnf['serviceType'] + '.service'
        vnf_service_file = open(vnf_service_file_string).read()

        # launch vnf host
        self.launch_vnf_host(vnf, host)

        # prepare VNF scripts depending on type of VNF
        if vnf['serviceType'] == 'firewall':
            vnf_script = self.generate_firewall_script(vnf['firewallRules'])

        if vnf['virtualization'] == 'container':
            # Get running container
            lxd_connection = host['lxd_connection']
            vnf_host_container = lxd_connection.containers.get(vnf['applicationName'])
            vnf_host_container_ip = self._container_manager.get_host_ip(lxd_connection, vnf['applicationName'])

            print('Uploading VNF script file ' + vnf_script_string + ' to container ' + vnf[
                'applicationName'] + ':/opt/' + str(vnf['serviceType']) + '.sh ...'),

            vnf_host_container.files.put('/opt/' + vnf['serviceType'] + '.sh', vnf_script)

            vnf_host_container.execute(['chmod', '+x', '/opt/' + vnf['serviceType'] + '.sh'])
            print('DONE.')

            print('Uploading systemd service file ' + vnf_service_file_string + ' to container ' + vnf[
                'applicationName'] + ':/etc/systemd/system/' + str(
                vnf['serviceType']) + '.service ...'),
            vnf_host_container.files.put('/etc/systemd/system/' + vnf['serviceType'] + '.service',
                                         vnf_service_file)  # This is an Ubunutu specific path for service files!
            print('DONE.')

            print('Start VNF ' + vnf['applicationName'] + ' as systemd service ... '),
            vnf_host_container.execute(['systemctl', 'start', vnf['serviceType'] + '.service'])
            print('DONE.')
            print('VNF {} successfully launched in {} with IP address {} !\n'.format(vnf['applicationName'],
                                                                                     vnf['virtualization'],
                                                                                     vnf_host_container_ip))

        elif vnf['virtualization'] == 'vm':
            print('ERROR: VM Virtualization is not supported yet. Aborting ...')
            exit(1)



    # Destroy VNF host (container or VM) and remove all references to the
    # VNF from internal data
    def destroy_vnf(self, vnf, host):

        if vnf['virtualization'] == 'container':
            print('Delete Container {} on host {} ...'.format(vnf['applicationName'], vnf['vnf_host']))
            self._container_manager.delete_virtual_host(host['lxd_connection'],
                                                        vnf['applicationName'])

        elif vnf['virtualization'] == 'vm':
            print('ERROR: VM Virtualization is not supported yet. Aborting ...')
            exit(1)

        print('DONE.')
