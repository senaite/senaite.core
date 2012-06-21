Apache configuration
====================

This document describes the the setup for Apache as web proxy to make the
LIMS available on the standard http port 80 for Unix/Linux servers.  The
process should be similar for MacOSX and other Unix-type operating systems.

Set up a domain name

    Set up a domain name for the LIMS site URL and add the Apache mapping
    noting the Zope server port used by the instance (default 8080)

    Edit the apache configuration, adding a new virtual host

   `sudo vim /etc/apache2/sites-enabled/000-default`

Add directives, ensuring an existing port is not conflicted::

    <VirtualHost*:80>
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

Test and reload apache config

    sudo apache2ctl configtest
    dig example.bikalabs.com
    sudo apachectl graceful

Test run in foreground, noting error messages if any and taking corrective action

    sudo bin/plonectl fg

Access the Zope instance via Apache

    Via a web browser on public URL http://admin:admin@example.bikalabs.com/manage/

Or via Zope:

    Or localhost address at http://admin:admin@localhost:8080/manage/

 Modify Apache web server configuration to point to instance root

    Point to the instance "Plone" or "Bika" root instead of Zope root if required
    by changing the Apache rewrite rule::

    #RewriteRule ^/(.*) http://localhost:8080/VirtualHostBase/http/example.bikalabs.com:80/VirtualHostRoot/$1 [L,P]
    RewriteRule ^/(.*) http://localhost:8080/VirtualHostBase/http/example.bikalabs.com:80/Bika/VirtualHostRoot/$1 [L,P]

Reload the Apache webserver's configuration::

    sudo apache2ctl graceful

Stop the foreground instance (Control C), and restart it as a background process.

    Add it to server startup scripts to start Plone on reboot::

    sudo bin/plonectl start

    Add similar as below to ``/etc/rc.local`` or equivalent::

    /home/example/zinstance/bin/plonectl start
