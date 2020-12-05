from __future__ import print_function
import paramiko
from os import environ
from dotenv import load_dotenv

load_dotenv()

class SFCProxyManager:
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

    def lxc_configure_sfc_proxy_mpls(self, hostname, user, server_ip, label_stack, container_name, vnf_label):
        print('Configure MPLS on SFC proxy container {} on VNF host {}...'.format(container_name, hostname), end=' ')

        ip_family = 'inet'
        if len(server_ip) > 15:
            ip_family = 'inet6'

        remaining_labels = map(str, label_stack[label_stack.index(vnf_label) + 1:])

        # TODO: Alternative:
        # execute - Execute a command on the container. The first argument is a list, in the form of subprocess.Popen with each item of the command as a separate item in the list. Returns a tuple of (exit_code, stdout, stderr). This method will block while the command is executed.

        # Enable MPLS kernel module in container
        lxc_command = "lxc exec " + str(container_name) + \
                      " -- sh -c \"sysctl -w net.mpls.platform_labels=9998\"" + " && " + \
                      "lxc exec " + str(container_name) + \
                      " -- sh -c \"sysctl -w net.mpls.conf.lo.input=1\"" + " && " + \
                      "lxc exec " + str(container_name) + \
                      " -- sh -c \"sysctl -w net.mpls.conf.eth0.input=1\""  # TODO: Hardcoded eth0 interface of container

        # Configure container to pop vnf_label and deliver locally
        lxc_command += " && lxc exec " + str(container_name) + " -- sh -c \"sudo ip -f mpls route replace " + str(
            vnf_label) + " dev lo\""

        # Configure container to remove remaining label stack
        for label in remaining_labels:
            lxc_command += " && lxc exec " + str(container_name) + " -- sh -c \"sudo ip -f mpls route replace " + str(
                label) + " dev lo\""

        # Configure container to push remaining label stack after VNF has processed packet
        remaining_labels_formatted_string = '/'.join(remaining_labels)
        lxc_command += " && lxc exec " + str(container_name) + " -- sh -c \"sudo ip route replace 0.0.0.0/0 encap mpls " + \
                       str(remaining_labels_formatted_string) + " via " + str(ip_family) + " " + str(
            server_ip) + " dev eth0\""

        self.connect(hostname, user)
        self.execute_command(lxc_command)
        self.disconnect()
        #print('DONE.')


    def lxc_configure_sfc_proxy_mpls_backwards(self, hostname, user, server_ip, label_stack_backwards, container_name,
                                               vnf_label, dstAddress):
        print('Configure backward MPLS on SFC proxy container {} on VNF host {}...'.format(container_name, hostname),
              end=' ')

        ip_family = 'inet'
        if len(server_ip) > 15:
            ip_family = 'inet6'

       # No VNF in the backwards label stack
        if len(label_stack_backwards) <= 2:
            print('No mpls routes need to be set here.')
        else:
            remaining_labels = map(str, label_stack_backwards[label_stack_backwards.index(vnf_label) + 1:])

            # Enable MPLS kernel module in container
            lxc_command = "lxc exec " + str(container_name) + \
                          " -- sh -c \"sysctl -w net.mpls.platform_labels=9998\"" + " && " + \
                          "lxc exec " + str(container_name) + \
                          " -- sh -c \"sysctl -w net.mpls.conf.lo.input=1\"" + " && " + \
                          "lxc exec " + str(container_name) + \
                          " -- sh -c \"sysctl -w net.mpls.conf.eth0.input=1\""  # TODO: Hardcoded eth0 interface of container

            # Configure container to pop vnf_label and deliver locally
            lxc_command += " && lxc exec " + str(container_name) + " -- sh -c \"sudo ip -f mpls route replace " + str(
                vnf_label) + " dev lo\""

            # Configure container to remove remaining label stack
            for label in remaining_labels:
                lxc_command += " && lxc exec " + str(container_name) + " -- sh -c \"sudo ip -f mpls route replace " + str(
                    label) + " dev lo\""

            # Configure container to push remaining label stack after VNF has processed packet
            remaining_labels_formatted_string = '/'.join(remaining_labels)
            lxc_command += " && lxc exec " + str(
                container_name) + " -- sh -c \"sudo ip route replace " + dstAddress + " encap mpls " + \
                           str(remaining_labels_formatted_string) + " via " + str(ip_family) + " " + str(
                server_ip) + " dev eth0\""

            self.connect(hostname, user)
            self.execute_command(lxc_command)
            self.disconnect()
