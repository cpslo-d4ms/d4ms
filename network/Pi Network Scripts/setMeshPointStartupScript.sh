#!/bin/sh
### BEGIN INIT INFO
# Provides:          setMeshPointStartupScript.sh
# Required-Start:    $remote_fs $sysylog
# Required-Stop:     $remote_fs $sysylog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Connect to mesh network at startup
### END INIT INFO

sudo ifconfig wlan0 down
sudo ifconfig wlan1 down
sudo iw dev wlan1 interface add mesh0 type mp mesh_id PIMESH
sudo ifconfig mesh0 down
sudo iw dev mesh0 set channel 1 HT20
sudo ifconfig mesh0 up
sudo ip addr add 192.168.10.2/24 dev mesh0
