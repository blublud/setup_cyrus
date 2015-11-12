#Restore cyrus

###Set up apache2
apt-get install apache2

###Configure php
apt-get install libapache2-mod-php5
apt-get install php5-mysqlnd

copy /etc/apache2 from backup.
copy /etc/php/ from backup

###Sites:
The webserver hosts websites located at /var/www/vhosts/
Copy web sites from backup data into /var/www/vhosts/

###Sphinx
apt-get install sphinxsearch

edit /etc/default/sphinxsearch and set START=yes
service sphinxsearch start
