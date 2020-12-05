# Imports for DataPlaneController
import p4runtime_lib.bmv2
import p4runtime_lib.helper

class BMv2Controller:

    def __init__(self, switch_address, p4info_file_path, bmv2_file_path):
        self._p4info_file_path = p4info_file_path
        self._bmv2_file_path = bmv2_file_path
        self._switch_address = switch_address
        self.p4info_helper = p4runtime_lib.helper.P4InfoHelper(self._p4info_file_path)
        self.packet_in_thread = None
        self.switch = None

    # Initialize switch (check connection to switch and install P4 program)
    def initialize(self):
        # PYTHON 2 SYNTAX for ending print without newline!
        # (TODO when porting to Python3)
        print('Connect to switch at ' + str(self._switch_address) + ' ...'),
        self.connect_to_switch(self._switch_address)
        print('DONE.')

        print('Install P4 progam to switch ... '),
        self.switch.SetForwardingPipelineConfig(p4info=self.p4info_helper.p4info,
                                                bmv2_json_file_path=self._bmv2_file_path)

        self.disconnect_from_switch()
        print('DONE. \n')

    # Create a switch connection object that is backed by a P4Runtime gRPC connection.
    # Then, send master arbitration update message to establish this controller as
    # master. This is required by P4Runtime before performing any other write operation.
    def connect_to_switch(self, switch_address):
        switch_connection = p4runtime_lib.bmv2.Bmv2SwitchConnection(name="ingress-switch", address=switch_address,
                                                                    device_id=0)
        switch_connection.MasterArbitrationUpdate()
        self.switch = switch_connection

    # Destroy connection object 'self.switch'
    def disconnect_from_switch(self):
        self.switch.shutdown()

    # Generate Bmv2 table entry for pushing an MPLS label stack to packets that match
    # the given source or destination IP address
    def generate_table_entry_mpls_encapsulation(self, label_stack, address_type, ip_address, ip_prefix_length):

        if (address_type != 'src') & (address_type != 'dst'):
            print('ERROR: Address type must be one of "src" or "dst". Defaulting to "src".')
            address_type = 'src'

        # TODO: Better determine the number of VNFs ?
        num_vnfs = (len(label_stack) - 2) / 2

        if address_type == 'src':
            table_name = "MyIngress.customer_lpm"
            match_fields = {"hdr.ipv4.srcAddr": (ip_address, int(ip_prefix_length))}
        elif address_type == 'dst':
            table_name = "MyIngress.customer_lpm_backwards"
            match_fields = {"hdr.ipv4.dstAddr": (ip_address, int(ip_prefix_length))}

        # Assemble the table entry, depending on the number of VNFs in the SFC.
        # The number of labels to push is (num_vnfs * 2 + 2) (1 label for each VNF, 1 label for each SFF,
        # 1 label for the ingress switch, 1 label for determining the port to send the packet to
        if num_vnfs < 1:
            print('SFC emtpy. No table entry has to be generated for label stack {}'.format(label_stack))
            return None

        elif num_vnfs == 1:
            action_name = "MyIngress.mpls_add_segment_routing_stack_1"
            action_params = {"label1": label_stack[0], "label2": label_stack[1], "label3": label_stack[2],
                             "label4": label_stack[3]}

        elif num_vnfs == 2:
            action_name = "MyIngress.mpls_add_segment_routing_stack_2"
            action_params = {"label1": label_stack[0], "label2": label_stack[1], "label3": label_stack[2],
                             "label4": label_stack[3], "label5": label_stack[4], "label6": label_stack[5]}

        elif num_vnfs == 3:
            action_name = "MyIngress.mpls_add_segment_routing_stack_3"
            action_params = {"label1": label_stack[0], "label2": label_stack[1], "label3": label_stack[2],
                             "label4": label_stack[3], "label5": label_stack[4], "label6": label_stack[5],
                             "label7": label_stack[6], "label8": label_stack[7]}
        else:
            print('You requested more than 3 VNFs. A maximum of 3 VNFs is supported so far - aborting...')
            exit(1)

        table_entry = self.p4info_helper.buildTableEntry(
            table_name=table_name,
            match_fields=match_fields,
            action_name=action_name,
            action_params=action_params
        )
        return table_entry

    # Generate Bmv2 table entry for forwarding packets that match
    # the given destination IP address to destination MAC address through egress port
    def generate_table_entry_ipv4_lpm(self, dst_ip_address, dst_ip_prefix_length, dst_mac, egress_port):
        table_entry = self.p4info_helper.buildTableEntry(
            table_name="MyIngress.ipv4_lpm",
            match_fields={
                "hdr.ipv4.dstAddr": (dst_ip_address, dst_ip_prefix_length)
            },
            action_name="MyIngress.ipv4_forward",
            action_params={
                "dstAddr": dst_mac,
                "port": egress_port
            })
        return table_entry

    # Generate Bmv2 table entry for forwarding packets that match the given MPLS label
    # to dst_mac via egress_port
    def generate_table_entry_mpls_forward(self, label, dst_mac, egress_port):
        table_entry = self.p4info_helper.buildTableEntry(
            table_name="MyIngress.mpls_exact",
            match_fields={
                "hdr.mpls[0].label": label
            },
            action_name="MyIngress.mpls_forward",
            action_params={
                "dstAddr": dst_mac,
                "port": egress_port
            })
        return table_entry

    # Generate Bmv2 table entry for IP-forwarding packets that match the given MPLS label via egress_port
    def generate_table_entry_mpls_finish(self, label, egress_port):
        table_entry = self.p4info_helper.buildTableEntry(
            table_name="MyIngress.mpls_exact",
            match_fields={
                "hdr.mpls[0].label": label
            },
            action_name="MyIngress.mpls_finish",
            action_params={
                "port": egress_port
            })
        return table_entry

    # Write encapsulation rules for traffic type, given the address type ("src" or "dst"), ip address and prefix length
    def write_mpls_sr_rule(self, label_stack, address_type, ip_address, ip_prefix_length):
        self.connect_to_switch(self._switch_address)

        if (address_type == 'src'):
            print('Write MPLS SR route to {} (Traffic from {}/{} is encapsulated with stack {}) ...  '
                  .format(self.switch.name, ip_address, ip_prefix_length, label_stack)),
        elif (address_type == 'dst'):
            print('Write MPLS SR route to {} (Traffic to {}/{} is encapsulated with stack {}) ...  '
                  .format(self.switch.name, ip_address, ip_prefix_length, label_stack)),

        # Generate and write the table entry
        table_entry = self.generate_table_entry_mpls_encapsulation(label_stack, address_type, ip_address,
                                                                   ip_prefix_length)

        if table_entry is not None:
            self.switch.WriteTableEntry(table_entry)

        self.disconnect_from_switch()
        print('DONE.')

    # Write rules for pushing SFC label stack to ingress node
    def delete_mpls_sr_rule(self, label_stack, address_type, ip_address, ip_prefix_length):
        self.connect_to_switch(self._switch_address)

        print('Delete MPLS SR route from ingress-switch {} (Traffic from {}/{} is encapsulated with stack {}) ... '
              .format(self.switch.name, ip_address, ip_prefix_length, label_stack)),

        # Generate and write the table entry
        table_entry = self.generate_table_entry_mpls_encapsulation(label_stack, address_type, ip_address,
                                                                   ip_prefix_length)
        if table_entry is not None:
            self.switch.DeleteTableEntry(table_entry)

        self.disconnect_from_switch()
        print('DONE.')

    # Write default rule for forwarding packets that are not cought by rules to
    # destination MAC address through egress port
    def write_default_ipv4_lpm_rule(self, dst_mac, egress_port):
        self.connect_to_switch(self._switch_address)

        print(
            'Write IPv4 LPM default forward rule to ingress-switch {} (Send to MAC address {} via port {}) ... '
            .format(self.switch.name, dst_mac, egress_port)),

        # Generate and write the table entry
        table_entry = self.p4info_helper.buildTableEntry(
            table_name="MyIngress.ipv4_lpm",
            action_name="MyIngress.default_ipv4_egress",
            default_action=True,
            action_params={
                "dstAddr": dst_mac,
                "port": egress_port
            })
        self.switch.WriteTableEntry(table_entry)

        self.disconnect_from_switch()
        print('DONE.')

    # Write rule for forwarding packets that match
    # the given destination IP address to destination MAC address through egress port
    def write_ipv4_lpm_rule(self, dst_ip_address, dst_ip_prefix_length, dst_mac, egress_port):
        self.connect_to_switch(self._switch_address)

        print('Write IPv4 LPM forward rule for address {}/{} to ingress-switch {} (Send to MAC address {} via port {}) ... '
                .format(dst_ip_address, dst_ip_prefix_length, self.switch.name, dst_mac, egress_port)),

        # Generate and write the table entry
        table_entry = self.generate_table_entry_ipv4_lpm(dst_ip_address, dst_ip_prefix_length, dst_mac, egress_port)
        self.switch.WriteTableEntry(table_entry)

        self.disconnect_from_switch()
        print('DONE.')

    # Delete rule for forwarding packets that match
    # the given destination IP address to destination MAC address through egress port
    def delete_ipv4_lpm_rule(self, dst_ip_address, dst_ip_prefix_length, dst_mac, egress_port):
        self.connect_to_switch(self._switch_address)

        print(
            'Delete IPv4 LPM forward rule for address {}/{} from ingress-switch {} (Send to MAC address {} via '
            'port {}) ... '
                .format(dst_ip_address, dst_ip_prefix_length, self.switch.name, dst_mac, egress_port)),

        # Generate and write the table entry
        table_entry = self.generate_table_entry_ipv4_lpm(dst_ip_address, dst_ip_prefix_length, dst_mac, egress_port)
        self.switch.DeleteTableEntry(table_entry)

        self.disconnect_from_switch()
        print('DONE.')

    # Write rule for MPLS-forwarding packets that match the given MPLS label
    # to dst_mac via egress_port
    def write_mpls_forward_rule(self, label, dst_mac, egress_port):
        self.connect_to_switch(self._switch_address)
        print(
            'Write MPLS forward rule to switch {} (Traffic with MPLS label {} is sent to MAC address {} via port {}) ... '.format(
                self.switch.name, label, dst_mac, egress_port)),

        # Generate and write the table entry
        table_entry = self.generate_table_entry_mpls_forward(label, dst_mac, egress_port)
        self.switch.WriteTableEntry(table_entry)

        self.disconnect_from_switch()
        print('DONE.')

    # Write rule for IP-forwarding packets that match the given MPLS label via egress_port
    def write_mpls_finish_rule(self, label, egress_port):
        self.connect_to_switch(self._switch_address)
        print(
            'Write MPLS finish rule to switch {} (Traffic with MPLS label {} is sent via port {}) ... '.format(
                self.switch.name, label, egress_port)),

        # Generate and write the table entry
        table_entry = self.generate_table_entry_mpls_finish(label, egress_port)
        self.switch.WriteTableEntry(table_entry)

        self.disconnect_from_switch()
        print('DONE.')

    # def writeMplsPoprule(self, label):
    #     # Assemble the table entry
    #     table_entry = self.p4info_helper.buildTableEntry(
    #         table_name="MyIngress.mpls_exact",
    #         match_fields={
    #             "hdr.mpls[0].label": label
    #         },
    #         action_name="MyIngress.mpls_pop")
    #
    #
    #     print('Connect to switch at ' + str(self._switch_address) + ' ... '),
    #     self.connect_to_switch(self._switch_address)
    #     print('DONE.')
    #
    #     # Write the table entry
    #     print('Install MPLS pop rule ...  (Pop MPLS label {})'.format(label))
    #     self.switch.WriteTableEntry(table_entry)
    #     print("Installed MPLS Pop rule on switch %s" % self.switch.name)
    #
    #     self.disconnect_from_switch()
    #     print('Disconnected from switch!')

    # def writeMplsPopAndForwardrule(self, label, dstMac, port):
    #     # Assemble the table entry
    #     table_entry = self.p4info_helper.buildTableEntry(
    #         table_name="MyIngress.mpls_exact",
    #         match_fields={
    #             "hdr.mpls[0].label": label
    #         },
    #         action_name="MyIngress.mpls_pop_and_forward",
    #         action_params={
    #             "dstAddr": dstMac,
    #             "port": port
    #         })
    #
    #     # Write the table entry
    #     self.switch.WriteTableEntry(table_entry)
    #     print("Installed MPLS Exact rule on switch %s" % self.switch.name)

    # def getCounterPackets(self, counter_name, index):
    #     """Returns the value of a packet counter at a specific index
    #
    #     :param counter_name: name of the counter
    #     :param index: index of the counter field
    #     :return: number. packet count
    #     """
    #     for response in self.switch.ReadCounters(self.p4info_helper.get_counters_id(counter_name), index):
    #         for entity in response.entities:
    #             counter = entity.counter_entry
    #
    #             # only return first
    #             return counter.data.packet_count

    # def getCounterBytes(self, counter_name, index):
    #     """Returns the value of a byte counter at a specific index
    #
    #     :param counter_name: name of the counter
    #     :param index: index of the counter field
    #     :return: number. byte count
    #     """
    #     for response in self.switch.ReadCounters(self.p4info_helper.get_counters_id(counter_name), index):
    #         for entity in response.entities:
    #             counter = entity.counter_entry
    #
    #             # only return first
    #             return counter.data.byte_count

    # Check if the message received from the switch contains a payload
    # def response_callback(self, switch, response):
    #     if response.packet.payload:
    #         self.packet_in_callback(switch, response.packet.payload)
    #     else:
    #         pass

    # def packet_in_callback(self, switch, packet_in):
    #
    #     print("Received packet in from switch %s" % self.switch.name)
    #     print(packet_in)
