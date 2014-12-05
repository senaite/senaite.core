*** Settings ***

Library          BuiltIn
Library          Selenium2Library  timeout=5  implicit_wait=0.2
Library          String
Resource         keywords.txt
Library          bika.lims.testing.Keywords
Resource         plone/app/robotframework/selenium.robot
Resource         plone/app/robotframework/saucelabs.robot
Variables        plone/app/testing/interfaces.py
Variables        bika/lims/tests/variables.py
Suite Setup      Start browser
#Suite Teardown   Close All Browsers

*** Variables ***

${ar_factory_url}  portal_factory/AnalysisRequest/xxx/ar_add

*** Test Cases ***

Check that automatic expanded and restricted categories expand and restrict
    # Check that automatic expanded and restricted categories expand and restrict
    # set preferences to Restrict='Microbiology' and Default='Metals'
    Go to                              ${PLONEURL}/clients/client-1/edit/#fieldsetlegend-preferences
    select from list                   RestrictedCategories:list   Microbiology
    select from list                   DefaultCategories:list      Metals
    click button                       Save
    wait until page contains           saved
    # Bring up the AR Add form
    Go to                              ${PLONEURL}/clients/client-1/${ar_factory_url}
    wait until page contains           xxx
    # Check that Microbiology category is RESTRICTED
    page should not contain element    css=th[cat=Microbiology]
    # Check that Metals category is EXPANDED
    wait until page contains element   css=th[cat=Metals].expanded

Contact is selected
    # Bring up the AR Add form
    Go to                              ${PLONEURL}/clients/client-1/${ar_factory_url}
    wait until page contains           xxx
    # when Contact is selected, CC Contacts are selected
    select from dropdown               ar_0_Contact         Rita
    xpath should match x times         xpath=.//[contains(@class, .reference_multi_item)]   1

AR Template selected
    Go to                              ${PLONEURL}/clients/client-1/${ar_factory_url}
    wait until page contains           xxx
    # when Template is selected
    select from dropdown               ar_0_Template                Bruma
    # Check that Metals category is EXPANDED
    wait until page contains element   css=th[cat=Metals].expanded
    # check field values are filled correctly
    textfield value should be          ar_0_SampleType              Water
    textfield value should be          ar_0_SamplePoint             Bruma Lake
    textfield value should be          ar_0_AnalysisSpecification   Water
    # 7 analysis services should be selected
    xpath should match x times         xpath=.//input[@type='checkbox' and @checked]     7
    xpath should match x times         xpath=.//input[@type='text' and .="9"]            7
    xpath should match x times         xpath=.//input[@type='text' and .="11"]           7
    xpath should match x times         xpath=.//input[@type='text' and .="10"]           7

    # XXX Check that prices are correctly calculated

AR Profile selected
    Go to                              ${PLONEURL}/clients/client-1/${ar_factory_url}
    wait until page contains           xxx

    # when Template is selected
    select from dropdown               ar_0_SampleType        Apple
    select from dropdown               ar_0_Profile           Hardness
    # Check that Metals and Water Chemistry are EXPANDED
    wait until page contains element   css=th[cat=Metals].expanded
    wait until page contains element   css=th[cat=Water Chemistry].expanded
    # 3 analysis services should be selected
    xpath should match x times         xpath=.//input[@type='checkbox' and @checked]     3

    # XXX Check that prices are correctly calculated

Test Specification
    Go to                              ${PLONEURL}/clients/client-1/${ar_factory_url}
    wait until page contains           xxx
    # setting spec directly should modify fields
    select from dropdown               ar_1_Profile           Hardness
    select from dropdown               ar_1_SampleType        Apple
    textfield value should be          ar_1_AnalysisSpecification   Apple Pulp
    xpath should match x times         xpath=.//input[@type='text' and .="9"]            6
    # setting SampleType must set the spec
    select from dropdown               ar_0_Profile           Hardness
    select from dropdown               ar_0_SampleType        Apple
    textfield value should be          ar_0_AnalysisSpecification   Apple Pulp
    xpath should match x times         xpath=.//input[@type='text' and .="9"]            3


Check that ST<-->SP restrictions are in place
    Go to                              ${PLONEURL}/clients/client-1/${ar_factory_url}
    wait until page contains           xxx
    # selecting samplepoint Borehole 12: only "Water" sampletype should
    # be available.
    select from dropdown               ar_0_SamplePoint           Borehole
    run keyword and expect error   *   select from dropdown       ar_0_SampleType    Barley
    select from dropdown               ar_0_SampleType            Water
    select from dropdown               ar_1_SampleType            Water
    run keyword and expect error   *   select from dropdown       ar_1_SamplePoint    Mill
    select from dropdown               ar_1_SamplePoint           Bruma

Test prices
    # HAPPY HILLS - Bulk discount N, member discount Y
    Go to                              ${PLONEURL}/clients/client-1/portal_factory/AnalysisRequest/xx0/ar_add
    wait until page contains           xx0
    select from dropdown               ar_0_Template          Hardness
    select from dropdown               ar_1_Profile           Hardness
    select checkbox         ccc

    # Klaymore - Bulk discount Y, member discount N
    Go to                              ${PLONEURL}/clients/client-1/portal_factory/AnalysisRequest/xx1/ar_add
    wait until page contains           xx1

    # Myrtle - Bulk discount N, member discount N
    Go to                              ${PLONEURL}/clients/client-1/portal_factory/AnalysisRequest/xx2/ar_add
    wait until page contains           xx2

    # Ruff - Bulk discount Y, member discount Y
    Go to                              ${PLONEURL}/clients/client-1/portal_factory/AnalysisRequest/xx3/ar_add
    wait until page contains           xx3




# select-all checkbox select's  all

#when Copy-Across is selected:
#    Make sure that it works for reference fields and their _uid counterparts
#    All fields tested here, must have their tests run against the copy-across machine.
#        - This must be done for all four test columns.
#        - Check the state_variable completely

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
#when selecting Sample:
#    Check that the secondary sample fields are filled in correctly.
#    Submit and check that the AR is correctly created.
#




*** Keywords ***

Start browser
    Open browser                http://localhost:55001/plone/login
    Log in                      test_labmanager    test_labmanager
    Set selenium speed          ${SELENIUM_SPEED}

Prices in column ${col_nr} should be: ${discount} ${subtotal} ${vat} ${total}
    element text should be      xpath=.//input[@id=ar_${col_nr}_discount]    ${discount}
    element text should be      xpath=.//input[@id=ar_${col_nr}_subtotal]    ${subtotal}
    element text should be      xpath=.//input[@id=ar_${col_nr}_vat]         ${vat}
    element text should be      xpath=.//input[@id=ar_${col_nr}_total]       ${total}

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
