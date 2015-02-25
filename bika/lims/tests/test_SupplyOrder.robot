*** Settings ***

Library          Selenium2Library  timeout=5  implicit_wait=0.2
Library          String
Resource         keywords.txt
Library          debuglibrary
Library          bika.lims.testing.Keywords
Resource         plone/app/robotframework/selenium.robot
Resource         plone/app/robotframework/saucelabs.robot
Variables        plone/app/testing/interfaces.py
Variables        bika/lims/tests/variables.py
Suite Setup      Start browser
Suite Teardown   Close All Browsers

*** Variables ***

*** Test Cases ***

Test Supply Orders
    Log in                              test_labmanager         test_labmanager
    Wait until page contains            You are now logged in
    debug

*** Keywords ***
