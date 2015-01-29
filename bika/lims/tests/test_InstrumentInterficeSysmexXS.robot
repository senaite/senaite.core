*** Settings ***
Documentation    Suite test for importing actions with Sysmex Interfice XS family.
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
${input_identifier} =  sysmex_xs_500i

*** Test Cases ***
test 500i CSV file
    [Documentation]  Check the correct behaviour of Analysis Service and default key input.
    ${PATH_TO_TEST} =         run keyword   resource_filename
    # First import
    Import Instrument File    Sysmex XS - 500i  ${PATH_TO_TEST}/files/SysmexXS-500i.csv  ${input_identifier}



*** Keywords ***
Start browser
    Open browser                        ${PLONEURL}/login_form  chrome
    Log in                              test_labmanager         test_labmanager
    Wait until page contains            You are now logged in
    Set selenium speed                  ${SELENIUM_SPEED}

Import Instrument File
    [Documentation]  Select the instrument and file type.
    ...              Then import the file created by the instrument.
    [arguments]  ${instrument}  ${file}  ${input_identifier}

    Click Link                  Import
    Wait until page contains    Select a data interface
    Select from list            exim  ${instrument}
    Element Should Contain      ${input_identifier}_format  CSV
    Import AR Results Instrument File    ${file}  ${input_identifier}_file

Import AR Results Instrument File
    [Documentation]  Import the file from test files folder, and submit it.
    [arguments]                 ${file}
    ...                         ${input_identifier}
    Choose File                 ${input_identifier}  ${file}
    Click Button                Submit
    Wait until page contains    Log trace
    page should contain         End of file reached successfully: 1 objects, 116 analyses, 1 results