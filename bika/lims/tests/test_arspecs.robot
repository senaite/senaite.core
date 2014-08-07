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

*** Test Cases ***

Test AR specs UI and alerts
    Log in                              test_labmanager  test_labmanager

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

    # select Barley, there is a Lab spec
    Select from dropdown                ar_0_SampleType         Barley
    sleep          3
    Textfield Value Should Be           css=input[class*='min'][keyword='Mg']           5       #  lab default : 5
    Textfield Value Should Be           css=input[class*='max'][keyword='Mg']           11      #  lab default : 11
    Textfield Value Should Be           css=input[class*='error'][keyword='Mg']         10      #  lab default :  10

    # select Apple pulp, there is a Client spec
    Select from dropdown                ar_0_SampleType         Apple Pulp
    sleep          3
    # when selecting a sampletype the spec is always set if a default is found
    Textfield Value Should Be           ar_0_Specification      Apple Pulp
    # That default spec gets automatically selected
    Text field value should be          ar_0_Specification      Apple Pulp
    # The value for Ca in the client spec is Ca=min:11 max:15 error:10%
    Textfield Value Should Be           css=input[class*='min'][keyword='Ca']           11      #  lab default : 9
    Textfield Value Should Be           css=input[class*='max'][keyword='Ca']           15      #  lab default : 11
    Textfield Value Should Be           css=input[class*='error'][keyword='Ca']         9       #  lab default :  10
    # these override the defaults
    Input text                          css=input[class*='min'][keyword='Ca']           1
    Input text                          css=input[class*='max'][keyword='Ca']           5
    Input text                          css=input[class*='error'][keyword='Ca']         10
    # And others will be blank.
    Input text                          css=input[class*='min'][keyword='Ca']           1
    Input text                          css=input[class*='max'][keyword='Ca']           5
    Input text                          css=input[class*='error'][keyword='Ca']         10

    # Save AR, and recive sample
    Set Selenium Timeout                30
    Click Button                        Save
    Wait until page contains            created
    Set Selenium Timeout                10
    Select Checkbox                     css=[item_title='AP-0001-R01']
    Click element                       css=[transition='receive']
    Wait until page contains            saved

    Click link                          css=[href*='AP-0001-R01']
    wait until page contains element    css=[selector='Result_Ca']

    # Check the client spec values
    Input text                          css=[selector='Result_Ca']      7
    Press Key                           css=[selector='Result_Ca']      \t
    Page Should contain element         css=[title='Result out of range (min 1, max 5)']
    Input text                          css=[selector='Result_Ca']      4
    Press Key                           css=[selector='Result_Ca']      \t
    Page Should not contain element     css=[title*='Result out of range']

    # Check the lab spec values
    Input text                          css=[selector='Result_Cu']      15
    Press Key                           css=[selector='Result_Cu']      \t
    Page Should not contain element     css=[title*='Result out of range']
    Input text                          css=[selector='Result_Cu']      1
    Press Key                           css=[selector='Result_Cu']      \t
    # I enter the out-of-range value last, and send it through
    # verify and publish
    Page Should contain element         css=[title='Result out of range (min 14, max 18)']
    Input text                          css=[selector='Result_Fe']      10
    Input text                          css=[selector='Result_Mg']      10
    Input text                          css=[selector='Result_Mn']      10
    Input text                          css=[selector='Result_Na']      10
    Input text                          css=[selector='Result_Zn']      10
    Click element                       css=[transition='submit']

    Log Out
    Log in                              test_labmanager1  test_labmanager1
    go to                               ${PLONEURL}/clients/client-1/AP-0001-R01
    wait until page contains element    css=#lab_analyses_select_all
    select checkbox                     css=#lab_analyses_select_all
    Click element                       css=[transition='verify']

    Wait until page contains            Publish

when selecting a Spec it should be set on the AR.
    Log in                              test_labmanager  test_labmanager

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
    # Page should contain element         xpath=.//*[contains(@id, 'Specification')]/span[@value='Barley']
    #spec as a view field:
    Page should contain element         xpath=.//a[@href='http://localhost:55001/plone/bika_setup/bika_analysisspecs/analysisspec-9']

*** Keywords ***

Start browser
    Open browser                ${PLONEURL}/login_form
    Set selenium speed          ${SELENIUM_SPEED}
