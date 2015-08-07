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


Add an ARTemplate with Analysis Dependencies
    #Test if alert is shown when selecting an analysis which has
    #a dependency in another analysis when creating a Profile and Template.

    Log in                              test_labmanager         test_labmanager
    Wait until page contains            You are now logged in
    Create ARTemplate with Analysis Dependences


*** Keywords ***

Add a Dependence to an Analysis Service
    #Test.xlsx set the check box "Use default calculation" from AddARTemplate/Method
    #We have to unselect this and select a Calculation whose calculation has Dependences
    Go to        ${PLONEURL}/bika_setup/bika_analysisservices
    Click Element            xpath=//th[@cat='Water Chemistry']
    Click Link               link=Tot. Hardness (THCaCO3)
    Click Link                       Method
    Unselect Checkbox                UseDefaultCalculation
    Select From List                 id=DeferredCalculation  Total Hardness
    Click Button             Save
    Wait until page contains    Changes saved.

Create ARTemplate with Analysis Dependences
    Add a Dependence to an Analysis Service
    Go to                       ${PLONEURL}/bika_setup/bika_artemplates
    Wait until page contains element    css=body.portaltype-artemplates
    Click Link                  Add Template
    Wait until page contains    Add AR Template
    Input Text                  title      test1
    Click Link                  fieldsetlegend-analyses
    Wait until page contains element    css=body.template-base_edit
    Select Checkbox               xpath=//input[@item_title='Tot. Hardness (THCaCO3)']
    Element Should Be Visible     messagebox
    Click Button                  //button[@type='button'][1]
    Click Button                  Save
    Wait until page contains    Changes saved.
