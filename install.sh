#!/bin/bash
#
# Original script by Inus Scheepers (inus@bikalabs.com),
# Proxy handling and Fedora suppot added
# by Pieter vd Merwe pieter_vdm@debortoli.com.au
# Updated to Plone 4.3.3 on 10 Jun 2014 by Inus Scheepers
# Also see https://github.com/bikalabs/Bika-LIMS/wiki/Bika-LIMS-Installation 
# Bika LIMS Installation
# ----------------------
#
# This document describes the installation of Bika LIMS
# on Ubuntu/Fedora Linux, using the Plone Unified Installer package.

# ## Configure environment.
# Change the following values if you are installing to a different directory
# or a using an internet proxy

# The target installation directory
BIKA_HOME=/home/bika

PLONE_VERSION=4.3.3

# If a proxy is used, set this value.
# PROXY=http://user:password@proxy1:80

# Script check.  You need to run this script as root
if [ ! $UID -eq 0 ]; then
  echo "Script must be run as root"
  echo "Try: sudo `basename $0`"
  exit 1
fi

# Set the linux proxy environment variables.  It may alread have been set
# but the sudo setup may not be configured to pass it along.
if [ -n "${PROXY}" ]; then
  export http_proxy=${PROXY}
  export https_proxy=${PROXY}
fi

# ## Download and install Plone
#
# The latest Unified Installer can be found at http://plone.org/products/plone/releases
# Plone 4 or newer is required. Bika has been tested with Plone 4.3.
#
# All steps are required except where marked as optionally. If your installation fails,
# ensure that each step has completed successfully.
#
# ## Install server (Linux) dependencies
#
# The following commands are as used for Ubuntu 12.04 and Fedora 17.
# Use a package manager to install the needed dependencies:
# (apt-get is an alternative to yum)

if [ -f /etc/lsb-release ]; then # Ubuntu
  aptitude install gcc
  aptitude install zlib1g-dev
  aptitude install libssl-dev
  aptitude install gnuplot
  aptitude install git-core

  # WeasyPrint dependencies:
  # http://weasyprint.org/docs/install/#debian-ubuntu
  aptitude install libffi-dev
  # Debian 7.0 Wheezy or newer, Ubuntu 11.10 Oneiric or newer:
  aptitude install libcairo2
  aptitude install libpango1.0-0
  aptitude install libgdk-pixbuf2.0-0
  #Debian 6.0 Squeeze, Ubuntu 10.04 Lucid
  aptitude install libgtk2.0-0
else
  if [ -f /etc/redhat-release ]; then # Fedora
    yum install gcc zlib-devel openssl-devel gnuplot git-core wget patch

    # WeasyPrint dependencies:
    # see http://weasyprint.org/docs/install/#fedora
    yum install libcairo2 libpango1.0-0 libgdk-pixbuf2.0-0 libffi-dev
  fi
fi

# ## Download and install the Plone UnifiedInstaller

# Retrieve the unified installer and run the install shell script.
# The "dev" branch is used in this case. Omit the "-b dev" argument
# to use the master branch instead.

mkdir -p $BIKA_HOME
wget -nc  --no-check-certificate  "https://launchpad.net/plone/4.3/$PLONE_VERSION/+download/Plone-$PLONE_VERSION-UnifiedInstaller.tgz"
tar xzf Plone-$PLONE_VERSION-UnifiedInstaller.tgz
cd Plone-$PLONE_VERSION-UnifiedInstaller/
./install.sh --build-python --static-lxml=yes  --target=${BIKA_HOME} standalone

# Visit http://plone.org/documentation/topic/Installation for more
# information about setting up Plone if the above fails.

# ## Change to the new Plone instance directory

cd ${BIKA_HOME}/zinstance

# If the proxy isn't set for git, set it.  The linux
# environment variables should be enough, but it didn't work on fedora.
if [ -n "$PROXY" ] && [ -z "`git config --get http.proxy`" ]; then
  sudo -u plone_buildout git config --global http.proxy ${PROXY}
fi

# At this point a plain Plone instance could be built and run.
# This is a good intermediary checkpoint in case of any system
# issues or installation problems. Refer to http://Plone.org
# if this step fails.

# ## (Option) Retrieve the development branch Bika code

#git clone -b dev https://github.com/bikalabs/Bika-LIMS.git src/bika.lims
#git clone -b release/3.1 http://github.com/bikalabs/Bika-LIMS.git src/bika.lims
sudo -u plone_buildout git clone -b 3.1 http://github.com/bikalabs/Bika-LIMS.git src/bika.lims
#    Omit the command line switch '-b dev' to use the master branch instead.

# ## Edit Plone/zinstance/buildout.conf and add Bika LIMS.

# Find the "eggs" section and add "bika.lims"
#
#     eggs =
#         ...
#         bika.lims
#         WeasyPrint

