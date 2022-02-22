#!/bin/bash
sudo ifconfig wlx9cefd5fa5eef down
sudo iw wlx9cefd5fa5eef set type ibss
sudo ifconfig wlx9cefd5fa5eef up
sudo iw dev wlx9cefd5fa5eef ibss join PIHOC "$2" "$3"
sudo ip addr add "$1"/24 dev wlx9cefd5fa5eef
