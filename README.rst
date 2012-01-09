Bika LIMS
============
This document describes the installation of Bika LIMS.
The ID-Server is now by default automatically built
and started as part of the Zope/Plone instance. 

See https://github.com/bikalabs for other install options, especially 
https://github.com/bikalabs/Bika-3-Buildout which automates most
of the steps below and also installs the Plone instance.

Installation
------------
This document details the installation steps for Bika LIMS version 3 
from the Unified Installer package as basis, as installed
on Linux, as well as the setup for Apache as web proxy to make 
the LIMS available on the standard http port 80. The process should be
similar for MacOSX and other Unix-type operating systems.


#. Get the latest Unified Installer: http://plone.org/products/plone/releases

#. Copy the link for the required version, and download it (eg. using wget)::

    wget http://launchpad.net/plone/4.1/4.1.2/+download/Plone-4.1.2-UnifiedInstaller.tgz

#. Untar the archive::

    tar xzf Plone-4.1.2-UnifiedInstaller.tgz

#. Run installer and point to new target direction::

    sudo ./install.sh --target=/home/example  standalone

#. (Optional) Set up a domain name::
   Set up the chosen domain name for the LIMS site, and add the Apache mapping on 
   the http-server, noting the Zope server port for instance (default 8080) 

   Edit the apache configuration, adding a new virtual host::

    sudo vim /etc/apache2/sites-enabled/000-default

   Add directives, ensuring an existing port is not conflicted::

     <VirtualHost *:80>
          ServerName  example.bikalabs.com
          ServerAdmin webmaster@bikalabs.com
          ErrorLog /var/log/apache2/example.bikalabs.com.error.log
          LogLevel warn
          CustomLog /var/log/apache2/example.bikalabs.com.access.log combined
          RewriteEngine On
          RewriteRule ^/robots.txt -  [L]
          RewriteRule ^/manage(.*) http://localhost:8080/VirtualHostBase/http/example.bikalabs.com:80/VirtualHostRoot/manage$1 [L,P]
          RewriteRule ^/(.\*) http://localhost:8080/VirtualHostBase/http/example.bikalabs.com:80/VirtualHostRoot/$1 [L,P]
     </VirtualHost>

#. Note the output of the installer script::

    ######################  Installation Complete  ######################

    Plone successfully installed at /home/example
    See /home/example/zinstance/README.html
    for startup instructions

    Use the account information below to log into the Zope Management Interface
    The account has full 'Manager' privileges.

    Username: admin
    Password: admin
    ...

#. Edit the buildout configuration, eg ``/home/example/zinstance/buildout.cfg``::

   a.) Find the ``eggs`` section.  Add ``bika.lims``::

       eggs =
           Plone
           Pillow
           bika.lims

   b.) Find the ``develop`` section. Add ``src/bika3``::

       develop =
         src/bika3

   c.) (Optional) Change the port to the one used in Apache above (8080)::

       http-address = 8080

   d.) (Optional) Change the effective user if not id plone. 

   e.) (Optional) Add the environment-vars stanza for the ID-server, noting port number::

       [instance]
       environment-vars =
           IDServerURL http://localhost:8081

#. Check out the bika3 code::

    cd /home/example/zinstance
    git clone https://github.com/bikalabs/Bika-LIMS src/bika3

#. Do the (verbose) buildout of the instance::

    sudo bin/buildout -v

#. (Optional) Test and reload apache config::

    sudo apache2ctl configtest
    dig example.bikalabs.com
    sudo apachectl graceful

#. Test run in foreground, noting error messages if any and making corrections::

    sudo bin/plonectl fg

    ...

    2011-11-13 12:06:07 INFO Zope Ready to handle requests


#. Access the Zope instance via a web browser

    http://admin:admin@example.bikalabs.com/manage

   alternatively if on localhost, 

    http://admin:admin@localhost:8080/manage

#. Add a new Plone instance::

   If not automatically created by the buildout process yet, add a Plone instance while
   noting the instance name (default Plone, or Bika) and ensure that the Bika LIMS option is ticked.

a). (Optional) Modify Apache web server configuration to point to instance "Plone" or "Bika" root instead of Zope root if required::

    #RewriteRule ^/(.*) http://localhost:8080/VirtualHostBase/http/example.bikalabs.com:80/VirtualHostRoot/$1 [L,P]

    RewriteRule ^/(.*) http://localhost:8080/VirtualHostBase/http/example.bikalabs.com:80/Plone/VirtualHostRoot/$1 [L,P]

   Reload the Apache webserver with new configuration::

    sudo apache2ctl graceful

b). (Optional) Stop the foreground instance (Control C), and restart it as a background process. 
    Add it to server startup scripts to start Plone on reboot::

    sudo bin/plonectl start

   Add similar as below to ``/etc/rc.local`` or equivalent::

    /home/example/zinstance/bin/plonectl start

