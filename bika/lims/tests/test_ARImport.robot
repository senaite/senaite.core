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

${input_identifier} =  input#arimport_file

*** Test Cases ***

Test AR Importing dependencies
    Log in                      test_labmanager  test_labmanager
    Wait until page contains    You are now logged in

    Import Classic Valid AR
    Submit Valid AR Import
    Import Classic AR File with invalid filename
    Import Classic AR File with errors

    Import Profile Valid AR
    Submit Valid AR Import
    Import Profile AR File with invalid filename
    Import Profile AR File with errors

*** Keywords ***

Import Classic AR File with invalid filename
    Go to                       http://localhost:55001/plone/clients/client-1
    Wait until page contains    Imports
    ${PATH_TO_TEST} =           run keyword   resource_filename
    Import Classic ARImport     ${PATH_TO_TEST}/files/ARImportClassicInvalidFilename.csv
    Page Should Contain         Error
    Page Should Contain         does not match entered filename

Import Classic AR File with errors
    Go to                       http://localhost:55001/plone/clients/client-1
    Wait until page contains    Imports
    ${PATH_TO_TEST} =           run keyword   resource_filename
    Import Classic ARImport     ${PATH_TO_TEST}/files/ARImportClassicErrors.csv
    Wait until page contains    Remarks
    Page Should Contain         Client ID should be
    Page Should Contain         Contact invalid
    Page Should Contain         Sample type WrongType invalid
    Page Should Contain         Container type WrongContainer invalid

Import Classic Valid AR
    Go to                       http://localhost:55001/plone/clients/client-1
    Wait until page contains    Imports
    ${PATH_TO_TEST} =           run keyword   resource_filename
    Import Classic ARImport     ${PATH_TO_TEST}/files/ARImportClassicValid.csv
    sleep                       5s
    Page Should Contain         Valid
    Page Should Not Contain     Error

Import Profile Valid AR
    Go to                       http://localhost:55001/plone/clients/client-1
    Wait until page contains    Imports
    ${PATH_TO_TEST} =           run keyword   resource_filename
    Import Profile ARImport     ${PATH_TO_TEST}/files/ARImportProfileValid.csv
    sleep                       5s
    Page Should Contain         Valid
    Page Should Not Contain     Error

Import Profile AR File with invalid filename
    Go to                       http://localhost:55001/plone/clients/client-1
    Wait until page contains    Imports
    ${PATH_TO_TEST} =           run keyword   resource_filename
    Import Profile ARImport     ${PATH_TO_TEST}/files/ARImportProfileInvalidFilename.csv
    Page Should Contain         Error
    Page Should Contain         does not match entered filename

Import Profile AR File with errors
    Go to                       http://localhost:55001/plone/clients/client-1
    Wait until page contains    Imports
    ${PATH_TO_TEST} =           run keyword   resource_filename
    Import Profile ARImport     ${PATH_TO_TEST}/files/ARImportProfileErrors.csv
    Page Should Contain         Remarks
    Page Should Contain         Client ID should be
    Page Should Contain         Contact invalid
    Page Should Contain         Sample type WrongType invalid
    Page Should Contain         Container type WrongContainer invalid


Submit Valid AR Import
    Open Workflow Menu
    Click Link                  link=Submit ARImport
    Wait until page contains    View
    Page Should Contain         Submitted

Import Classic ARImport
    [arguments]  ${file}

    Click Link                  Imports
    Wait until page contains    AR Import
    Click Link                  AR Import
    Wait until page contains    Import Analysis Request Data
    Select Import Option        c
    Import ARImport File        ${file}

Import Profile ARImport
    [arguments]  ${file}

    Click Link                  Imports
    Wait until page contains    AR Import
    Click Link                  AR Import
    Wait until page contains    Import Analysis Request Data
    Select Import Option        p
    Import ARImport File        ${file}

Import ARImport File
    [arguments]  ${file}

    Choose File                 css=${input_identifier}  ${file}
    Wait until page contains    Import Analysis Request Data
    Set Selenium Timeout        30
    Click Button                Import
    Set Selenium Timeout        5

HangOn
    Import library  Dialogs
    Pause execution

Open Add New Menu
    Open Menu  plone-contentmenu-factories

Open Workflow Menu
    Open Menu  plone-contentmenu-workflow

Open Menu
    [Arguments]  ${elementId}

    Element Should Be Visible  css=dl#${elementId}
    Element Should Not Be Visible  css=dl#${elementId} dd.actionMenuContent
    Click link  css=dl#${elementId} dt.actionMenuHeader a
    Wait until keyword succeeds  5s  1s  Element Should Be Visible  css=dl#${elementId} dd.actionMenuContent

Select Import Option
    [Arguments]  ${option}

    [Documentation]  LOG Set Import Option to ${option}
    Select Radio Button  ImportOption  ${option}
    Radio Button Should Be Set To  ImportOption  ${option}
