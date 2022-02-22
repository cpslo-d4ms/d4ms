#!/bin/bash
sudo ifconfig wlan0 down
sudo ifconfig wlan1 down
sudo iw dev wlan1 interface add mesh0 type mp mesh_id PIMESH
sudo ifconfig mesh0 down
sudo iw dev mesh0 set channel "$2" "$3"
sudo ifconfig mesh0 up
sudo ip addr add "$1"/24 dev mesh0
iw dev
