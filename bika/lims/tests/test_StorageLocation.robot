*** Settings ***

Library          Selenium2Library  timeout=10  implicit_wait=0.2
Library          String
Resource         keywords.txt
Library          bika.lims.testing.Keywords
Resource         plone/app/robotframework/selenium.robot
Resource         plone/app/robotframework/saucelabs.robot
Variables        plone/app/testing/interfaces.py
Variables        bika/lims/tests/variables.py
Suite Setup      Start browser
Suite Teardown   Close All Browsers

*** Variables ***

${PATH_TO_TEST} =

*** Test Cases ***

Test Storage Location
    Log in                      test_labmanager  test_labmanager

    Check Bika Setup imported correctly
    Create Setup Location
    Create Client Location

*** Keywords ***

Start browser
    Open browser                http://localhost:55001/plone/login
    Set selenium speed          ${SELENIUM_SPEED}

Check Bika Setup imported correctly
    Go to                       http://localhost:55001/plone/bika_setup/bika_storagelocations
    Wait until page contains    Storage Locations
    Page Should Contain         HAM.FZ1.S2

Create Setup Location
    Go to                       http://localhost:55001/plone/bika_setup/bika_storagelocations
    Wait until page contains    Storage Locations
    Click Link                  link=Add
    Wait until page contains    Add Storage Location
    Page Should Contain         Address
    Create Location             BIKA.FR1.S2
    Go to                       http://localhost:55001/plone/bika_setup/bika_storagelocations
    Page should contain         BIKA.FR1.S2

Create Client Location
    Go to                       http://localhost:55001/plone/clients/client-1/storagelocations
    Wait until page contains    Storage Locations
    Click Link                  link=Add
    Wait until page contains    Add Storage Location
    Page Should Contain         Address
    Create Location             HAP.FR1.S2
    Go to                       http://localhost:55001/plone/clients/client-1/storagelocations
    Page should contain         HAP.FR1.S2

Create Location
    [Arguments]  ${address}
    Input Text                  title  ${address}
    Input Text                  SiteTitle  BIKA Labs
    Input Text                  SiteCode  BIKA
    Input Text                  SiteDescription  BIKA Labs site in Grabou
    Input Text                  LocationTitle  Freezer 1
    Input Text                  LocationCode  FR1
    Input Text                  LocationDescription  Freeze 1
    Input Text                  LocationType  Freezer
    Input Text                  ShelfTitle  Shelf 2
    Input Text                  ShelfCode  S2
    Input Text                  ShelfDescription  Second shelf from bottom
    Click Button                Save
    Wait until page contains    Changes saved.
