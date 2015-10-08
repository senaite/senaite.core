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

    Check result formatting options

*** Keywords ***

Create AnalysisRequests
    [Documentation]     Add and receive 10 ARs at once.
    Disable stickers
    given an ar add form in client-2 with columns layout and 10 ars
    I select Johanna Smith from the Contact combogrid in column 0
    I click the copy button for the Contact field
    I select Water from the SampleType combogrid in column 0
    I click the copy button for the SampleType field
    Select date  SamplingDate-0  1
    I click the copy button for the SamplingDate field
    I expand the lab Metals category
    I select the Calcium service in all columns
    set selenium timeout   30
    Click Button  Save
    Wait until page contains  created
    Go to  ${PLONEURL}/clients/client-2
    Select checkbox  analysisrequests_select_all
    Click element  receive_transition
    set selenium timeout   5
    Wait until page contains  saved

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
    Input Text  xpath=//tr[@keyword='Ca'][1]//input[@selector='Result_Ca']  5.234
    Input Text  xpath=//tr[@keyword='Ca'][2]//input[@selector='Result_Ca']  13.5
    Input Text  xpath=//tr[@keyword='Ca'][3]//input[@selector='Result_Ca']  0.0077
    Input Text  xpath=//tr[@keyword='Ca'][4]//input[@selector='Result_Ca']  0.123
    Input Text  xpath=//tr[@keyword='Ca'][5]//input[@selector='Result_Ca']  0.00101
    Input Text  xpath=//tr[@keyword='Ca'][6]//input[@selector='Result_Ca']  3.123
    Input Text  xpath=//tr[@keyword='Ca'][7]//input[@selector='Result_Ca']  32092
    Input Text  xpath=//tr[@keyword='Ca'][8]//input[@selector='Result_Ca']  456021
    Input Text  xpath=//tr[@keyword='Ca'][9]//input[@selector='Result_Ca']  1293945
    Input Text  xpath=//tr[@keyword='Ca'][10]//input[@selector='Result_Ca']  0.0000123

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
    Page should contain   0.004e04
    Page should contain   0.0042e05
    Page should contain   0.00018e06
    Page should contain   0.2e-05

Check result formatting options
    Go to   ${PLONEURL}/bika_setup
    Click link  Analyses
    Wait Until element is visible  ScientificNotationResults
    Select from list  ScientificNotationResults   ax10^b / ax10^-b
    Select from list  ResultsDecimalMark   Comma (,)
    Click Button  Save
    Wait Until Page Contains  Changes saved.
    
    Go to   ${PLONEURL}/worksheets/WS-001    
    
    # Formatted results
    Page should contain   5,2
    Page should contain   14
    Page should contain   0,008
    Page should contain   0,12
    Page should contain   0,00101
    Page should contain   3,1
    Page should contain   3,209x10^4
    Page should contain   4,5602x10^5
    Page should contain   1,29394x10^6
    Page should contain   1,23x10^-5

    # Uncertainties
    Page should contain   0,2
    Page should contain   1
    Page should contain   0,002
    Page should contain   0,01
    Page should contain   0,00001
    Page should contain   0,8
    Page should contain   0,004x10^4
    Page should contain   0,0042x10^5
    Page should contain   0,00018x10^6 
    Page should contain   0,2x10^-5
