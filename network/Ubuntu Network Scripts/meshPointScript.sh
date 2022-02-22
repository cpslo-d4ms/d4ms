sudo ifconfig wlx9cefd5fa5eef down
sudo iw wlx9cefd5fa5eef set type mp
sudo ifconfig wlx9cefd5fa5eef up
sudo iw wlx9cefd5fa5eef mesh join PIMESH freq "$2" "$3"
sudo ip addr add "$1"/24 dev wlx9cefd5fa5eef
