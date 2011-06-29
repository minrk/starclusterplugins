"""Two plugins for installing pyzmq, either from source, or from an egg

The EggSetup is generic, and should work for any eggs

Source:
    Installed: 
    * uuid-dev from apt
    * zeromq-2.1.7
    * pyzmq-2.1.7

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

class EggSetup(ClusterSetup):
    """install a Python egg.  Specify egg_url in plugin config."""
    def __init__(self, egg_url):
        self.egg_url = egg_url
    
    def install_packages(self, nodes, dest='all nodes'):
        log.info("Installing egg %s on %s"%(self.egg_url, dest))
        threadedssh(nodes, "easy_install %s"%self.egg_url)
        
    def run(self, nodes, master, user, user_shell, volumes):
        self.install_packages(nodes)
    
    def on_add_node(self, node, nodes, master, user, user_shell, volumes):
        self.install_packages([node], node.alias)

class PyZMQSourceSetup(ClusterSetup):
    """Build PyZMQ and its dependencies from source."""
    def install_packages(self, nodes, dest='all nodes'):
        threadedssh(nodes, "test -d ~/src || mkdir ~/src")
        log.info("building PyZMQ and dependencies from source on %s"%dest)
        log.info("Installing zeromq-2.1.7 on %s"%dest)
        threadedssh(nodes, """
        # skip if we already have libzmq:
        test -f /usr/local/lib/libzmq.so && exit 0
        # install libuuid with headers
        apt-get -y install uuid-dev
        cd ~/src
        wget -nc http://download.zeromq.org/zeromq-2.1.7.tar.gz
        tar -xzf zeromq-2.1.7.tar.gz
        cd zeromq-2.1.7
        ./configure
        make
        make install
        # update ldconfig for unconfigured pyzmq
        ldconfig
        cd
        """)
        log.info("Installing pyzmq on %s"%dest)
        threadedssh(nodes, "easy_install 'pyzmq>=2.1.7'")
        
    def run(self, nodes, master, user, user_shell, volumes):
        tic = time.time()
        self.install_packages(nodes)
        
        mins = (time.time()-tic)/60.
        log.info("Building & installing pyzmq & dependencies took %.2f mins"%(mins))
    
    def on_add_node(self, node, nodes, master, user, user_shell, volumes):
        self.install_packages([node], node.alias)

