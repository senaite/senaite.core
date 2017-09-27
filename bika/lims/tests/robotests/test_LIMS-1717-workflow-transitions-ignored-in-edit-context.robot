*** Settings ***

Library         BuiltIn
Library         Selenium2Library  timeout=5  implicit_wait=0.2
Library         String
Resource        keywords.txt
Resource        plone/app/robotframework/selenium.robot
Library         Remote  ${PLONEURL}/RobotRemote
Variables       plone/app/testing/interfaces.py
Variables       bika/lims/tests/variables.py

Suite Setup     Start browser
Suite Teardown  Close All Browsers

Library          DebugLibrary

*** Variables ***

*** Test Cases ***

Test that workflow transitions invoked from /edit views take effect
    Enable autologin as  LabManager
    set autologin username  test_labmanager
    Disable stickers
    ${cat_uid} =  Get UID  catalog_name=bika_setup_catalog  portal_type=AnalysisCategory  title=Metals
    ${service_uid} =  Create Object   bika_setup/bika_analysisservices  AnalysisService  s1  title=AL396152  Keyword=Al396152  Category=${cat_uid}
    ${st_uid} =  Get UID  catalog_name=bika_setup_catalog  portal_type=SampleType  title=Bran
    ${sp_uid} =  Get UID  catalog_name=bika_setup_catalog  portal_type=SamplePoint  title=Mill
    ${ar_uid} =  Create AR  /clients/client-1  analyses=${service_uid}  SampleType=${st_uid}  SamplePoint=${sp_uid}
    # Now, we will browse to the AR's edit screen, and manually invoke the
    # workflow transition using the Plone UI.
    go to    ${PLONEURL}/clients/client-1/BR-0001-R01
    click element  css=.label-state-sample_due > a
    click element  css=#workflow-transition-receive
    wait until page contains   Changes saved.
    page should contain element  css=.label-state-sample_received


*** Keywords ***

Start browser
    Open browser                        ${PLONEURL}  chrome
    Set selenium speed                  ${SELENIUM_SPEED}

