#!/bin/bash
sudo rfcomm connect 0 00:06:66:8C:D3:F8 >/dev/null &
sudo python /home/pi/button.py &
echo "Sleep" >> /home/pi/bluetooth.log.txt
sleep 10
echo "Done Sleep" >> /home/pi/bluetooth.log.txt
sudo /usr/local/bin/script.sh

