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

Test Analysis Uncertainty Precision
    [Documentation]   Analysis Results with Uncertainities and Precision
    ...  Creates an Analysis Service with uncertainities and
    ...  enables the 'Calculate precision from uncertainities' option.
    ...  The results must be formatted accordingly
    ...  See https://jira.bikalabs.com/browse/LIMS-1334 for further
    ...  information.
    Log in  test_labmanager  test_labmanager
    Go to   ${PLONEURL}/bika_setup/bika_analysisservices/analysisservice-3
    Click link  Analysis
    Wait Until Page Contains Element    Precision
    Input Text  Precision   2
    Input Text  ExponentialFormatPrecision  4
    Click link  Uncertainties

    Wait Until Page Contains Element    css=#Uncertainties-intercept_min-0
    Input Text  css=#Uncertainties-intercept_min-0   0
    Input Text  css=#Uncertainties-intercept_max-0   0.0001
    Input Text  css=#Uncertainties-errorvalue-0      0.000002
    Click Button  css=#Uncertainties_more

    Wait Until Page Contains Element    css=#Uncertainties-intercept_min-1
    Input Text  css=#Uncertainties-intercept_min-1   0.00011
    Input Text  css=#Uncertainties-intercept_max-1   0.002
    Input Text  css=#Uncertainties-errorvalue-1      0.000012
    Click Button  css=#Uncertainties_more

    Wait Until Page Contains Element    css=#Uncertainties-intercept_min-2
    Input Text  css=#Uncertainties-intercept_min-2   0.0021
    Input Text  css=#Uncertainties-intercept_max-2   0.08
    Input Text  css=#Uncertainties-errorvalue-2      0.0021
    Click Button  css=#Uncertainties_more

    Wait Until Page Contains Element    css=#Uncertainties-intercept_min-3
    Input Text  css=#Uncertainties-intercept_min-3   0.081
    Input Text  css=#Uncertainties-intercept_max-3   0.13
    Input Text  css=#Uncertainties-errorvalue-3      0.013
    Click Button  css=#Uncertainties_more

    Wait Until Page Contains Element    css=#Uncertainties-intercept_min-4
    Input Text  css=#Uncertainties-intercept_min-4   4.1
    Input Text  css=#Uncertainties-intercept_max-4   6
    Input Text  css=#Uncertainties-errorvalue-4      0.22
    Click Button  css=#Uncertainties_more

    Wait Until Page Contains Element    css=#Uncertainties-intercept_min-5
    Input Text  css=#Uncertainties-intercept_min-5   0.14
    Input Text  css=#Uncertainties-intercept_max-5   4
    Input Text  css=#Uncertainties-errorvalue-5      0.81
    Click Button  css=#Uncertainties_more

    Wait Until Page Contains Element    css=#Uncertainties-intercept_min-6
    Input Text  css=#Uncertainties-intercept_min-6   6.1
    Input Text  css=#Uncertainties-intercept_max-6   15
    Input Text  css=#Uncertainties-errorvalue-6      1.34
    Click Button  css=#Uncertainties_more

    Wait Until Page Contains Element    css=#Uncertainties-intercept_min-7
    Input Text  css=#Uncertainties-intercept_min-7   500001
    Input Text  css=#Uncertainties-intercept_max-7   5000000
    Input Text  css=#Uncertainties-errorvalue-7      182
    Click Button  css=#Uncertainties_more

    Wait Until Page Contains Element    css=#Uncertainties-intercept_min-8
    Input Text  css=#Uncertainties-intercept_min-8   15.1
    Input Text  css=#Uncertainties-intercept_max-8   50000
    Input Text  css=#Uncertainties-errorvalue-8      37
    Click Button  css=#Uncertainties_more

    Wait Until Page Contains Element    css=#Uncertainties-intercept_min-9
    Input Text  css=#Uncertainties-intercept_min-9   50001
    Input Text  css=#Uncertainties-intercept_max-9   500000
    Input Text  css=#Uncertainties-errorvalue-9      423

    Select Checkbox  PrecisionFromUncertainty
    Click Button  Save
    Wait Until Page Contains    Changes saved.

    Create Analysis Requests

    Create Worksheet with Analysis Requests

    Submit results and test

