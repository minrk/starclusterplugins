"""A plugin for installing the dependencies for IPython parallel computing
in version 0.11

Installed: 
* uuid-dev from apt
* zeromq-2.1.7
* pyzmq-2.1.7.1

Upgraded:
* Cython (to >= 0.13)
* IPython (to git master, 0.10 is also removed)

Packages are downloaded/installed in threads, allowing for faster installs
when using many nodes.


"""
import time
import thread
from threading import Thread

from starcluster.clustersetup import ClusterSetup
from starcluster.logger import log

def threadedssh(nodes, cmd, join=True):
    """Run a command via ssh simultaneously on all nodes."""
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
    def run(self, nodes, master, user, user_shell, volumes):
        log.info("Installing IPython and dependencies")
        tic = time.time()
        threadedssh(nodes, "test -d ~/src || mkdir ~/src")
        log.info("Updating Cython on all nodes")
        cythons = threadedssh(nodes, "easy_install 'cython>=0.13'", join=False)
        log.info("Installing zeromq-2.1.7 on all nodes")
        libzmqs = threadedssh(nodes, """
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
        """, join=False)
        log.info("Fetching IPython from github on all nodes")
        ipythons = threadedssh(nodes, """
        # get IPython from GitHub
        cd src
        test -d ipython || git clone git://github.com/ipython/ipython.git
        cd
        """, join=False)
        log.info("Waiting for Cython update threads...")
        [t.join() for t in cythons]
        log.info("Waiting for zeromq install threads...")
        [t.join() for t in libzmqs]
        log.info("Installing pyzmq on all nodes")
        threadedssh(nodes, "easy_install 'pyzmq>=2.1.7'")
        log.info("Waiting for IPython download threads...")
        [t.join() for t in ipythons]
        log.info("Installing IPython master on all nodes")
        threadedssh(nodes, """
        # install pip for uninstall to be available
        easy_install 'pip>=1.0'
        pip uninstall -y ipython
        # install IPython
        cd ~/src/ipython
        python setupegg.py install
        # rehash PATH
        hash -r
        """, join=True)
        
        mins = (time.time()-tic)/60.
        log.info("IPython & dependencies took %.2f mins"%(mins))
        
