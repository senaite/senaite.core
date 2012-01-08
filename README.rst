Bika LIMS
============

Installation
------------

Documenting the bika3 installation as done on Debian server 13/11/11. Updated
for changes affecting ID-Server, which is now by default automatically built
and started in the instance. This document describes the manual
steps to install the LIMS and set up Apache as proxy on port 80. See 
https://github.com/bikalabs for other install options, especially 
https://github.com/bikalabs/Bika-3-Buildout which automates most
of the steps below and also installs the Plone instance.

#. Get the latest Unified Installer: http://plone.org/products/plone/releases

#. Copy link, and wget it on your server::

    wget http://launchpad.net/plone/4.1/4.1.2/+download/Plone-4.1.2-UnifiedInstaller.tgz

#. Untar::

    tar xzf Plone-4.1.2-UnifiedInstaller.tgz

#. Run installer and point to new target direction::

    sudo ./install.sh --target=/home/example  standalone

#. (Optional) Set up a domain name for the LIMS site and add the Apache mapping on 
   the http-server, noting the port for instance (default 8080) - Add ``A`` or ``CNAME`` record, if needed.

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
    Password: password
    ...

#. Edit ``/home/example/zinstance/buildout.cfg``.

   a. Find the ``eggs`` section.  Add ``bika.lims``::

       eggs =
           Plone
           Pillow
           bika.lims

   b. Find the ``develop`` section. Add ``src/bika3``::

       develop =
         src/bika3

   c. (Optional) Change the port to the one used in Apache above (8080)::

       http-address = 8080

   d. (Optional) Change the effective user if not id plone. 

   e. (Optional) Add the ``Environ`` variable for ID-server, noting port number for shell
      script later::

       [instance]
       environment-vars =
           IDServerURL http://localhost:8081

#. Check out the bika3 code::

    cd /home/example/zinstance
    git clone https://github.com/bikalabs/Bika-LIMS src/bika3

#. Do the buildout of the instance::

    sudo bin/buildout -v

#. Test and reload apache config, if new server name DNS is ready::

    sudo apache2ctl configtest
    dig example.bikalabs.com
    sudo apachectl graceful

#. Test run in foreground, noting error messages::

    sudo bin/plonectl fg

    ...

    2011-11-13 12:06:07 INFO Zope Ready to handle requests


#. Access via Web::

    http://admin:password@example.bikalabs.com/manage

   or::

    http://admin:password@localhost:8080/manage

#. Add Plone site, noting Instance name (default Plone), and ensure to tick Bika LIMS option

#. (Optional) Modify apache config to point to instance "Plone" root instead of Zope root if required::

    #RewriteRule ^/(.*) http://localhost:8080/VirtualHostBase/http/example.bikalabs.com:80/VirtualHostRoot/$1 [L,P]

    RewriteRule ^/(.*) http://localhost:8080/VirtualHostBase/http/example.bikalabs.com:80/Plone/VirtualHostRoot/$1 [L,P]

   Reload config::

    sudo apache2ctl graceful

#. Stop foreground instance (Control C), restart as process and optionally add to server startup scripts::

    sudo bin/plonectl start

   Add similar as below to ``/etc/rc.local`` or equivalent::

    /home/example/zinstance/bin/plonectl start

#. Test on subdomain name URL as above.
