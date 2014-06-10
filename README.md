Bika Laboratory Information Management System

Installation
------------

1. Read https://plone.org/documentation/manual/installing-plone
2. Read https://plone.org/documentation/kb/installing-add-ons-quick-how-to
3. Install Plone and the "bika.lims" package

For unix-like systems, download and run the script that, if all goes well, should install the prerequisite Plone 4.3.3 and Bika LIMS in /home/bika and start the server in foreground on port 8080. 

  wget  -nc  --no-check-certificate  https://raw.githubusercontent.com/bikalabs/Bika-LIMS/develop/install.sh

  chmod +x install.sh

  sudo ./install.sh

Windows installations require Visual Studio 2008 correctly configured, and a normal python .MSI installation before 
buildout will compile cffi and cairo binaries. 

If you have questions, please post to one of our mailing lists:

* Users: http://lists.sourceforge.net/lists/listinfo/bika-users
* LIMS design: https://groups.google.com/forum/?hl=en#%21forum/bika-design
* Developers: http://lists.sourceforge.net/lists/listinfo/bika-developers

Please log issues, feature requests, or bug reports in the public issue
tracker at Github:

https://github.com/bikalabs/Bika-LIMS/issues

Bika Lab Systems
info@bikalabs.com
http://www.bikalabs.com
