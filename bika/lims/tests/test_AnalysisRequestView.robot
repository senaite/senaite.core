*** Settings ***
Documentation    Tests related with AnalysisRequestView only.
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

*** Test Cases ***
Test CCContacts dropdown filter by client
    [Documentation]  This test check if the CCContacts dropdown list
    ...  is filtred by client.
    ${ARId}=  Simple AR Creation  Happy Hills  Rita  Barley  Metals  Calcium
    # Create a contact in an other client.
    Create a contact  Klaymore  Moist Von  LipWig
    # Check if you can select a Contact from another client.
    Go to             ${PLONEURL}/clients/client-1/analysisrequests
    click link        ${ARId}
    focus   CCContact
    page should not contain  Moist Von
    page should contain  Seemonster


*** Keywords ***
Start browser
    Open browser                        ${PLONEURL}/login_form
    Log in                              test_labmanager         test_labmanager
    Wait until page contains            You are now logged in
    Set selenium speed                  ${SELENIUM_SPEED}

Provided precondition
    Setup system under test