Recovering mariadb:
1. Re-install mariadb version (10.0) as before the incident happened
2. Disable Transparent HugePage Support to use tokudb plug-in
Modify /etc/rc.local

if test -f /sys/kernel/mm/transparent_hugepage/enabled; then
   echo never > /sys/kernel/mm/transparent_hugepage/enabled
fi
if test -f /sys/kernel/mm/transparent_hugepage/defrag; then
   echo never > /sys/kernel/mm/transparent_hugepage/defrag
fi

3. Configure mariadb to use previous configuration (file my3307.cnf) (copied from backup data)
4. Start mariadb (use previous accounts/passwords) automatically when system starts:
Add this line to /etc/rc.local (does not work)
mysqld_safe --defaults-file=/path/to/my3307.cnf --user=mysql &

Note:
Due to legacy issue, our configuration is quite special: There are two instances of mysql running:
+ One is the default instance running in port 3306.
+ One using my3307 config, restored from previous system.
