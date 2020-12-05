#!/bin/bash
iptables -I INPUT -j ACCEPT

while $(sleep 10);
do
        echo "Firewall VNF is running111 ..."
done

