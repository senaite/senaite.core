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

Check that automatic expanded and restricted categories expand and restrict
    # set HappyHills preferences:
    #   Restrict 'Microbiology'
    #   Auto-Expand 'Metals'
    Log in                      test_labmanager1   test_labmanager1
    Go to                       ${PLONEURL}/clients/client-1/edit/#fieldsetlegend-preferences
    select from list            RestrictedCategories:list   Microbiology
    select from list            DefaultCategories:list      Metals
    click button                Save
    # Bring up the AR Add form
    Go to                       ${PLONEURL}/clients/client-1
    Wait until page contains element    css=form#analysisrequests
    Click Link                  Add
    Wait until page contains    Request new analyses
    # Check that Microbiology is RESTRICTED
    log   sleeping 118   warn
    sleep   117
    # Check that Metals is EXPANDED
    log   sleeping 117   warn
    sleep   118


#when Contact is selected:
#    Check if CC Contacts are selected
#    Check that the State variable has been completely configured.
#
#when Template is selected:
#    Check that SampleType is ${st}
#    Check that SamplePoint is ${sp}
#    Check that category ${poc} ${cat} is expanded
#    Check that analyses from ${profile_id} are set
#    Check that specification is ${spec_title}
#    Check that specification ${spec_title} is applied
#    Check that prices are correctly calculated
#    Check that the State variable has been completely configured.
#
#when Profile selected:
#    Check that profile analyses from PROFILE_ID are set correctly
#    Check that profile analyses from ${profile_id} are set
#    Check that prices are correctly calculated
#    Check that the State variable has been completely configured.
#
#when Sample Type selected:
#    Check that specification is ${spec_title}
#    Check that specification ${spec_title} is applied
#    Check that ST<-->SP restrictions are in place
#    Check that the State variable has been completely configured.
#
#when Sample Point selected:
#    Check that ST<-->SP restrictions are in place
#    Check that the State variable has been completely configured.
#
#when Specification is selected:
#    Check that specification is ${spec_title}
#    Check that specification ${spec_title} is applied
#    Check that the State variable has been completely configured.
#
#when Report as Dry Matter:
#    Check that DryMatterService is selected.
#    Check that prices are correctly calculated
#    Check that the State variable has been completely configured.
#
#when DryMatterService is un-selected:
#    Check that "Report as Dry Matter" option is un-checked (warning?)
#    Check that the State variable has been completely configured.
#
#When analysis checkbox is "Clicked"
#    check that the ar_spec fields are displayed if the option is enabled
#    check that the ar_spec fields are not displayed if the option is disabled
#    Check that the State variable has been completely configured.
#    Check that required services are recommended
#    Check that service is un-selected if requirements are not fulfilled
#    Check that services who require this service are warned about
#    Check that services who require this service are unselected if this one is
#
#when Create Profile button is clicked:
#    popup appears, enter the value, click save, monitor for correct response.
#
#test Calculate Partitions:
#    if Container selected
#    or Analysis selected
#    or SampleType selected
#    or DefaultContainerType selected.
#
#when Copy-Across is selected:
#    Make sure that it works for reference fields and their _uid counterparts
#    All fields tested here, must have their tests run against the copy-across machine.
#        - This must be done for all four test columns.
#        - Check the state_variable completely
#
#when selecting Sample:
#    Check that the secondary sample fields are filled in correctly.
#    Submit and check that the AR is correctly created.
#

#Set COMPLETE list of fields for ONE AR.
#    Check that the State variable has been completely configured.
#

*** Keywords ***

Start browser
    Open browser                http://localhost:55001/plone/login
    Set selenium speed          ${SELENIUM_SPEED}

