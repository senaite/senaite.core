Installing Bika LIMS 2 Inkosi on Linux
Tested with Ubuntu Gutsy Gibbon 7.10 and Hardy Heron 8.04
---------------------------------------------------------


Document Version 1.0,  26 May 2008
Updated versions, including screen shots,
 at http://www.bikalabs.com/helpcentre/manual/bika-installation-guides/bika-on-ubuntu-linux/installing-bika-lims-2-0


Requirements
------------

    Plone 2.5

    Zope 2.9

    Python 2.4

Tested with Plone 2.5.1 and Zope 2.9.5
   

Installation guide
------------------

At this stage Plone must be installed already, see the Linux Plone installation page

   1. Download Bika LIMS from: http://sourceforge.net/project/showfiles.php?group_id=145464

   2. If you want to install Bika LIMS 2 Inkosi, then download the Bika package in the archive format that suits you best

      There are two types of packages:

      Bika only
      bika-2_1.rar - This archive only contains the Bika products, but not Bika dependent products. Only download if you already have a Bika installation
      Make sure your Bika dependent products are up to date

      Bika Product Bundle, bika-2_1_bundle. rar - this archive contains
      Plone Products
          * ATExtensions - version 0.7.1
          * ATSchemaEditorNG - version 0.4.2
          * bika - version LIMS 2.1
          * BikaCalendar - version 1.0
          * PloneHelpCenter - version 0.9-Modified_by_Upfront
          * Portal Transport - version 1.1
          * RenderableCharts version 0.9.8
          * stripogram
          * Upfront Contacts - version 0.4
      Additional Products
          * Reportlab - version 1.19    
          * ReportlabFonts                    Adobe fonts required by Reportlab

      Extract the downloaded archive to a temporary folder

   3. Install Reportlab

      NB Ubuntu Hardy Users, specify reportlab be installed on the Python 2.4 instance. On Ubuntu 8.04 onwards, Python 2.5 is used by the OS, and Plone 2.5 uses Python 2.4

      If you can't find the re_config.py file, it is suggested you install Reporlab from source

      python2.4 setup.py install


   4. Copy the BikaFonts to a directory. e.g. /usr/local/lib/python2.4/site-packages/reportlab/fonts if Reportlab is installed here

   5. In Reportlab, e.g. /var/lib/zope2.9/instance/plone-site/Products/reportlab', edit rl_config.py, adding the BikaFonts path to the T1SearchPath parameter

      Example, depending on your installation, in /usr/local/lib/python2.4/site-packages/reportlab

      # places to look for T1Font information
      T1SearchPath =  '/usr/local/lib/python2.4/site-packages/reportlab/fonts', #Linux, Acrobat 8?
                      '/usr/local/Acrobat4', #Linux, Acrobat 4
                      '/usr/local/Acrobat5', #Linux, Acrobat 5?
                      '/usr/local/Acrobat7/Font', #Linux, Acrobat 5?
                      '%(REPORTLAB_DIR)s/fonts' #special
      )


   6. Copy the _renderPM directory to /var/lib/zope2.9/instance/plone-site/Products

   7. Copy the Bika Product package or Bika Product Bundle to the Products directory of your Zope instance, assuming you have the same set-up described in the Linux Plone installation page, this would be /var/lib/zope2.9/instance/plone-site/Products

         1. If you would like to create a separate instance for bika, rather then the default 'Plone Site', open your Command line editor and enter the following

            ~$ cd /usr/lib/zope2.9/bin/mkzopeinstance

         2. You will be prompted to give the instance a name, and access details

   8. ID server

      Before you start up your Zope instance, generally Zope starts automatically, you need to setup the ID server

      Copy the 'start-id-server' shell script from the BIKA products directory inside /var/lib/zope2.9/instance/plone-site/Products/bika/scripts to the root of your Zope instance, e.g. /var/lib/zope2.9/instance/plone-site

   9. Modify the path to the Python binary inside the 'start-id-server' shell script and change the port if necessary

  10. Edit the zope.conf file in your Zope instance /var/lib/zope2.9/instance/plone-site/etc and add an <environment> section for the ID Server:

      <environment>

      IDServerURL http://localhost:8081

      </environment>

  11. Re-start Zope and browse to the management interface at http://localhost:8080/manage. Provide your login and password

      Assuming you have the same set-up described in the Linux Plone installation page  this would be

      Login: admin
      Password: local

  12. Following successful authentication you should see the infamous Zope Management Interface or ZMI


  13. Select 'Plone site' from the 'Add' drop down menu

  14. Specify the id - its short name, part of site's address, e.g. 'bika', Title, say 'Bika LIMS Portal' and Description of your choice

      Select 'bika' from the 'Extension Profiles' at the bottom of the form

      Click the [Add Plone Site] button

  15. After this step you should be automatically redirected to the ZMI, listing your new Bika instance

  16. Click on your bika instance, and then click on the 'View' tab to see bika full screen

      Alternatively, browse to http://localhost:8080/bika

  17. Test. Once your Bika installation is complete, navigate to 
      http://localhost:8080/bika/test_install

      It should display a test image of a bell curve and texts

      See the test image at http://www.bikalabs.com/testinstall

      http://www.reportlab.org/

  18. Uploading Sample Data for bika

      If you want to populate your Bika LIMS with demonstration data, login into bika as administrator, and run a set-up script by navigating too http://localhost:8080/bika/load_sample_data

      The script will run for several seconds, and then load a  white screen with reading 'Ok' at top left

      NB. Make sure your IDServer is running!

      To run the IDServer on Ubuntu open your command line terminal and type

      ~$ su zope
      ~$ cd /var/lib/zope2.9/instance/plone-site
      ~$ ./start-id-server

  19. Use the browser's back button to return to the Bika LIMS