*** Keywords ***

Start browser
    Open browser  ${PLONEURL}/login_form  chrome
    Set selenium speed  ${SELENIUM_SPEED}

Create AnalysisRequests
    [Documentation]     Add and receive 10 ARs at once.
    @{time} =                   Get Time        year month day hour min sec
    Go to                       ${PLONEURL}/clients/client-2/portal_factory/AnalysisRequest/Request new analyses/ar_add?col_count=11
    Wait until page contains    Request new analyses
    Select From Dropdown        ar_0_Contact       Johanna Smith
    Select From Dropdown        ar_1_Contact       Johanna Smith
    Select From Dropdown        ar_2_Contact       Johanna Smith
    Select From Dropdown        ar_3_Contact       Johanna Smith
    Select From Dropdown        ar_4_Contact       Johanna Smith
    Select From Dropdown        ar_5_Contact       Johanna Smith
    Select From Dropdown        ar_6_Contact       Johanna Smith
    Select From Dropdown        ar_7_Contact       Johanna Smith
    Select From Dropdown        ar_8_Contact       Johanna Smith
    Select From Dropdown        ar_9_Contact       Johanna Smith
    Select From Dropdown        ar_10_Contact      Johanna Smith
    Select From Dropdown        ar_0_SampleType    Water
    Select From Dropdown        ar_1_SampleType    Water
    Select From Dropdown        ar_2_SampleType    Water
    Select From Dropdown        ar_3_SampleType    Water
    Select From Dropdown        ar_4_SampleType    Water
    Select From Dropdown        ar_5_SampleType    Water
    Select From Dropdown        ar_6_SampleType    Water
    Select From Dropdown        ar_7_SampleType    Water
    Select From Dropdown        ar_8_SampleType    Water
    Select From Dropdown        ar_9_SampleType    Water
    Select From Dropdown        ar_10_SampleType   Water
    SelectDate                 ar_0_SamplingDate   @{time}[2]
    SelectDate                 ar_1_SamplingDate   @{time}[2]
    SelectDate                 ar_2_SamplingDate   @{time}[2]
    SelectDate                 ar_3_SamplingDate   @{time}[2]
    SelectDate                 ar_4_SamplingDate   @{time}[2]
    SelectDate                 ar_5_SamplingDate   @{time}[2]
    SelectDate                 ar_6_SamplingDate   @{time}[2]
    SelectDate                 ar_7_SamplingDate   @{time}[2]
    SelectDate                 ar_8_SamplingDate   @{time}[2]
    SelectDate                 ar_9_SamplingDate   @{time}[2]
    SelectDate                 ar_10_SamplingDate   @{time}[2]
    Click Element              xpath=//th[@id='cat_lab_Metals']
    Select Checkbox            xpath=//input[@title='Calcium' and @name='ar.0.Analyses:list:ignore_empty:record']
    Select Checkbox            xpath=//input[@title='Calcium' and @name='ar.1.Analyses:list:ignore_empty:record']
    Select Checkbox            xpath=//input[@title='Calcium' and @name='ar.2.Analyses:list:ignore_empty:record']
    Select Checkbox            xpath=//input[@title='Calcium' and @name='ar.3.Analyses:list:ignore_empty:record']
    Select Checkbox            xpath=//input[@title='Calcium' and @name='ar.4.Analyses:list:ignore_empty:record']
    Select Checkbox            xpath=//input[@title='Calcium' and @name='ar.5.Analyses:list:ignore_empty:record']
    Select Checkbox            xpath=//input[@title='Calcium' and @name='ar.6.Analyses:list:ignore_empty:record']
    Select Checkbox            xpath=//input[@title='Calcium' and @name='ar.7.Analyses:list:ignore_empty:record']
    Select Checkbox            xpath=//input[@title='Calcium' and @name='ar.8.Analyses:list:ignore_empty:record']
    Select Checkbox            xpath=//input[@title='Calcium' and @name='ar.9.Analyses:list:ignore_empty:record']
    Select Checkbox            xpath=//input[@title='Calcium' and @name='ar.10.Analyses:list:ignore_empty:record']
    Set Selenium Timeout       90
    Click Button               Save
    Wait until page contains   created
    Go to                      ${PLONEURL}/clients/client-2
    Set Selenium Timeout       10
    Select checkbox            analysisrequests_select_all
    Click element               receive_transition
    Wait until page contains    saved

