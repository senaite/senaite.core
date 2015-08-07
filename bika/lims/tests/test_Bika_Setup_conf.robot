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

Test Separators
    Log in  test_labmanager  test_labmanager
    ${ARId}=  Simple AR Creation  client-1  Rita  Barley  Metals  Calcium
    Should Be Equal  ${ARId}   BAR-0001-R01
    # Changeing the analysis request separator
    Go to  http://localhost:55001/plone/bika_setup/edit
    Click Link  ID Server
    # This selection part may fail if the Analysis Request line isn'tin the firts place...
    Select From List  xpath=//select[starts-with(@id, 'Prefixes-separator-')]  _
    Click Button  Save
    Wait until page contains    Changes saved
    ${ARId}=  Simple AR Creation  client-1  Rita  Barley  Metals  Calcium
    Should Be Equal  ${ARId}   BAR-0002_R01

*** Keywords ***
