#!/bin/bash
sudo cp setMeshPointStartupScript.sh /etc/init.d/
cd /etc/init.d
sudo chmod +x setMeshPointStartupScript.sh
sudo update-rc.d setMeshPointStartupScript.sh defaults
echo "Please run sudo reboot"
