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

*** Test Cases ***
Test CCContacts dropdown filter by client
    [Documentation]  This test checks if the CCContacts dropdown list
    ...  is filtred by client.
    Log in                              test_labmanager         test_labmanager
    Wait until page contains            You are now logged in
    ${ARId}=  Simple AR Creation  client-1  Rita  Barley  Metals  Calcium
    # Create a contact in an other client.
    Create a contact  Klaymore  Moist Von  LipWig
    # Check if you can select a Contact from another client.
    Go to             ${PLONEURL}/clients/client-1/analysisrequests
    click link        ${ARId}
    focus   CCContact
    page should not contain  Moist Von
    page should contain  Seemonster

Test autosave feature
    Log in                              test_labmanager         test_labmanager
    Wait until page contains            You are now logged in
    [Documentation]  It ckhecks the correct functionament of autosaving feature.
    # Enable sampling workflow to test all possibilities
    Enable Sampling Workflow
    ${ARId}=  Simple AR Creation  client-1  Rita  Barley  Metals  Calcium
    Go to             ${PLONEURL}/clients/client-1/analysisrequests
    click link        ${ARId}
    # Testing checkboxes
    select checkbox      InvoiceExclude
    wait until page contains  updated successfully
    Reload Page
    checkbox should be selected  InvoiceExclude
    unselect checkbox    InvoiceExclude
    wait until page contains  updated successfully
    Reload Page
    checkbox should not be selected  InvoiceExclude
    # Testing typical Input
    input text           ClientOrderNumber  777
    #We need to focus out the input to allow save it.
    focus  Contact
    wait until page contains  updated successfully
    Reload Page
    Textfield Should Contain  ClientOrderNumber  777
    # Testing lists
    select from list  Sampler  Lab Sampler 1
    wait until page contains  updated successfully
    Reload Page
    element should contain  Sampler  Lab Sampler 1
    # Testing dropdown
    select from dropdown  Specification  Bran
    wait until page contains  updated successfully
    Reload Page
    Textfield Should Contain  Specification  Bran
    # Testinc CCContact
    select from dropdown  CCContact   Neil
    wait until page contains  updated successfully
    Reload Page
    page should contain  Neil


*** Keywords ***

Provided precondition
    Setup system under test
