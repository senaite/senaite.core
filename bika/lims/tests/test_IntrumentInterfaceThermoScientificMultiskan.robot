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

ELISA csv file
    [Documentation]  Firts we have to create the AS to match the
    ...              analysis in the file. Then we have to create the AR
    ...              and tranistion it. Finally qe can import the results.
    ${PATH_TO_TEST} =           run keyword   resource_filename
    Disable stickers
    Import Instrument File     Thermo Scientific Multiskan - GO Microplate Spectrophotometer  ${PATH_TO_TEST}/files/ELISA.csv

    page should contain         End of file reached successfully: 24 objects, 1 analyses, 24 results

*** Keywords ***

Start browser
    Open browser                        ${PLONEURL}/login_form  chrome
    Log in                              test_labmanager         test_labmanager
    Wait until page contains            You are now logged in
    Set selenium speed                  ${SELENIUM_SPEED}

Import Instrument File
    [Documentation]  Select the instrument and file type.
    ...              Then import the file created by the instrument.
    [arguments]  ${instrument}  ${file}
    Go to                       ${PLONEURL}
    Click Link                  Import
    Wait until page contains    Select a data interface
    Select from list            exim  ${instrument}
    Element Should Contain      format  CSV
    Import AR Results Instrument File    ${file}  data_file

Import AR Results Instrument File
    [Documentation]  Import the file from test files folder, and submit it.
    [arguments]                 ${file}
    ...                         ${input_identifier}
    Choose File                 ${input_identifier}  ${file}
    Click Button                Submit
    Wait until page contains    Log trace
