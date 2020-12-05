from __future__ import print_function
import paramiko
from os import environ
from dotenv import load_dotenv

load_dotenv()

class SFFManager:
    k = paramiko.RSAKey.from_private_key_file(environ.get('SSH_PRIVATE_KEY_PATH'))

    def __init__(self):
        self.sshClient = paramiko.SSHClient()
        self.sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self, hostname, username):
        #print('Connect to {}:{} with ssh ...'.format(username, hostname), end=' ')
        self.sshClient.connect(hostname=hostname, username=username, pkey=self.k)
        #print('DONE.')

    def disconnect(self):
       # print('Disconnect ssh client ...', end=' ')
        self.sshClient.close()
        #print('DONE.')

    def execute_command(self, command):
        stdin, stdout, stderr = self.sshClient.exec_command(command)
        stdout.read()

        for line in stdout:
            if 'Error' in line or 'RTNETLINK' in line:
                print(line)
                print('\n' + 'ERROR while configuring container with lxc commands over ssh!')
                exit(1)

    def enable_mpls_kernel_module(self, hostname, user):
        print('Enable MPLS kernel module on host {}...'.format(hostname), end=' ')
        command = "sudo modprobe mpls_router && " + \
                  "sudo modprobe mpls_gso && " + \
                  "sudo modprobe mpls_iptunnel && " + \
                  "sudo sysctl -w net.mpls.platform_labels=9999"

        self.connect(hostname, user)
        self.execute_command(command)
        self.disconnect()
        #print('DONE.')

    def write_mpls_forwarding_route(self, hostname, user, mpls_label, ip_address, network_interface):
        print('Write MPLS local route ({} via inet {} dev {}) on host {}...'.format(mpls_label, ip_address,
                                                                                    network_interface,
                                                                                    hostname), end=' ')
        ip_family = 'inet'
        if len(ip_address) > 15:
            ip_family = 'inet6'

        command = "sudo sysctl -w net.mpls.conf." + str(network_interface) + ".input=1 " + " && " + \
                  "sudo ip -f mpls route del " + str(mpls_label) + " && " + "sudo ip -f mpls route replace " + \
                  str(mpls_label) + " via " + ip_family + " " + str(ip_address) + \
                  " dev " + str(network_interface)

        self.connect(hostname, user)
        self.execute_command(command)
        self.disconnect()
        #print('DONE.')

    def write_mpls_local_route(self, hostname, user, mpls_label):
        print('Write MPLS local route on host {}...'.format(hostname), end=' ')
        command = "sudo sysctl -w net.mpls.conf.lo.input=1 " + " && " + \
                  "sudo ip -f mpls route del " + str(mpls_label) + " && " + \
                  "sudo ip -f mpls route add " + str(mpls_label) + " dev lo"

        self.connect(hostname, user)
        self.execute_command(command)
        self.disconnect()
        #print('DONE.')

    def write_mpls_pop_label_route(self, hostname, user, mpls_label, ip_address, network_interface):
        print('Write MPLS pop label route on host {} (Pop label {} and forward packet to {} via {}) ... '
              .format(hostname, mpls_label, ip_address, network_interface), end=' ')

        ip_family = 'inet'
        if len(ip_address) > 15:
            ip_family = 'inet6'

        command = "sudo sysctl -w net.mpls.conf." + str(network_interface) + ".input=1 " + " && " + \
                  "sudo ip -f mpls route replace " + \
                  str(mpls_label) + " via " + ip_family + " " + str(ip_address) + \
                  " dev " + str(network_interface)

        self.connect(hostname, user)
        self.execute_command(command)
        self.disconnect()
        #print('DONE.')

    def remove_mpls_label_route(self, hostname, user, mpls_label):
        print('Remove MPLS label route on host {}...'.format(hostname), end=' ')

        command = "sudo ip -f mpls route del " + str(mpls_label)

        self.connect(hostname, user)
        self.execute_command(command)
        self.disconnect()
        #print('DONE.')

