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

Client Permisions on Published Results
    [Documentation]   Create an AR and then publish it. The client contacts will
    ...               be able to see the published files. Contacts from other clients NOT.
    enable autologin as  LabManager
    set autologin username  test_labmanager
    Disable stickers
    ${ARId}=  Simple AR Creation  client-1  Rita  Barley  Metals  Calcium
    Go to             ${PLONEURL}/clients/client-1/analysisrequests
    click link        ${ARId}
    Execute transition receive inside ClientARView/ManageResults
    input text        xpath=//input[@selector='Result_Ca']  10
    select from list  xpath=//select[@selector='Analyst_Ca']  Lab Analyst 1
    click button      submit_transition
    wait until page contains  Changes saved.
    disable autologin
    enable autologin as  LabManager
    set autologin username  test_labmanager1
    Go to             ${PLONEURL}/clients/client-1/${ARId}
    Execute transition verify inside ClientARView/ManageResults
    wait until page contains  Item state changed.
    Execute transition publish inside ClientARView/ManageResults
    click button      publish_button
    Go to             ${PLONEURL}/clients/client-1/${ARId}/published_results
    page should contain link  Download
    disable autologin
    #Check the client's user with manual login
    Log in            ritamo  ritamo
    Go to             ${PLONEURL}/clients/client-1/${ARId}/published_results
    page should contain link  Download
    Log out
    #check a non client user with manual login
    Log in            johannasm  johannasm
    Go to             ${PLONEURL}/clients/client-1/${ARId}/published_results
    page should not contain link  Download
