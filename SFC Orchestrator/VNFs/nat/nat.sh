#!/bin/bash
sudo iptables -t nat -A POSTROUTING -o eth0 -j SNAT --to 192.168.122.50
#sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE