#!/bin/bash
#This scrip is meant to be copied to a Linux server that is going to be managed by QMN-Ansible/Rundeck.
#If you do not wish to have the server managed in this way, do not run this script.rundeck_ip
# Written By: Braxton Acheson

#Creating timestamp for the logs
tstamp=$(date +%d/%m/%y-%T)
#create the ansible_client.log file for errors
currentdir=$(pwd)
#errlog=$($currentdir/ansible_client.log)
#sudo touch $errlog
#echo "Errors for this script will be logged here: $errlog" 

#IP Address of the Rundeck Ansible Server
rundeck_ip="192.168.101.62"

#Sudo permissions are required for this script to work properly,
#This script will start with a sudo command to accept the sudo password right away.
echo "This script requires the use of sudo, so please enter your sudo password now."
echo "This script will proceeed automatically if your sudo password is not needed!"
sudo echo "$tstamp Script has started" 

#Prompt for password
read -p "Please enter the password you would like to use for the qmnansible and rundeck user: " qmnpasswd
echo "$tstamp Rundeck and qmnansible password configured" 
runpasswd=$qmnpasswd

#This section will determine what OS the current system is
client_os=$(cat /etc/os-release | grep 'ID=' | grep -iv 'version_id=' | grep -iv 'platform' | cut -d "=" -f2) 
sudo echo "$tstamp It looks like you are using $client_os!" 
#Setting the static OS options for the If/Else
ubuntu_os="ubuntu"
kali_os="kali"
pi_os="raspbian"
centos_os="centos"
rocky_os="rocky"

#Set the sudo_group variable based on the OS detected.
if [[ $client_os == $ubuntu_os ]] || [[ $client_os == $kali_os ]] || [[ $client_os == $pi_os ]]
    then
    #Debian based sudoers group is sudo
        sudo_group="sudo"
        sudo echo "$tstamp User will be added to the sudo group." 
        
    elif [[ $client_os == $centos_os ]] || [[ $client_os == $rocky_os ]]
        then
        #RHEL based sudoers group is wheel.
        sudo_group="wheel"
        sudo echo "$tstamp Users will be added to the wheel group." 
        
    else
        sudo echo "$tstamp You are using an unexpected OS, so you will have to add the users to the sudo group manually." 

fi

#This section will create the qmnansible user
    echo "Starting by creating the qmnansible user: "
#read -p "What password would you like to configure the qmnansible user with?" qmnpasswd
    sudo useradd -m qmnansible 
    echo "qmnansible:$qmnpasswd" | sudo chpasswd
    sudo usermod -aG wheel qmnansible
    echo "qmnansible ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/qmnansible

#This section will create the Rundeck User
    echo "Starting by creating the rundeck user:"
    echo "Setting up the Rundeck user with the same password."
    sudo useradd -m rundeck 
    echo "rundeck:$qmnpasswd" | sudo chpasswd
    sudo gpasswd -a rundeck wheel
    echo "rundeck ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/rundeck

#Prompt for what IP and Hostname should be written to the hostfile
    read -p "What is the IP address of the current server? " curr_serverip
    echo "Adding the IP $curr_serverip to the Rundeck/Ansible File"
    sshpass -vvv -p "Mm8@3m1N*" ssh -o StrictHostKeyChecking=no qmnansible@$rundeck_ip "echo '$curr_serverip' | tee  /etc/ansible/tmp/IPADDRESS.txt"

    read -p "What is the Hostname that you would like added to the Rundeck Project? " curr_hostname
    echo "Adding the Hostname $curr_hostname to the Rundeck/Ansible File."
    sshpass -vvv -p "Mm8@3m1N*" ssh -o StrictHostKeyChecking=no qmnansible@$rundeck_ip  "echo '$curr_hostname' | tee  /etc/ansible/tmp/HOSTNAME.txt"

#Host File Selection
    echo "###############################################################"
    echo ""
    echo " 1.) AMA Hosts"
    echo " 2.) Data Center/IT Hosts"
    echo " 3.) NTA Hosts"
    echo " 4.) Raspberry Pi Hosts"
    echo " 5.) SEL Hosts"
    echo ""
    read -p "What Hostfile should this host be applied to? (Please only enter a Number): " host_select

    if [[ $host_select -eq 1 ]]
        then
        #Debian based sudoers group is sudo
        echo "You have selected AMA Hosts!"
        sshpass -vvv -p "Mm8@3m1N*" ssh -o StrictHostKeyChecking=no qmnansible@$rundeck_ip  'bash -s < /home/qmnansible/scripts/rundeck/AMA-autoAdd.sh'
        
        elif [[ $host_select -eq 2 ]]
        then
        #Debian based sudoers group is sudo
        echo "You have selected Data Center/IT Hosts!"
        sshpass -vvv -p "Mm8@3m1N*" ssh -o StrictHostKeyChecking=no qmnansible@$rundeck_ip 'bash -s < /home/qmnansible/scripts/rundeck/DC-autoAdd.sh'
        
        elif [[ $host_select -eq 3 ]]
        then
        #Debian based sudoers group is sudo
        echo "You have selected NTA Hosts!"
        sshpass -vvv -p "Mm8@3m1N*" ssh -o StrictHostKeyChecking=no qmnansible@$rundeck_ip 'bash -s < /home/qmnansible/scripts/rundeck/NTA-autoAdd.sh'

        elif [[ $host_select -eq 4 ]]
        then
        #Debian based sudoers group is sudo
        echo "You have selected Raspberry Pi Hosts"
        sshpass -vvv -p "Mm8@3m1N*" ssh -o StrictHostKeyChecking=no qmnansible@$rundeck_ip 'bash -s < /home/qmnansible/scripts/rundeck/PI-autoAdd.sh'

        elif [[ $host_select -eq 5 ]]
        then
        #Debian based sudoers group is sudo
        echo "You have selected SEL Hosts!"
        sshpass -vvv -p "Mm8@3m1N*" ssh -o StrictHostKeyChecking=no qmnansible@$rundeck_ip  'bash -s < /home/qmnansible/scripts/rundeck/SEL-autoAdd.sh'

        else
        #Debian based sudoers group is sudo
        echo "You have made an invalid selection, using the default"
        sshpass -vvv -p "Mm8@3m1N*" ssh -o StrictHostKeyChecking=no qmnansible@$rundeck_ip 'bash -s < /home/qmnansible/scripts/rundeck/Default-autoAdd.sh'

    fi


#Password Scrub
echo "The script has completed, Ruining everything now :) "
sleep 5
currentdir=$(pwd)
sudo sed -i s/"Mm8@3m1N*"/"<SCRUBBED>"/g $currentdir/Rundeck-Client_AUTO.sh
