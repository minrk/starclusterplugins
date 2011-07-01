"""A plugin for running a script, and retrieving some file as output


"""
import os
import posixpath
import time

from starcluster.clustersetup import ClusterSetup
from starcluster.logger import log

def user_ssh(node, user, cmd):
    """run code as user, from user's home"""
    return node.ssh.execute("su - %s -c 'cd && %s'"%(user, cmd))

class ScriptSetup(ClusterSetup):
    
    def __init__(self, script, output=None, runner='python'):
        self.script = os.path.expanduser(script)
        self.output = output
        self.runner = runner
    
    def _send_script(self, node, user):
        fname = os.path.basename(self.script)
        user_home = node.getpwnam(user).pw_dir
        remotepath = posixpath.join(user_home, fname)
        log.info("Sending %s to %s as %s"%(self.script, node.alias, remotepath))
        rf = node.ssh.remote_file(remotepath)
        with open(self.script) as f:
            rf.write(f.read())
        rf.close()
        
        # give ownership to the user
        node.ssh.execute("chown %s %s"%(user,remotepath))
        return remotepath

    def run(self, nodes, master, user, user_shell, volumes):
        tic = time.time()
        rfile = self._send_script(master, user)
        s = user_ssh(master, user, "%s %s"%(self.runner, rfile))
        for line in s:
            # print the output of the script, which may be meaningful
            log.info(line)
        output = self.output
        if output:
            if os.path.basename(output) == output:
                user_home = master.getpwnam(user).pw_dir
                output = posixpath.join(user_home, output)
            log.info("retrieving output from %s"%output)
            base = posixpath.basename(output)
            dest = base
            i=1
            while os.path.exists(dest):
                dest = "%s_%i"%(base,i)
                i+=1
            master.ssh.sftp.get(output, dest)
        mins = (time.time()-tic)/60.
        log.info("Running script %s took %.2f mins"%(self.script, mins))
    