Important ID Server Notes
-------------------------

The IDServer, once run, is supposed to create the following files;

    /var/lib/zope2.9/instance/plone-site/log/id.counter
    /var/lib/zope2.9/instance/plone-site/log/idserver.log
    /var/lib/zope2.9/instance/plone-site/log/idserver.pid

If these files are NOT created when running the IDServer, it's most probably due to the access rights on the Zope's log folder /var/lib/zope2.9/instance/plone-site/log

Either change the rights to the log folder so that the files can be created

or

Create the files manually, but make sure they've got 'write' permissions

If you have any trouble with the above installation procedure, please join the Bika users mailing list and report any problems you might have

http://lists.sourceforge.net/lists/listinfo/bika-users

Additional Contribution to this document by

1) Sébastien DOVILLEZ - Magikal



Additional ReportLab installation notes
----------------------------------------

From the ReportLab README - additional information in the ReportLab installation package

Either unpack reportlab.zip or reportlab.tgz to some directory say d:\ReportLab. If you can, ensure that the line terminator style is correct for your OS (man zip programs have a text mode option eg -a)

Create a .pth file, say reportlab.pth in your Python home directory. It should have one line: e.g. /home/zope/plone/Products/ReportLab

Alternatively unpack the archive into a directory which is already on your python path


The Font Problem
----------------

On Linux, renderPM needs to know the locations of the following
fonts:

AdobeSansMM.MMM.pfb
AdobeSansMM.pfb
AdobeSerifMM.MMM.pfb
AdobeSerifMM.pfb
Arial-BoldItalic.pfb
Arial-Bold.pfb
Arial-Italic.pfb
Arial.pfb
Courier-BoldOblique.pfb
Courier-Bold.pfb
Courier-Oblique.pfb
Courier.pfb
Symbol.pfb
TimesNewRoman-BoldItalic.pfb
TimesNewRoman-Bold.pfb
TimesNewRoman-Italic.pfb
TimesNewRoman.pfb
ZapfDingbats.pfb

These fonts may be downloaded from:

http://bioinf.scri.ac.uk/lp/downloads/programs/genomediagram/linfonts.zip

The locations that ReportLab will look for these fonts are defined in
the file rl_config.py.  The relevant part of this file, at the time of
writing, looks like this: 

# places to look for T1Font information
T1SearchPath =  (
                'c:/Program Files/Adobe/Acrobat 6.0/Resource/Font', #Win32, Acrobat 6
                'c:/Program Files/Adobe/Acrobat 5.0/Resource/Font',     #Win32, Acrobat 5
                'c:/Program Files/Adobe/Acrobat 4.0/Resource/Font', #Win32, Acrobat 4
                '%(disk)s/Applications/Python %(sys_version)s/reportlab/fonts', #Mac?
                '/usr/lib/Acrobat5/Resource/Font',      #Linux, Acrobat 5?
                '/usr/lib/Acrobat4/Resource/Font',      #Linux, Acrobat 4
                '/usr/local/Acrobat6/Resource/Font',    #Linux, Acrobat 5?
                '/usr/local/Acrobat5/Resource/Font',    #Linux, Acrobat 5?
                '/usr/local/Acrobat4/Resource/Font',    #Linux, Acrobat 4
                '%(REPORTLAB_DIR)s/fonts',              #special
                '%(REPORTLAB_DIR)s/../fonts',           #special
                '%(REPORTLAB_DIR)s/../../fonts',        #special
                '%(HOME)s/fonts',                       #special
                 )

Placing the font files in any of these locations should be enough to
solve the problem.  Otherwise, you may need to edit the rl_config.py
file yourself to specify the appropriate location.