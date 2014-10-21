*** Settings ***

Library          Selenium2Library  timeout=5  implicit_wait=0.2
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
    Wait until page contains    You are now logged in

    Create New Priority

*** Keywords ***

Create New Priority
    Go to                       http://localhost:55001/plone/bika_setup/bika_arpriorities
    Wait until page contains    Priorities
    Page Should Contain         Add
    Click Link                  link=Add
    Wait until page contains    Add ARPriority
    Input Text                  title  Critical
    Input Text                  sortKey  100
    Input Text                  pricePremium  30
    Click Element               xpath=//input[@value='Save'][1]
    Page Should Contain         Changes saved
    Page Should Contain         Critical



HangOn
    Import library  Dialogs
    Pause execution

