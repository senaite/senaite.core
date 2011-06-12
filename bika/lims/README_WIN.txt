Installing Bika LIMS 2 Inkosi on Windows

Bika LIMS 2 installation guide for Windows. Tested with XP Pro 5.1
------------------------------------------------------------------

Document Version 1.0, 26 May 2008
Updated versions, including screen shots, at 
http://www.bikalabs.com/helpcentre/manual/bika-installation-guides/bika-on-windows/installing-bika-lims-2-0


Requirements
------------

    Plone 2.5

    Zope 2.9

    Python 2.4

Tested with Plone 2.5.3 and Zope 2.9.7


Installation guide
------------------

At this stage Plone must be installed already, see the Win Plone installation page

There are several Bika Products listed at http://sourceforge.net/project/showfiles.php?group_id=145464

         1. If you want to install Bika LIMS 2 Inkosi, then download the Bika package in the archive format that suits you best

         2. There are two types of packages:

            Bika only
            ---------

            E.g. bika-2_1.rar - this archive only contains the Bika products, but not Bika dependent products. Only download if you already have a Bika installation. Make sure your Bika dependent products are up to date

            Bika Product Bundle, bika-2_1_bundle. rar - this archive contains
            --------------------

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

                * _renderPM 0.99                   Win32dlls-py24
                * Reportlab - version 1.19     
                * ReportlabFonts                    Adobe fonts required by Reportlab

           

         3. Extract the downloaded archive to a temporary folder

            Copy the folders in the Plone Products directory to the Products folder of your Zope instance

            Assuming you have the same set-up described in the Plone installation page, this would be C:\Program Files\Plone 2\Data\Products


         4. ID server
            ---------

            Nemesis, take special care

            Copy start-id-server.bat
            from   C:\Program Files\Plone 2\Data\Products\bika\scripts
            to       C:\Program Files\Plone 2\Data

            If necessary, edit start-id-server.bat for the PYTHON and BIKA_BASE variables to reflect your installation. If you kept to the recommended folder paths and names, everything should be fine:

            @set PYTHON=C:\Program Files\Plone 2\Python\python.exe
            @set BIKA_BASE=C:\Program Files\Plone 2\Data
            @set COUNTER_FILE=%BIKA_BASE%\var\idserver.counter
            @set LOG_FILE=%BIKA_BASE%\var\idserver.log
            @set PID_FILE=%BIKA_BASE%\var\idserver.pid
            @set SCRIPT=%BIKA_BASE%\Products\bika\scripts\id-server.py
            @set PORT=8081

            "%PYTHON%" "%SCRIPT%" -f "%COUNTER_FILE%" -p "%PORT%" -l "%LOG_FILE%" %1 %2 %3 %4 %5 %6 %7

         5. Edit zope.conf, in C:\Program Files\Plone 2\Data\etc\zope.conf

            Edit the <Environment> paragraph in the Environment directive, to include the ID Server address

            Maintain the HTTP_MANAGE $ZOPE_MANAGEZODB_PORT setting

            <environment>
            HTTP_MANAGE $ZOPE_MANAGEZODB_PORT
            IDServerURL http://localhost:8081
            </environment>

         6. Graphics
            --------

            Bika 2 QC graphs require Reportlab, http://www.reportlab.org/

            If you installed the Bika Bundle, RenderableCharts will be in 
            your Product directory c:\Program Files\Plone 2\Data\Products

            i) Copy the extracted reportlab folder to Python, into a reportlab - all lower case - 
            folder e.g. C:\Program Files\Plone 2\Python\Lib\reportlab.
            MANIFEST.txt should be in c:\Program Files\Plone 2\Python\Lib and 
            rl_config.py should be inside 
            c:\Program Files\Plone 2\Python\Lib\reportlab

            ii) Copy the ReportlabFonts to a directory of your choice, e.g. C:\ReportlabFonts

            iii) In the reportlab folder, edit rl_config.py and add the 
            ReportlabFonts path to the T1SearchPath parameter, e.g. 
                # places to look for T1Font information
                T1SearchPath =  ('C:/ReportlabFonts',
                                'c:/Program Files/Adobe/Acrobat 6.0/....

            iv) Copy _renderPM dlls  from renderPM_Win32dlls-py24 to python,
            to C:\Program Files\Plone 2\Python\DLLs

            v) Test. Once your Bika installation is complete, navigate to 
             http://localhost:8080/bika/test_install

            It should display a test image of a bell curve and texts

            See the test image at http://www.bikalabs.com/testinstall
            

         7. Run 'runzope.bat' from C:\Program Files\Plone 2\Data\bin

            or

            Run the Plone Control panel which you can find from Start -> Programs -> Plone -> Plone

            Click on the Start button

            Click on the 'Zope Management Interface' button, and the ZMI should open up in a new browser window

         8. Start the IDServer from C:\Program Files\Plone 2\Data
            Test by browsing to http://localhost:8081/ - if running it will display a number, and will increment it with every reload

         9. [Skip this step if you used the Plone Controller]
            Open Browser, go to ZMI, typically http://localhost:8080/manage

        10. ZMI: a pop-up will appear requesting your login and password
         

        11. Assuming you have the same set-up described in the Plone installation page, this would be

            Login: admin
            Password: local

        12. Following successful authentication you should see the infamous Zope Management Interface or ZMI

        13. Select 'Plone site' from the 'Add' drop down menu

        14. On the following screen:

            Specify the site's id - its short name, part of site's address, e.g. 'bika', Title, say 'Bika LIMS Portal' and Description of your choice

            Select 'bika' from the 'Extension Profiles' at the bottom of the form

            Click the [Add Plone Site] button

        15. You should be automatically redirected to the Zope Management Interface (ZMI), listing your new Bika instance

        16. Click on you bika instance, and then click on the 'View' tab to see bika full screen. Or alternatively, open a new browser window or tab, and enter the following address: http://localhost:8080/bika

        17. Uploading demonstration data

            If you want to populate your Bika LIMS with sample data, login into bika as administrator, and enter the following address in your browser:
            http://localhost:8080/bika/load_sample_data

            NOTE: Make sure your IDServer is running!

        18. This will take several seconds, and will be followed by a blank screen with 'Ok' in the top left

        19. Use the browser's back button to return to the Bika LIMS


If you have any trouble with the above installation procedure, please join the Bika users mailing list and report any problems you might have.

http://lists.sourceforge.net/lists/listinfo/bika-users