python -c 'open("buildout.1","w").write("".join([line.replace("    Pillow", "    Pillow\n    bika.lims") for line in open("buildout.cfg").readlines()]))'
mv buildout.1 buildout.cfg
python -c 'open("buildout.1","w").write("".join([line.replace("    Pillow", "    Pillow\n    WeasyPrint") for line in open("buildout.cfg").readlines()]))'
mv buildout.1 buildout.cfg

#and 'WeasyPrint = 0.19.2'
# in [versions] section
python -c 'open("buildout.1","w").write("".join([line.replace("[versions]", "[versions]\nWeasyPrint = 0.19.2") for line in open("buildout.cfg").readlines()]))'
mv buildout.1 buildout.cfg

### (Option) - Use the latest source code instead of the PYPI egg
# Find the "develop" section and add "src/bika.lims" to it
#
#   develop =
#        src/bika.lims

python -c 'open("buildout.2","w").write("".join([line.replace("develop =", "develop =\n     src/bika.lims") for line in open("buildout.cfg").readlines()]))'
mv buildout.2 buildout.cfg


### Run buildout

sudo -u plone_buildout bin/buildout

# Some non-fatal error messages may scroll past

### Start Plone

# Start the Plone instance in foreground (debug) mode which will
# display the instance log on the console.

sudo -u plone_daemon bin/plonectl fg

# Alternatively, start it as a normal server process:

# bin/plonectl start

# The log should indicate that the Zope server is ready to serve
# requests, and the port. If it does not start up, ensure that a
# server is not already using the chosen port.
#
# You may track the instance log for a server process by running
#
# tail -f var/log/instance.log

### Add a new Plone instance with the Bika LIMS extension:

# Assign an ID of your choice, and select the checkbox to activate the
# Bika-LIMS extension profile. The 'title' field is optional.
#
# To add Bika LIMS to an existing Plone site, visit the Addons page
# of Site Setup or the quickinstaller.

# IMPORTANT: Don't use "Bika" or "BIKA" as the instance name, this is a
# reserved namespace. If you get "Site Error" citing "AttributeError: adapters",
# this is the most likely cause.

### Removing the installed database and starting fresh

# In case you need to start with a clean slate, (re)move the Data.fs files.
# This will remove all Plone instances, and WILL DESTROY all entered data.
# The Plone and Bika code will not be affected.

# rm -f var/filestorage/*

# In this case, or if you have problems logging in, you might need to
# initialize the Plone database with an admin user:

# bin/plonectl adduser admin password

# That's it!

### Visit the site in your Browser
# You should be able to test the site now by visiting

# http://localhost:8080/Plone
# or, for the really lazy:
# http://admin:password@localhost:8080/Plone

# If you need to visit the ZMI, use

# http://localhost:8080/manage

# If no Plone object exists, add one and tick the "Bika LIMS" extension.
# (Note that "Bika" may not work as an instance name, see above.)

# You can edit the code in src/bika.lims and restart the instance to
# make the changes take effect. It should not affect the installed databases.
# Changing the CSS does not require the instance to be restarted.
#
# Once logged in, you will be given the option to load a test laboratory
# setup via a link on the front page. To verify, select a client from the
# left-hand portlet, add an Analysis Request, and fill in the fields.
# Progress the AR through reception, results entry, verification/retraction
# and publication phases. Note that the mail server setup, in "Site Setup"
# at the top righthand, needs to be completed before mail can be delivered.

#### Error code encountered in case the code for "bika.lims" not installed


# If you encounter the message "AttributeError: type object 'IIdServer' has no attribute '__iro__'"
# it may mean that the Bika lims code was not included, neither as egg
# or as source code, while the Bika objects are in the Plone database.
#

#
#### Adding Plone proxying to Apache setup for port 80  HTTP service

# Find the apache virtual host entry, by default in Ubuntu in
# /etc/apache2/sites-enabled/000-default and add the following:

# <Virtualhost *:80>
# ...
#  <Proxy *>
#     Order deny,allow
#     Allow from all
#   </Proxy>

#   Proxypass / http://localhost:8080/
#   ProxypassReverse / http://localhost:8080/

# </VirtualHost>

# You would also need to enable the module for the stock Ubuntu
# installation of apache:

# a2enmod proxy

# Restart apache to effect changes:

# apache2ctl restart

# You may now visit http://server/Plone (or your chosen instance name).

#### Adding Plone server to the system startup

# Add the following line to  /etc/rc.local, before
# the "exit 0" line, adjusting for the target directory name:

# /home/bika/zinstance/bin/plonectl start

# Test by rebooting the server and verification by visiting the
# URL by browser to check if the site is accessible.
#
# Thank for you reading the entire document, you may run this
# installation on a new Ubuntu installation via bash as follows
#
# bash ./installation.txt
#
# The end.
#
# (Reuploaded on 26 Feb 2013 after it got clobbered)tion on a new Ubuntu installation via bash as follows
#
# bash ./installation.txt
#
# The end.
#
# (Reuploaded on 26 Feb 2013 after it got clobbered)
