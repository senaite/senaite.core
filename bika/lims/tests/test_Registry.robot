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

Test Client landing page
    Log in                              ${SITE_OWNER_NAME}   ${SITE_OWNER_PASSWORD}
    Wait until page contains            You are now logged in

    go to                               ${PLONEURL}/portal_registry
    input text                          css=input[name='q']  bika.lims.client
    click element                       css=input[value='Filter']
    click link                          bika lims client default_landing_page
    select from list                    form-widgets-value  batches
    click button                        form-buttons-save
    wait until page contains            Override the translation machinery
    go to                               ${PLONEURL}/clients
    wait until page contains            Happy Hills
    click link                          Happy Hills
    location should be                  ${PLONEURL}/clients/client-1/batches

    log out
    log in                              ritamo  ritamo
    location should be                  ${PLONEURL}/clients/client-1/batches

*** Keywords ***