#Create AR
#    Log in                      test_labmanager  test_labmanager
#    @{time} =                   Get Time        year month day hour min sec
#    Go to                       ${PLONEURL}/clients/client-1
#    Wait until page contains element    css=body.portaltype-client
#    Click Link                  Add
#    Wait until page contains    Request new analyses
#    Select from dropdown        ar_0_Contact                Rita
#    Select from dropdown        ar_0_Template               Bore
#    Select Date                 ar_0_SamplingDate           @{time}[2]
#    Set Selenium Timeout        30
#    Click Button                Save
#    Set Selenium Timeout        10
#    Wait until page contains    created
#    ${ar_id} =                  Get text      //dl[contains(@class, 'portalMessage')][2]/dd
#    ${ar_id} =                  Set Variable  ${ar_id.split()[2]}
#    Go to                       http://localhost:55001/plone/clients/client-1/analysisrequests
#    Wait until page contains    ${ar_id}
#    Select checkbox             xpath=//input[@item_title="${ar_id}"]
#    Click button                xpath=//input[@value="Receive sample"]
#    Wait until page contains    saved
#    [return]                    ${ar_id}
#
#Create Primary AR By Row
#    Log in                      test_labmanager  test_labmanager
#    @{time} =                   Get Time        year month day hour min sec
#    Go to                       ${PLONEURL}/clients/client-1
#    Wait until page contains element    css=body.portaltype-client
#    Input text                  ar_count    2
#    Select from list            layout      rows
#    Click Link                  Add
#    Wait until page contains    Request new analyses
#    Select from dropdown        Contact                     Rita
#    Select Date                 ar_0_SamplingDate           @{time}[2]
#    Select from dropdown        ar_0_SampleType             Water
#    Click element               ar_0_Analyses
#    Wait until page contains    Select Analyses for AR
#    Click element               xpath=//th[@id="cat_lab_Metals"]
#    Select checkbox             xpath=//input[@title="Calcium"]
#    Click Button                Submit
#    Set Selenium Timeout        10
#    ${Analyses} =               Get value    xpath=//input[@id="ar_0_Analyses"]
#    Log                         ${Analyses}
#    Should Be Equal             ${Analyses}    Calcium
#    Click Button                Save
#    Wait until page contains    was successfully created.
#    ${ar_id} =                  Get text      //dl[contains(@class, 'portalMessage')][2]/dd
#    ${ar_id} =                  Set Variable  ${ar_id.split()[2]}
#    Go to                       http://localhost:55001/plone/clients/client-1/analysisrequests
#    Wait until page contains    ${ar_id}
#    Select checkbox             xpath=//input[@item_title="${ar_id}"]
#    Click button                xpath=//input[@value="Receive sample"]
#    Wait until page contains    saved
#    [return]                    ${ar_id}
#
#Create Mulitple Primary ARs By Row With Template
#    Log in                      test_labmanager  test_labmanager
#    @{time} =                   Get Time        year month day hour min sec
#    Go to                       ${PLONEURL}/clients/client-1
#    Wait until page contains element    css=body.portaltype-client
#    Input text                  ar_count    2
#    Select from list            layout      rows
#    Click Link                  Add
#    Wait until page contains    Request new analyses
#    Select from dropdown        Contact                     Rita
#    Select Date                 ar_0_SamplingDate           @{time}[2]
#    Select from dropdown        ar_0_Template               Bore
#    Set Selenium Timeout        10
#    ${Analyses} =               Get value    xpath=//input[@id="ar_0_Analyses"]
#    Log                         ${Analyses}
#    Should Be Equal             ${Analyses}    Calcium, Magnesium
#    Click Element               //img[contains(@class, 'TemplateCopyButton')]
#    Click Element               //img[contains(@class, 'SamplingDateCopyButton')]
#    Click Button                Save
#    Wait until page contains    were successfully created.
#    ${ar_id} =                  Get text      //dl[contains(@class, 'portalMessage')][2]/dd
#    ${ar_id_1} =                Set Variable  ${ar_id.split()[2]}
#    ${ar_id_1} =                Set Variable  ${ar_id_1.split(',')[0]}
#    ${ar_id_2} =                Set Variable  ${ar_id.split()[3]}
#    ${ar_id_2} =                Set Variable  ${ar_id_2.split(',')[0]}
#    Go to                       http://localhost:55001/plone/clients/client-1/analysisrequests
#    Wait until page contains    ${ar_id_1}
#    Page should contain         ${ar_id_2}
#
#Create Primary AR By Row With Template
#    Log in                      test_labmanager  test_labmanager
#    @{time} =                   Get Time        year month day hour min sec
#    Go to                       ${PLONEURL}/clients/client-1
#    Wait until page contains element    css=body.portaltype-client
#    Input text                  ar_count    2
#    Select from list            layout      rows
#    Click Link                  Add
#    Wait until page contains    Request new analyses
#    Select from dropdown        Contact                     Rita
#    Select Date                 ar_0_SamplingDate           @{time}[2]
#    Select from dropdown        ar_0_Template               Bore
#    Set Selenium Timeout        10
#    ${Analyses} =               Get value    xpath=//input[@id="ar_0_Analyses"]
#    Log                         ${Analyses}
#    Should Be Equal             ${Analyses}    Calcium, Magnesium
#    Click Button                Save
#    Wait until page contains    was successfully created.
#    ${ar_id} =                  Get text      //dl[contains(@class, 'portalMessage')][2]/dd
#    ${ar_id} =                  Set Variable  ${ar_id.split()[2]}
#    Go to                       http://localhost:55001/plone/clients/client-1/analysisrequests
#    Wait until page contains    ${ar_id}
#    Select checkbox             xpath=//input[@item_title="${ar_id}"]
#    Click button                xpath=//input[@value="Receive sample"]
#    Wait until page contains    saved
#    [return]                    ${ar_id}
#
#
#Create Secondary AR
#    Log in                      test_labmanager  test_labmanager
#    @{time} =                   Get Time        year month day hour min sec
#    Go to                       ${PLONEURL}/clients/client-1
#    Wait until page contains element    css=body.portaltype-client
#    Click Link                  Add
#    Wait until page contains    Request new analyses
#    Select from dropdown        ar_0_Contact                Rita
#    Select from dropdown        ar_0_Template               Bruma
#    select from dropdown        ar_0_Sample
#    Set Selenium Timeout        30
#    Click Button                Save
#    Set Selenium Timeout        2
#    Wait until page contains    created
#    ${ar_id} =                  Get text      //dl[contains(@class, 'portalMessage')][2]/dd
#    ${ar_id} =                  Set Variable  ${ar_id.split()[2]}
#    [return]                    ${ar_id}
#
#Complete ar_add form with template ${template}
#    Wait until page contains    Request new analyses
#    @{time} =                   Get Time        year month day hour min sec
#    SelectDate                  ar_0_SamplingDate   @{time}[2]
#    Select from dropdown        ar_0_Contact       Rita
#    Select from dropdown        ar_0_Priority           High
#    Select from dropdown        ar_0_Template       ${template}
#    Sleep                       5
#    Click Button                Save
#    Wait until page contains    created
#    ${ar_id} =                  Get text      //dl[contains(@class, 'portalMessage')][2]/dd
#    ${ar_id} =                  Set Variable  ${ar_id.split()[2]}
#    [return]                    ${ar_id}
#
#Complete ar_add form Without template
#    @{time} =                  Get Time        year month day hour min sec
#    SelectDate                 ar_0_SamplingDate   @{time}[2]
#    Select From Dropdown       ar_0_SampleType    Water
#    Select from dropdown       ar_0_Contact       Rita
#    Select from dropdown       ar_0_Priority           High
#    Click Element              xpath=//th[@id='cat_lab_Water Chemistry']
#    Select Checkbox            xpath=//input[@title='Moisture' and @name='ar.0.Analyses:list:ignore_empty:record']
#    Click Element              xpath=//th[@id='cat_lab_Metals']
#    Select Checkbox            xpath=//input[@title='Calcium' and @name='ar.0.Analyses:list:ignore_empty:record']
#    Select Checkbox            xpath=//input[@title='Phosphorus' and @name='ar.0.Analyses:list:ignore_empty:record']
#    Click Element              xpath=//th[@id='cat_lab_Microbiology']
#    Select Checkbox            xpath=//input[@title='Clostridia' and @name='ar.0.Analyses:list:ignore_empty:record']
#    Select Checkbox            xpath=//input[@title='Ecoli' and @name='ar.0.Analyses:list:ignore_empty:record']
#    Select Checkbox            xpath=//input[@title='Enterococcus' and @name='ar.0.Analyses:list:ignore_empty:record']
#    Select Checkbox            xpath=//input[@title='Salmonella' and @name='ar.0.Analyses:list:ignore_empty:record']
#    Set Selenium Timeout       60
#    Click Button               Save
#    Wait until page contains   created
#    ${ar_id} =                 Get text      //dl[contains(@class, 'portalMessage')][2]/dd
#    ${ar_id} =                 Set Variable  ${ar_id.split()[2]}
#    [return]                   ${ar_id}
