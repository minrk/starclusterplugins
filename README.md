My StarCluster plugins

* ipythondev: installs IPython from git master
* pyzmq: two plugins
    1. EggSetup installs generic user-specified egg_url
    2. PyZMQSourceSetup builds and installs pyzmq and zeromq-2.1.7

* ipcluster: starts an IPython cluster with SGE, and fetches the connector file

The necessary config to get a new IPython cluster running:

<pre>
    # you need just one of these two for pyzmq:
    [plugin pyzmqegg]
    # as built by setupegg.py build bdist_egg --zmq=/usr/local (or similar)
    setup_class = pyzmq.EggSetup
    egg_url = http://my.example.com/pyzmq-2.1.7-py2.6-linux-x86_64.egg
    
    [plugin pyzmqsrc]
    setup_class = pyzmq.PyZMQSourceSetup
    
    [plugin ipythondev]
    setup_class = ipythondev.IPythonSetup

    [plugin ipcluster]
    setup_class = ipcluster.IPClusterSetup
    
    # now in your cluster, add:
    
    plugins = pyzmqegg, ipythondev, ipcluster
    # or if you don't have an egg
    plugins = pyzmqsrc, ipythondev, ipcluster
</pre>

