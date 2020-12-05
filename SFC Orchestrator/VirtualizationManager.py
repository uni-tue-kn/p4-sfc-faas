import libvirt
from abc import abstractmethod
import pylxd
import sys
import time
import logging


class VirtualizationManager:

    def __init__(self):
        pass

    @abstractmethod
    def connect(self, client):
        pass

    @abstractmethod
    def create_virtual_host(self, client, config, hostname):
        pass

    @abstractmethod
    def delete_virtual_host(self, client, hostname):
        pass

    @abstractmethod
    def get_host_ip(self, client, hostname):
        pass


class LxdContainerManager(VirtualizationManager):

    CERT_PATH = 'certs/lxd.crt'
    KEY_PATH = 'certs/lxd.key'

    def __init__(self):
        VirtualizationManager.__init__(self)

    # Establish a connection to the LXD daemon
    def connect(self, client_address):
        print('Establish a connection to the LXD daemon at {} ... '.format(client_address)),
        client = pylxd.Client(endpoint=client_address, cert=(self.CERT_PATH, self.KEY_PATH), verify=False)
        client.authenticate('trust')
        print('DONE.')
        return client

    # Create and start a new LXD container with given config and name
    def create_virtual_host(self, client, config, containerName):
        containerName = containerName.replace(' ', '')  # TODO: Handling of the fact that VNF names are not allowed to have whitespaces

        if client.containers.exists(containerName):
            print('Container <', containerName, '> already exists')
            return True
        else:
            # Check if specified image exists on machine
            try:
                client.images.get_by_alias(config['source']['alias'])
            except pylxd.exceptions.NotFound:
                logging.warning("Specified LXC image is not available on the machine.")
                print("Downloading Ubuntu 20 image with alias 'orch-template'... Please wait... ")
                groovy_image = client.images.create_from_simplestreams(server='https://cloud-images.ubuntu.com/daily/',
                                                                       alias='groovy/amd64')
                groovy_image.add_alias('orch-template', 'Ubuntu 20 example image for SFs')
                print("Downloaded Ubuntu 20 image with alias 'orch-template'.")

            # Now create and start the container with the newly downloaded image
            try:
                config['name'] = containerName
                new_container = client.containers.create(config, wait=True)
                new_container.start()
                return not new_container == None
            except pylxd.exceptions.NotFound:
                logging.warning("Downloading image did not help. Specified LXC image is not available on the machine..")

    # Delete an existing LXD container
    def delete_virtual_host(self, client, container_name):
        print('Delete container {} ... '.format(container_name)),
        if client.containers.exists(container_name):
            container = client.containers.get(container_name)
            container.stop()
            time.sleep(2)
            container.delete()
        else:
            print('Container <' + str(container_name) + '> does not exist.')
            sys.exit(1)
        print('DONE.')

    def get_host_ip(self, client, container_name):
        c = client.containers.get(container_name)
        state = c.state()
        net_state = state.network
        if (net_state == None):
            logging.error("Container {} not available! Aborting ...".format(container_name))
            exit(1)
        else:
            return net_state["eth0"]["addresses"][0]["address"]


class LibvirtVmManager(VirtualizationManager):

    def __init__(self):
        VirtualizationManager.__init__(self)

    # establish a connection to the KVM hypervisor
    def connect(self, client_address):
        print('Connect to libvirt hypervisor on ' + client_address + ' ... '),
        try:
            conn = libvirt.open(client_address) # TODO: openAuth verwenden um Password nicht eingeben zu muessen
        except libvirt.libvirtError:
            conn = None
        if conn is None:
            print('ERRPR: Failed to open connection to hypervisor ' + client_address + '. Aborting... ')
            exit(1)

        print('DONE.')
        return conn

    def create_virtual_host(self, client, config, hostname):
        pass

    def delete_virtual_host(self, client, hostname):
        pass

    def get_host_ip(self, client, hostname):
        pass
