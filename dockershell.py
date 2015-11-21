#!/bin/python
import shlex
import sys
import os
import pwd
import csv

from cmd import Cmd
################################################
### ACL CONSTANTS
ACL_DIR             = "/etc/dockershell/"
ACL_PATH            = "%s/acl.csv"%ACL_DIR
ACL_PATH_BACKUP     = "%s/acl_bk.csv"%ACL_DIR
ACL_PATH_BACKUP_OK  = "%s/OK"%ACL_DIR
ACL_CONTAINER   =":container:"
ACL_USER      =   ":username:"
ACL_FIELDS  =   [ACL_CONTAINER, ACL_USER]
################################################
CHECK_OWNER_CMDS    = ['exec','kill','restart','rm','rmi','start','stop']
NOCHECK_OWNER_CMDS  = ['run']
UNGUARDED_COMMANDS  = ['help','commit','info','inspect','login','logout','port','ps','pull','push','search', 'stats', 'version','wait']
GUARDED_COMMANDS    = CHECK_OWNER_CMDS + NOCHECK_OWNER_CMDS
ENABLED_COMMANDS    = GUARDED_COMMANDS + UNGUARDED_COMMANDS
################################################
WELCOME_MSG = \
'''
This is shell wrapper for docker commands.
It is used to prevent the behaviors that may endanger our system.
To report bugs or request new features, please:
    + Go to https://github.com/blublud/setup_cyrus/issues.
    + Notify me via email:pdpham@ucdavis.edu or fb: fb.com/blueblood
I will try to resolve them as soon as possible.

To use this shel, please use docker commands as normal.
E.g. to stop a container cc:
        >>> docker stop cc

'''

def setup_acldb():
    if not os.path.exists(ACL_DIR):
        os.system("sudo mkdir %s"%ACL_DIR)
    os.system("sudo chown root:docker %s"%ACL_DIR)
    os.system("sudo chmod g=rwx %s"%ACL_DIR)
    if not os.path.exists(ACL_PATH):
        os.system("sudo touch %s"%ACL_PATH)
        os.system("sudo chmod g=rw %s"%ACL_PATH)
        #os.system("sudo chown root:dockershell %s"%ACL_PATH)
    os.system("touch %s"%ACL_PATH_BACKUP_OK)

class DockerShell(Cmd):

    def cmdloop(self,intro):
        print intro
        try:
            Cmd.cmdloop(self,intro)
        except KeyboardInterrupt as e:
            self.cmdloop(intro)

    def do_EOF(self,line):
        print ''
        exit(0)

    def do_docker(self,line):
        line = 'docker ' + line
        args=shlex.split(line)

        if args[1] not in ENABLED_COMMANDS:
            print 'This [%s] command is not enabled. If you think it should be, please contact docker admin'%args[1]
            return
        if args[1] in CHECK_OWNER_CMDS:
            containers=extract_container_name_checkowner(args)
            username=get_username()
            if not is_owner(username,containers):
                return

        if args[1] == 'run':
            if not check_run(args):
                return
            username=get_username()
            container=extract_container_name_run(args)
            #make sure the container is created successfully
            if 0 == os.system(line):
                add_container(username,container)
        elif args[1] == 'exec':
            if not check_exec(args):
                return
            os.system(line)
        elif args[1] == 'rm':
            username=get_username()
            containers=extract_container_name_checkowner(args)
            params=args[0:-1*len(containers)]
            for c in containers:
                if 0 == os.system(' '.join(params+[c])):
                    remove_container(username,c)
        else:
            os.system(line)

    def help_docker(self):
        print 'Use docker commands as normal: i.e. ' \
                'to stop container cc, \t 0>>> docker stop cc.'

    def do_acl(self,line):
        acl=get_acl()
        for container,user in acl.items():
            print user + '\t\t' + container

    def help_acl(self):
        print 'List the ownerships of all containers'
    def emptyline(self):
        return

#######################################
#Access Control List utilities
def acl_is_ok():
    if not os.path.exists(ACL_PATH_BACKUP_OK):
        print("Cannot verify ACL backup status. Inconsistency may occured. Contact docker admin")
        return False
    if not os.path.exists(ACL_PATH):
        print("ACL db [%s] is not available. Contact docker admin"%ACL_PATH)
        return False
    return True

