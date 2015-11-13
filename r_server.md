##1.Add PGP key
>sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E084DAB9  
echo "deb http://cran.mtu.edu/bin/linux/ubuntu trusty/" >> /etc/apt/sources.list  
sudo apt-get update  
sudo apt-get install r-base  
sudo apt-get install gdebi-core  
wget https://download2.rstudio.org/rstudio-server-0.99.489-amd64.deb  
sudo gdebi rstudio-server-0.99.489-amd64.deb
##
