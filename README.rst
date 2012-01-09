Bika LIMS
============
This document describes the installation of Bika LIMS 
(Laboratory Information Management System) on a Unix server.
The ID-Server is now by default automatically built
and started as part of the Zope/Plone instance but can
optionally still be deployed in a clustering setup. 

See https://github.com/bikalabs for other install options, especially 
https://github.com/bikalabs/Bika-3-Buildout which automates most
of the steps below and also installs the /Bika Plone instance.

Installation
------------
This document details the installation steps for Bika LIMS version 3 
from the Plone Unified Installer package for Linux, as well as the 
setup for Apache as web proxy to make the LIMS available on the 
standard http port 80. The process should be similar for MacOSX and
other Unix-type operating systems. The gcc compiler, python2.6, 
the python-dev library and git is required and you could use that
already installed on your operating system.

#. Download the Unified Installer from plone.org::

    From http://plone.org/products/plone/releases copy the link for the
    required version (tested on 4.1.2), and download it, eg. using wget
    from http://launchpad.net/plone/4.1/4.1.2/+download/Plone-4.1.2-UnifiedInstaller.tgz

#. Untar the archive an run the installer::

    tar xzf Plone-4.1.2-UnifiedInstaller.tgz
    cd Plone-4.1.2-UnifiedInstaller
    sudo ./install.sh --target=/home/example  standalone

#. (Optional) Set up a domain name::

    Set up a domain name for the LIMS site URL and add the Apache mapping
    noting the Zope server port used by the instance (default 8080) 

    Edit the apache configuration, adding a new virtual host 

   ``sudo vim /etc/apache2/sites-enabled/000-default``

   Add directives, ensuring an existing port is not conflicted::

    <VirtualHost *:80>
      ServerName  example.bikalabs.com
      ServerAdmin webmaster@bikalabs.com
      ErrorLog /var/log/apache2/example.bikalabs.com.error.log
      LogLevel warn
      CustomLog /var/log/apache2/example.bikalabs.com.access.log combined
      RewriteEngine On
      RewriteRule ^/robots.txt -  [L]
      RewriteRule ^/manage(.*) http://localhost:8080/VirtualHostBase/http/example.bikalabs.com:80 /VirtualHostRoot/manage$1 [L,P]
      RewriteRule ^/(.\*) http://localhost:8080/VirtualHostBase/http/example.bikalabs.com:80/VirtualHostRoot/$1 [L,P]
    </VirtualHost>

#. Verify successful build from the output of the installer script. Refer to http://plone.org if installation fails::

    ######################  Installation Complete  ######################

    Plone successfully installed at /home/example
    See /home/example/zinstance/README.html
    for startup instructions

    Use the account information below to log into the Zope Management Interface
    The account has full 'Manager' privileges.

    Username: admin
    Password: xyz
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

   c.) (Optional) Change the Zope instance port if the default 8080 is not used::

       http-address = 8080

   d.) (Optional) Change the ``effective-user`` if ``plone`` is not the one used. 

   e.) Add the environment-vars entry for the ID-server, noting port number::

       [instance]
       environment-vars =
           IDServerURL http://localhost:8081

   
#. Retrieve the bika3 source code::

    cd /home/example/zinstance
    git clone https://github.com/bikalabs/Bika-LIMS src/bika3

#. Do the (verbose, if needed) buildout of the instance::

    sudo bin/buildout -v

#. (Optional) Test and reload apache config::

    sudo apache2ctl configtest
    dig example.bikalabs.com
    sudo apachectl graceful

#. Test run in foreground, noting error messages if any and taking corrective action if so::

    sudo bin/plonectl fg

    ...

    2011-11-13 12:06:07 INFO Zope Ready to handle requests


#. Access the Zope instance::

   a.) via a web browser on public URL http://admin:admin@example.bikalabs.com/manage/ ::

   b.) or if on localhost at  http://admin:admin@localhost:8080/manage/ ::

#. Add the Plone instance with Bika LIMS extensions::

    If not automatically created by the buildout process yet, add a Plone instance,
    noting the instance name (default Plone, or Bika) and ensure that the Bika LIMS option is ticked.



#. (Optional) Modify Apache web server configuration to point to instance root::

    Point to the instance "Plone" or "Bika" root instead of Zope root if required
    by changing the Apache rewrite rule::

    #RewriteRule ^/(.*) http://localhost:8080/VirtualHostBase/http/example.bikalabs.com:80/VirtualHostRoot/$1 [L,P]
    RewriteRule ^/(.*) http://localhost:8080/VirtualHostBase/http/example.bikalabs.com:80/Bika/VirtualHostRoot/$1 [L,P]

     Reload the Apache webserver's configuration::

     sudo apache2ctl graceful

#. (Optional) Stop the foreground instance (Control C), and restart it as a background process. 
    Add it to server startup scripts to start Plone on reboot::

    sudo bin/plonectl start

    Add similar as below to ``/etc/rc.local`` or equivalent::

    /home/example/zinstance/bin/plonectl start

#. To update the Bika source code from the GitHub repository::

    Rename (or move) the src/bika3 directory or rerun the ``git clone`` or ``git pull`` command in 
    the source directory src/bika3, then re-run bin/buildout.

#. To start with a completely fresh instance::

    Rename/move the Data.fs.* files in var/filestorage (after stopping instance). 
