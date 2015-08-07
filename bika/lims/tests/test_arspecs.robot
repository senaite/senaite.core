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

Test AnalysisRequest Specifications
    Enable autologin as  LabManager
    Set autologin username   test_labmanager

    # First enable visibility of AR Specification fields
    Go To                               ${PLONEURL}/bika_setup/edit
    Click Link                          Analyses
    Select Checkbox                     EnableARSpecs
    Click Button                        Save

    # Load the AR Add form, and set some basic things.
    Go To                               ${PLONEURL}/clients/client-1/analysisrequests
    Click Link                          Add
    Wait Until Page Contains            Request new analyses
    Select From Dropdown                ar_0_Profile            Trace Metals
    Select From Dropdown                ar_0_Contact            Rita
    SelectDate                          ar_0_SamplingDate       1

    # select Barley, and check that the Lab spec is applied
    Select from dropdown                ar_0_SampleType         Barley
    sleep                               3
    Textfield Value Should Be           ar_0_Specification      Barley
    Textfield Value Should Be           css=input[class*='min'][keyword='Mg']           5
    Textfield Value Should Be           css=input[class*='max'][keyword='Mg']           11
    Textfield Value Should Be           css=input[class*='error'][keyword='Mg']         10

    # select Apple pulp, and check that the Client spec is applied
    Select from dropdown                ar_0_SampleType         Apple Pulp
    sleep                               3
    Textfield Value Should Be           ar_0_Specification      Apple Pulp
    Textfield Value Should Be           css=input[class*='min'][keyword='Ca']           11
    Textfield Value Should Be           css=input[class*='max'][keyword='Ca']           15
    Textfield Value Should Be           css=input[class*='error'][keyword='Ca']         9    #  lab default is 10

    # Set AR overrides for Zinc.
    Input text                          css=input[class*='min'][keyword='Zn']           22
    Input text                          css=input[class*='max'][keyword='Zn']           33
    Input text                          css=input[class*='error'][keyword='Zn']         44

    # Save AR (AP-0001-R01) and recive it.
    Set Selenium Timeout                30
    Click Button                        Save
    Wait until page contains            created
    Set Selenium Timeout                5
    Select Checkbox                     css=[item_title='AP-0001-R01']
    Click element                       css=[transition='receive']
    Wait until page contains            saved

    # Now click the AR, and make sure we have result entry fields.
    Click link                          css=[href*='AP-0001-R01']
    wait until page contains element    css=[selector='Result_Zn']

    # Fill in valid form values
    Input text                          css=[selector='Result_Ca']      11
    Input text                          css=[selector='Result_Cu']      14
    Input text                          css=[selector='Result_Fe']      15
    Input text                          css=[selector='Result_Mg']      1
    Input text                          css=[selector='Result_Mn']      17
    Input text                          css=[selector='Result_Na']      21
    Input text                          css=[selector='Result_T']       1
    # Check that the overrides from the AR add form were applied:
    Input text                          css=[selector='Result_Zn']      1
    Press Key                           css=[selector='Result_Zn']      \t
    Page Should contain element         css=[title='Result out of range (min 22, max 33)']
    Input text                          css=[selector='Result_Zn']      22
    Press Key                           css=[selector='Result_Zn']      \t
    Page Should not contain element     css=[title*='Result out of range']
    # submit AR for verification.
    Click element                       css=[transition='submit']

    # Now copy this AR to new (open the AR add form with values prefilled):
    Go To                               ${PLONEURL}/clients/client-1/analysisrequests
    Select Checkbox                     css=[selector='client-1_AP-0001-R01']
    Click element                       css=[transition='copy_to_new']

    # The add form should have our existing specs applied:
    Wait until page contains element    css=[keyword='Zn'].min
    Textfield Value Should Be           css=[keyword='Zn'].min      22
    Textfield Value Should Be           css=[keyword='Zn'].max      33
    Textfield Value Should Be           css=[keyword='Zn'].error    44

    # We will now de-select Zinc, and create the AR.
    Unselect Checkbox                   css=[type='checkbox'][keyword='Zn']
    SelectDate                          ar_0_SamplingDate       1
    Set Selenium Timeout                30
    Click Button                        Save
    Wait until page contains            created
    Set Selenium Timeout                5

    # Now copy the new AR without the Zinc analysis:
    Go To                               ${PLONEURL}/clients/client-1/analysisrequests
    Select Checkbox                     css=[selector='client-1_AP-0002-R01']
    Click element                       css=[transition='copy_to_new']

    # Then select the Zinc analysis, the custom values should be applied.
    Select Checkbox                     css=[type='checkbox'][keyword='Zn']
    Textfield Value Should Be           css=[keyword='Zn'].min      22
    Textfield Value Should Be           css=[keyword='Zn'].max      33
    Textfield Value Should Be           css=[keyword='Zn'].error    44

    # OK forget that AR add form, let's go back to AP-0002-R01: the zinc-less AR.
    Go To                               ${PLONEURL}/clients/client-1/AP-0002-R01

    # Manage Analyses should also detect existing values:
    Click Link                          Manage Analyses
    Select Checkbox                     css=[alt="Select Zinc"]
    Page should contain element         css=[field='min'][value='22']
    Page should contain element         css=[field='max'][value='33']
    Page should contain element         css=[field='error'][value='44']

    Disable autologin
    Enable autologin as  LabManager
    Set autologin username   test_labmanager1

    go to                               ${PLONEURL}/clients/client-1/AP-0001-R01
    wait until page contains element    css=#lab_analyses_select_all
    select checkbox                     css=#lab_analyses_select_all
    Click element                       css=[transition='verify']

    Wait until page contains            Publish

when selecting a Spec it should be set on the AR.
    Enable autologin as  LabManager
    Set autologin username   test_labmanager

    # enable ar spec fields
    go to                               ${PLONEURL}/bika_setup/edit
    click link                          Analyses
    select checkbox                     EnableARSpecs

    # add ar
    go to                               ${PLONEURL}/clients/client-1/analysisrequests
    click link                          Add
    wait until page contains            Request new analyses
    Select from dropdown                ar_0_Profile            Trace
    Select from dropdown                ar_0_Contact            Rita
    SelectDate                          ar_0_SamplingDate       1
    Select from dropdown                ar_0_SampleType         Barley
    sleep        3
    Textfield Value Should Be           css=input[class*='min'][keyword='Mg']           5       #  lab default : 5
    Textfield Value Should Be           css=input[class*='max'][keyword='Mg']           11      #  lab default : 11
    Textfield Value Should Be           css=input[class*='error'][keyword='Mg']         10      #  lab default :  10
    Select from dropdown                ar_1_Template           Bruma Metals
    Select from dropdown                ar_1_Contact            Rita
    SelectDate                          ar_1_SamplingDate       1
    Textfield Value Should Be           ar_1_SampleType         Water
    Textfield Value Should Be           ar_1_Specification      Water
    Set Selenium Timeout                30
    Click Button                        Save
    Wait until page contains            created
    Set Selenium Timeout                10
    Select Checkbox                     css=[item_title='BAR-0001-R01']
    Click element                       css=[transition='receive']
    Wait until page contains            saved
    go to                               ${PLONEURL}/clients/client-1/BAR-0001-R01/base_view

    #spec as an edit field:
    Textfield Value Should Be           Specification     Barley
    #spec as a view field:
    # Page should contain element         xpath=.//a[@href='http://localhost:55001/plone/bika_setup/bika_analysisspecs/analysisspec-9']

*** Keywords ***
