#!/bin/bash
interfaceName=`ls /sys/class/net/ | grep wlx`

sudo ifconfig $interfaceName down
sudo iw $interfaceName set type mp
sudo ifconfig $interfaceName up
sudo iw $interfaceName mesh join PIMESH freq "$2" "$3"
sudo ip addr add "$1"/24 dev $interfaceName