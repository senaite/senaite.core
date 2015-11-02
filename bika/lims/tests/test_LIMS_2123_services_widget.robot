*** Settings ***

Library         BuiltIn
Library         Selenium2Library  timeout=5  implicit_wait=0.2
Library         String
Resource        keywords.txt
Library         bika.lims.testing.Keywords
Resource        plone/app/robotframework/selenium.robot
Library         Remote  ${PLONEURL}/RobotRemote
Variables       plone/app/testing/interfaces.py
Variables       bika/lims/tests/variables.py

Suite Setup     Start browser
Suite Teardown  Close All Browsers

Library          DebugLibrary

*** Variables ***

*** Test Cases ***

Check that ajax_categories function in ServicesWidget.
    [Documentation]   Worksheets
    ...  Groups analyses together for data entry, instrument interfacing,
    ...  and workflow transition cascades.
    Enable autologin as  LabManager
    Set autologin username   test_labmanager
    go to  ${PLONEURL}/bika_setup/bika_worksheettemplates/worksheettemplate-1
    # First check that services in the the expanded category Metals, are saved
    click link   fieldsetlegend-analyses
    select checkbox   xpath=.//input[@alt='Iron']
    select checkbox   xpath=.//input[@alt='Copper']

    # Add one from Microbiology category
    click element     xpath=.//th[@cat='Microbiology']
    select checkbox   xpath=.//input[@alt='Ecoli']

    click button     save
    wait until page contains element   css=#fieldsetlegend-analyses
    click link   fieldsetlegend-analyses
    checkbox should be selected   xpath=.//input[@alt='Iron']
    checkbox should be selected   xpath=.//input[@alt='Copper']
    checkbox should be selected   xpath=.//input[@alt='Ecoli']

*** Keywords ***
