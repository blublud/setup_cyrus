sudo userdel dockershell
sudo useradd -r -s /bin/false -G docker dockershell

sudo rm -rf /etc/dockershell
sudo mkdir -p /etc/dockershell/
sudo touch /etc/dockershell/acl.csv
sudo touch /etc/dockershell/OK
sudo chmod 755 -R /etc/dockershell/
sudo chown -R dockershell:dockershell /etc/dockershell/

sudo chmod G=rx /usr/bin/dockershell

#add user to dockershell group:

#for demo:
sudo userdel dockershell
sudo useradd -r -s /bin/false -G docker dockershell

sudo rm -rf /etc/dockershell
sudo mkdir -p /etc/dockershell/
sudo touch /etc/dockershell/acl.csv
sudo touch /etc/dockershell/OK
sudo chmod a+rwx -R /etc/dockershell/

sudo chown -R dockershell:dockershell /etc/dockershell/
