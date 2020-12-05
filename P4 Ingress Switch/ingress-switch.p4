/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV4 = 0x800;
const bit<16> TYPE_MPLS = 0x8847;

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;
typedef bit<20> label_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header mpls_t {
    label_t label;
    bit<3> traffic_class;
    bit<1> bottom_of_stack;
    bit<8> time_to_live;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

header icmp_t {
    bit<8> icmp_type;
    bit<8> icmp_code;
    bit<16> icmp_checksum;
}

struct metadata {
    /* empty */
}

struct headers {
    ethernet_t       ethernet;
    mpls_t[MAX_HOPS] mpls;
    ipv4_t           ipv4;
    icmp_t           icmp;
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            TYPE_MPLS: parse_mpls;
            TYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }

    state parse_mpls {
        packet.extract(hdr.mpls.next);
        transition select(hdr.mpls.last.bottom_of_stack) {
            1 : parse_ipv4;
            default: parse_mpls;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol) {
            default: accept;
        }
    }

    state parse_icmp {
        packet.extract(hdr.icmp);
        transition accept;
    }
}

/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

// register<bit<16>>(1) id;
// register<bit<16>>(1) seq_no;
// register<bit<384>>(1) data;

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

    action drop() {
        mark_to_drop(standard_metadata);
    }

    action ipv4_forward(macAddr_t dstAddr, egressSpec_t port) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    action mpls_add_segment_routing_stack_1(label_t label1, label_t label2, label_t label3,
        label_t label4) {

        hdr.ethernet.etherType = TYPE_MPLS;

        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label1, 0, 0, 64};
        hdr.mpls[1].setValid();
        hdr.mpls[1] = {label2, 0, 0, 64};
        hdr.mpls[2].setValid();
        hdr.mpls[2] = {label3, 0, 0, 64};
        hdr.mpls[3].setValid();
        hdr.mpls[3] = {label4, 0, 1, 64};

        // recirculate({standard_metadata});
        standard_metadata.egress_spec = 132;
    }

    action mpls_add_segment_routing_stack_2(label_t label1, label_t label2, label_t label3,
        label_t label4, label_t label5, label_t label6) {

        hdr.ethernet.etherType = TYPE_MPLS;

        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label1, 0, 0, 64};
        hdr.mpls[1].setValid();
        hdr.mpls[1] = {label2, 0, 0, 64};
        hdr.mpls[2].setValid();
        hdr.mpls[2] = {label3, 0, 0, 64};
        hdr.mpls[3].setValid();
        hdr.mpls[3] = {label4, 0, 0, 64};
        hdr.mpls[4].setValid();
        hdr.mpls[4] = {label5, 0, 0, 64};
        hdr.mpls[5].setValid();
        hdr.mpls[5] = {label6, 0, 1, 64};

        // recirculate({standard_metadata});
        standard_metadata.egress_spec = 132;

    }

    action mpls_add_segment_routing_stack_3(label_t label1, label_t label2, label_t label3,
        label_t label4, label_t label5, label_t label6, label_t label7, label_t label8) {

        hdr.ethernet.etherType = TYPE_MPLS;

        hdr.mpls[0].setValid();
        hdr.mpls[0] = {label1, 0, 0, 64};
        hdr.mpls[1].setValid();
        hdr.mpls[1] = {label2, 0, 0, 64};
        hdr.mpls[2].setValid();
        hdr.mpls[2] = {label3, 0, 0, 64};
        hdr.mpls[3].setValid();
        hdr.mpls[3] = {label4, 0, 0, 64};
        hdr.mpls[4].setValid();
        hdr.mpls[4] = {label5, 0, 0, 64};
        hdr.mpls[5].setValid();
        hdr.mpls[5] = {label6, 0, 0, 64};
        hdr.mpls[6].setValid();
        hdr.mpls[6] = {label7, 0, 0, 64};
        hdr.mpls[7].setValid();
        hdr.mpls[7] = {label8, 0, 1, 64};

        // recirculate({standard_metadata});
        standard_metadata.egress_spec = 132;

    }

    action mpls_forward(macAddr_t dstAddr, egressSpec_t port) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.mpls[0].time_to_live = hdr.mpls[0].time_to_live - 1;
    }

    action mpls_pop() {

        hdr.mpls[0].setInvalid();
        hdr.mpls[1].setInvalid();

        //recirculate({standard_metadata});
        standard_metadata.egress_spec = 132;
    }

    action mpls_pop_and_forward(macAddr_t dstAddr, egressSpec_t port) {

        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.mpls[0].time_to_live = hdr.mpls[0].time_to_live - 1;

        hdr.mpls[0].setInvalid();

    }

    action mpls_finish(egressSpec_t port) {

        hdr.mpls[0].setInvalid();
        hdr.ethernet.etherType = TYPE_IPV4;
        hdr.ipv4.setValid();
        standard_metadata.egress_spec = port;
    }

    table customer_lpm {
        key = {
            hdr.ipv4.srcAddr: lpm;
        }
        actions = {
            mpls_add_segment_routing_stack_1;
            mpls_add_segment_routing_stack_2;
            mpls_add_segment_routing_stack_3;
            drop;
            NoAction;
        }
        size = 1024;
    }

    table customer_lpm_backwards {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            mpls_add_segment_routing_stack_1;
            mpls_add_segment_routing_stack_2;
            mpls_add_segment_routing_stack_3;
            drop;
            NoAction;
        }
        size = 1024;
    }

    action default_ipv4_egress(macAddr_t dstAddr, egressSpec_t port) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_forward;
            drop;
            NoAction;
            default_ipv4_egress;
        }
        size = 1024;
    }

    table mpls_exact {
        key = {
            hdr.mpls[0].label: exact;
        }
        actions = {
            mpls_forward;
            mpls_pop;
            mpls_pop_and_forward;
            mpls_finish;
            drop;
            NoAction;
        }
    }

    apply {

        if (hdr.ipv4.isValid()) {
            customer_lpm.apply();
            customer_lpm_backwards.apply();
        }

        if (hdr.mpls[0].isValid()) {
            mpls_exact.apply();
        }

        if (hdr.ipv4.isValid() && !hdr.mpls[0].isValid()){
            ipv4_lpm.apply();
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {

    }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
     apply {

    update_checksum(
	    hdr.ipv4.isValid(),
            { hdr.ipv4.version,
	      hdr.ipv4.ihl,
              hdr.ipv4.diffserv,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
    }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.mpls);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.icmp);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