def get_acl():
    acl={}
    with open(ACL_PATH) as csvfile:
        reader = csv.DictReader(csvfile,fieldnames=ACL_FIELDS)
        for ac in reader:
            acl[ac[ACL_CONTAINER]]=ac[ACL_USER]
        acl.pop(ACL_CONTAINER,None)

    return acl

def update_acl(acl):
    if not acl_is_ok():
        raise Exception("Last acl backup has error. Contact docker admin")
    os.system("rm %s"%ACL_PATH_BACKUP_OK)
    os.system("cp -f %s %s"%(ACL_PATH, ACL_PATH_BACKUP))

    with open(ACL_PATH,'w') as csvfile:
        writer = csv.DictWriter(csvfile,fieldnames=ACL_FIELDS)
        writer.writeheader()
        for container,user in acl.items():
            writer.writerow({ACL_USER:user,ACL_CONTAINER:container})

    os.system("touch %s"%ACL_PATH_BACKUP_OK)

def add_container(user,container):
    acl=get_acl()
    acl[container]=user
    update_acl(acl)

def remove_container(user,container):
    acl=get_acl()
    acl.pop(container,None)
    update_acl(acl)

def is_owner(username,containers,print_err=True):
    acl=get_acl()
    for c in containers:
        if c not in acl:
            if print_err:
                print "Container [%s] is not found in ACL db"%(c)
            return False
        if acl[c] != username:
            if print_err:
                print "Ownership of user [%s] for container [%s] is not found"%(username,c)
            return False
    return True

def is_currentuser_owner(containers):
    username=get_username()
    return is_owner(username,containers)

########################################
def check_run(args):

    if None==extract_container_name_run(args):
        print "A name for container must be specified. Use --name"
        return False
    #Prevent mapping dirs that the user do not have write access.
    mounts=[]
    #Find all mappings source:
    for i,v in enumerate(args):
        if (v == '-v' or v == '--volume') and i + 1 <= len(args):
            mounts.append(args[i+1])
    #enforce dir must pre-exist and user has write permission
    for pair in mounts:
        if len(pair.split(':')) != 2:
            print ("Mount point syntax [%s] is incorrect"%pair)
            return False
        dir=pair.split(':')[0]
        if not os.access(dir, os.F_OK):
            print ("The directory you are trying to mount [%s] does not exist"%dir)
            return False
        if not os.access(dir, os.W_OK):
            print ("The directory you are trying to mount [%s] is not writeable"%dir)
            return False
    return True

def check_exec(args):
    #Only allow bash command
    command=None
    for i,arg in enumerate(args[2:],start=2):
        if      not args[i].startswith('-') \
                and i + 1 < len(args) \
                and args[i+1] != 'bash':
            print("Only command 'bash' is allowed in docker exec.")
            return False
    return True

def extract_container_name_checkowner(args):
    if args[1] not in CHECK_OWNER_CMDS:
        print 'Extracting container name for this command [%s] is not supported'%args[1]
        return None
    if args[1] in ['kill','restart','rm','restart','start','stop']:
        return [arg for arg in args[2:] if not arg.startswith('-')]

    elif args[1] in ['exec']:
        tokens=[]
        for i,arg in enumerate(args[2:],start=2):
            if not args[i].startswith('-'):
                return [arg]
        return None

def extract_container_name_run(args):
    if '--name' not in args:
        return None
    idx = args.index('--name')
    if (idx + 1 >= len(args)):
        return None

    return args[idx + 1]

def get_username():
    return pwd.getpwuid( os.getuid() )[0]

def __main__():
    if not acl_is_ok():
        exit(1)

    shell = DockerShell()
    shell.prompt='>>> '
    shell.cmdloop(WELCOME_MSG)

if __name__ == '__main__':
    __main__()

'''
Testing inputs:
docker run -d -p 8888:8888 --name datsci -v /docker:/home/jovyan/work/  -e NB_UID=1002 jupyter/datascience-notebook

docker run -d --name datsci -v /tmp/pdp/:/home/jovyan/work/ -v /tmp/pdp/d:/home/jovyan/work/ jupyter/datascience-notebook

docker run -d --name datsci jupyter/datascience-notebook
'''
