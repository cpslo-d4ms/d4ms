#!/bin/bash
sudo iw dev wlan1 ibss leave
sudo iw dev wlan1 ibss join PIHOC "$2" "$3"
sudo ip addr del 192.168.4.1/24 dev wlan1
sudo ip addr add "$1"/24 dev wlan1