Create Worksheet With Analysis Requests
    Create Worksheet
    Add Analyses                H2O-0001-R01_Ca  H2O-0002-R01_Ca  H2O-0003-R01_Ca  H2O-0004-R01_Ca  H2O-0005-R01_Ca  H2O-0006-R01_Ca  H2O-0007-R01_Ca  H2O-0008-R01_Ca  H2O-0009-R01_Ca  H2O-0010-R01_Ca
    
Create Worksheet
    Go to  ${PLONEURL}/worksheets
    Wait Until Page Contains    Mine
    Select From List            analyst          Lab Analyst 1
    Click Button                Add
    Wait Until Page Contains    Add Analyses

Add Analyses
    [Arguments]         @{analyses}

    Go to                               ${PLONEURL}/worksheets/WS-001/add_analyses
    Wait Until Page Contains            Add Analyses
    Click Element                       css=th#foldercontents-getRequestID-column
    Wait Until Page Contains Element    css=th#foldercontents-getRequestID-column.sort_on

    :FOR     ${analysis}   IN   @{analyses}
    \     Select Checkbox         xpath=//input[@selector='${analysis}']

    Set Selenium Timeout        30
    Click Element               assign_transition
    Wait Until Page Contains    Manage Results
    Set Selenium Timeout        10

Submit results and test
    Input Text    xpath=//tr[@keyword='Ca']//input[@selector='Result_Ca'][1]          5.234
    Input Text    xpath=//tr[@keyword='Ca']//input[@selector='Result_Ca'][2]          13.5
    Input Text    xpath=//tr[@keyword='Ca']//input[@selector='Result_Ca'][3]          0.0077
    Input Text    xpath=//tr[@keyword='Ca']//input[@selector='Result_Ca'][4]          0.123
    Input Text    xpath=//tr[@keyword='Ca']//input[@selector='Result_Ca'][5]          0.00101
    Input Text    xpath=//tr[@keyword='Ca']//input[@selector='Result_Ca'][6]          3.123
    Input Text    xpath=//tr[@keyword='Ca']//input[@selector='Result_Ca'][7]          32092
    Input Text    xpath=//tr[@keyword='Ca']//input[@selector='Result_Ca'][8]          456021
    Input Text    xpath=//tr[@keyword='Ca']//input[@selector='Result_Ca'][9]          1293945
    Input Text    xpath=//tr[@keyword='Ca']//input[@selector='Result_Ca'][10]         0.0000123

    Focus                       css=.analyst
    Click Element               xpath=//input[@value='Submit for verification'][1]
    Wait Until Page Contains    Changes saved.

    # Formatted results
    Page should contain   5.2
    Page should contain   14
    Page should contain   0.008
    Page should contain   0.12
    Page should contain   0.00101
    Page should contain   3.1
    Page should contain   3.2092e+04
    Page should contain   4.56021e+05
    Page should contain   1.293945e+06
    Page should contain   1.23000e-05

    # Uncertainties
    Page should contain   0.2
    Page should contain   1
    Page should contain   0.002
    Page should contain   0.01
    Page should contain   0.00001
    Page should contain   0.8
    Page should contain   0.004e+04
    Page should contain   0.0042e+05
    Page should contain   0.00018e+06 
    Page should contain   0.2e-05
