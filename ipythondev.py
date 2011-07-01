"""A plugin for installing git master IPython.  Depends on pyzmq (see pyzmq plugin)

Packages are downloaded/installed in threads, allowing for faster installs
when using many nodes.


"""
import time
from threading import Thread

from starcluster.clustersetup import ClusterSetup
from starcluster.logger import log

def threadedssh(nodes, cmd, join=True):
    """Run a command via ssh simultaneously on a collection of nodes."""
    threads = []
    for node in nodes:
        t = Thread(target=node.ssh.execute, args=(cmd,))
        t.start()
        threads.append(t)
    if join:
        for t in threads:
            t.join()
    else:
        return threads

class IPythonSetup(ClusterSetup):
    
    def install_packages(self, nodes, dest='all nodes'):
        log.info("Installing IPython master from github on %s"%dest)
        ipythons = threadedssh(nodes, """
        # get IPython from GitHub
        test -d ~/src || mkdir ~/src
        cd src
        test -d ipython || git clone git://github.com/ipython/ipython.git
        cd ipython && git pull
        python setupegg.py install
        """, join=True)
        
    def run(self, nodes, master, user, user_shell, volumes):
        tic = time.time()
        self.install_packages(nodes)
        mins = (time.time()-tic)/60.
        log.info("Installing IPython master took %.2f mins"%(mins))
    
    def on_add_node(self, node, nodes, master, user, user_shell, volumes):
        self.install_packages([node], node.alias)

        
