Bika LIMS
============

Installation
------------

Documenting the bika3 installation as done on Debian server 13/11/11.

#. Get the latest Unified Installer: http://plone.org/products/plone/releases

#. Copy link, and wget it on your server::

    wget http://launchpad.net/plone/4.1/4.1.2/+download/Plone-4.1.2-UnifiedInstaller.tgz

#. Untar::

    tar xzf Plone-4.1.2-UnifiedInstaller.tgz

#. Run installer and point to new target direction::

    sudo ./install.sh --target=/home/example  standalone

#. Make new DYN name for site and add apache mapping on server, noting new
   port for instance - Add ``A`` or ``CNAME`` record, if needed.

   Edit the apache configuration, adding a new virtual host::

    sudo vim /etc/apache2/sites-enabled/000-default

   Add the following, ensure an existing port is not conflicted::

     <VirtualHost *:80>
          ServerName  example.bikalabs.com
          ServerAdmin webmaster@bikalabs.com
          ErrorLog /var/log/apache2/example.bikalabs.com.error.log
          LogLevel warn
          CustomLog /var/log/apache2/example.bikalabs.com.access.log combined
          RewriteEngine On
          RewriteRule ^/robots.txt -  [L]
          RewriteRule ^/manage(.*) http://localhost:8030/VirtualHostBase/http/example.bikalabs.com:80/VirtualHostRoot/manage$1 [L,P]
          RewriteRule ^/(.\*) http://localhost:8030/VirtualHostBase/http/example.bikalabs.com:80/VirtualHostRoot/$1 [L,P]
     </VirtualHost>

#. Note the output of the installer script::

    ######################  Installation Complete  ######################

    Plone successfully installed at /home/example
    See /home/example/zinstance/README.html
    for startup instructions

    Use the account information below to log into the Zope Management Interface
    The account has full 'Manager' privileges.

    Username: admin
    Password: password
    ...

#. Edit ``/home/example/zinstance/buildout.cfg``.

   a. Find the ``eggs`` section.  Add ``bika.lims``::

       eggs =
           Plone
           Pillow
           lxml
           bika.lims

   b. Find the ``develop`` section. Add ``src/bika3``::

       develop =
         src/bika3

   c. Change the port to the one used in Apache above (8030)::

       http-address = 8030

   d. Change the effective user if not id plone. (Optional.)

      Add the ``Environ`` variable for ID-server, noting port number for shell
      script later::

       [instance]
       environment-vars =
           IDServerURL http://localhost:8031

#. Check out the bika3 code::

    cd /home/example/zinstance

   a. With SVN::

       sudo svn co https://bika.svn.sourceforge.net/svnroot/bika/bika3 src/bika3

   b. From Git::

       git clone https://github.com/bikalabs/Bika-LIMS src/bika3

#. Do the buildout of the instance::

    sudo bin/buildout -v

#. Create an ``idserver`` start script, similar to below: Use the
   python from the ``bin/plonectl`` script::

    #!/bin/sh
    PYTHON=/home/exmple/Python-2.6/bin/python
    BIKA_BASE=/home/example/zinstance
    COUNTER_FILE=$BIKA_BASE/var/id.counter
    LOG_FILE=$BIKA_BASE/var/log/idserver.log
    PID_FILE=$BIKA_BASE/var/idserver.pid
    PORT=8031

    SRC_DIR=src/bika3

    exec $PYTHON $BIKA_BASE/$SRC_DIR/bika/lims/scripts/id-server.py \
            -f $COUNTER_FILE \
            -p $PORT \
            -l $LOG_FILE \
            -d $PID_FILE

#. Make it exectuable and test::

    sudo chmod +x start-idserver.sh
    sudo su plone -c "./start-idserver.sh"
    lynx http://localhost:8031/

   A "1" should appear, incrementing on reloads. A different browser can also
   be used from another server, if needed. Note port.

#. Make a ``stop-idserver`` script::

    #!/bin/sh
    kill ``cat var/idserver.pid``

#. Test and reload apache config, if new server name DNS is ready::

    sudo apache2ctl configtest
    dig example.bikalabs.com
    sudo apachectl graceful

#. Remove ``id.counter`` file to reset, and restart: (optional)::

    sudo ./stop-idserver.sh
    sudo rm var/id.counter
    sudo su plone -c ./start-idserver.sh

#. Test run in foreground, noting error messages::

    sudo bin/plonectl fg

    ...

    2011-11-13 12:06:07 INFO Zope Ready to handle requests


#. Access via Web::

    http://admin:password@example.bikalabs.com/manage

   or::

    http://admin:password@localhost:8030/manage

#. Add Plone site, noting Instance name (default Plone), and ensure to tick Bika LIMS option

#. Modify apache config to point to instance "Plone" root instead of Zope root if required::

    #RewriteRule ^/(.*) http://localhost:8030/VirtualHostBase/http/example.bikalabs.com:80/VirtualHostRoot/$1 [L,P]

    RewriteRule ^/(.*) http://localhost:8030/VirtualHostBase/http/example.bikalabs.com:80/Plone/VirtualHostRoot/$1 [L,P]

   Reload config::

    sudo apache2ctl graceful

#. Stop foreground instance (Control C), restart as process and optionally add to server startup scripts::

    sudo bin/plonectl start

   Add similar as below to ``/etc/rc.local`` or equivalent::

    su plone -c  /home/example/zinstance/start-idserver.sh
    /home/example/zinstance/bin/plonectl start

#. Test on subdomain name URL as above.
