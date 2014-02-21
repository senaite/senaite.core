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

*** Test Cases ***

Test AR Priorities
    Log in                      test_labmanager  test_labmanager

    Create New Priority

*** Keywords ***

Start browser
    Open browser                http://localhost:55001/plone/login
    Set selenium speed          ${SELENIUM_SPEED}

Create New Priority
    Go to                       http://localhost:55001/plone/arpriorities
    Wait until page contains    Priorities
    Page Should Contain         Add
    Click Link                  link=Add
    Wait until page contains    View
    Page Should Contain         Submitted



HangOn
    Import library  Dialogs
    Pause execution

