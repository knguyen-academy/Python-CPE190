#!/bin/bash

#Collecting data through gs.py
sudo python /home/pi/gs.py
echo "Sleeping" >> /home/pi/log.txt
sleep 5
echo "Wakeup" >> /home/pi/log.txt
echo "Parsing" >> /home/pi/log.txt
sudo python /home/pi/parse.py
echo "Parsed" >> /home/pi/log.txt

#Sending all files 
echo "Sending out1" >> /home/pi/log.txt
sshpass -p '123456' scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no /home/pi/out1.txt knguyen@10.117.132.25:/Desktop
echo "Sending out2" >> /home/pi/log.txt
sshpass -p '123456' scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no /home/pi/out2.txt knguyen@10.117.132.25:/Desktop
echo "Sending out3" >> /home/pi/log.txt
sshpass -p '123456' scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no /home/pi/out3.txt knguyen@10.117.132.25:/Desktop
echo "Sending out4" >> /home/pi/log.txt
sshpass -p '123456' scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no /home/pi/out4.txt knguyen@10.117.132.25:/Desktop
echo "Sending out5" >> /home/pi/log.txt
sshpass -p '123456' scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no /home/pi/out5.txt knguyen@10.117.132.25:/Desktop
echo "Sending out6" >> /home/pi/log.txt
sshpass -p '123456' scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no /home/pi/out6.txt knguyen@10.117.132.25:/Desktop
echo "Sending out0" >> /home/pi/log.txt
sshpass -p '123456' scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no /home/pi/out0.txt knguyen@10.117.132.25:/Desktop

#sshpass -p '123456' sftp -o UserKnownHostsFile=/dev/null/ -o StrictHostkeyChecking=no -oBatchMode=no -b - knguyen@10.117.132.25:/Desktop  << !
#	put output3.txt
#	bye
#!
echo "DONE!" >> /home/pi/log.txt
