*** Settings ***

Library         BuiltIn
Library         Collections
Library         Selenium2Library  timeout=5  implicit_wait=0.2
Library         OperatingSystem
Library         String
Resource        keywords.txt
Resource        plone/app/robotframework/selenium.robot
Library         Remote  ${PLONEURL}/RobotRemote
Variables       plone/app/testing/interfaces.py
Variables       bika/lims/tests/variables.py

Suite Teardown  Close All Browsers

Library          DebugLibrary

*** Variables ***

*** Test Cases ***

Test LaChat QuickChem FIA Exporter
    Enable autologin as  Manager
    set autologin username  test_manager
    # create and configure chrome downloads directory
    ${directory}    Join Path    ${OUTPUT DIR}    downloads
    Create Directory    ${directory}
    ${chrome options}=    Evaluate    sys.modules['selenium.webdriver'].ChromeOptions()    sys, selenium.webdriver
    ${prefs}    Create Dictionary    download.default_directory=${directory}
    Call Method    ${chrome options}    add_experimental_option    prefs    ${prefs}
    Create Webdriver    Chrome    chrome_options=${chrome options}
    # Requirements for creating services and ARs:
    ${cat_uid} =  Create Object  bika_setup/bika_analysiscategories  AnalysisCategory  c1  title=test
    ${st_uid} =  Create Object   bika_setup/bika_sampletypes  SampleType  ST1  title=Sample Type 1   Prefix=ST
    ${sp_uid} =  Create Object   bika_setup/bika_samplepoints  SamplePoint  SP1  title=Sample Point 1
    # I will just test two services for a single sample.
    # One of them is Nitrate/Nitrite, to be sure the keywords
    ${service_uid1} =  Create Object  bika_setup/bika_analysisservices  AnalysisService  srv1  title=Nitrate/Nitrite  Keyword=NitrateNitrite  Category=${cat_uid}
    ${service_uid2} =  Create Object  bika_setup/bika_analysisservices  AnalysisService  srv2  title=Ammonia  Keyword=ammonia  Category=${cat_uid}
    # Add a reference sample matching these two analyses
    ${supplier_uid} =  Create Object  bika_setup/bika_suppliers    Supplier    sup1  Name=Reference Supplier
    ${ref_uid} =  Create Object   bika_setup/bika_suppliers/supplier-3  ReferenceSample  ref1  Title=Reference 1  ReferenceResults=[{'uid':'${service_uid1}', 'result':5, 'min':4, 'max':6, 'error':1},{'uid':'${service_uid2}', 'result':5, 'min':4, 'max':6, 'error':1}]
    # And then create a new AR with just these two services.
    # We'll set the ClientSampleID to match the first valid result in the XLSX.
    ${ar_uid} =  Create AR  /clients/client-1  analyses=${service_uid1},${service_uid2}  SampleType=${st_uid}    SamplePoint=${sp_uid}   ClientSampleID=A00036896008
    do action for  ${ar_uid}  receive
    # Create an instrument and link it to our exporter
    Go to  ${PLONEURL}/bika_setup/bika_instruments
    Wait Until Page Contains    Add
    Click Link                  Add
    wait until page contains element    title
    input text  title  LaChat FIA
    select from list  css=#DataInterface   LaChat QuickChem FIA
    click button  Save
    wait until page contains  Changes saved.
    # Create a worksheet for the new instrument
    Go to  ${PLONEURL}/worksheets
    wait until page contains element  css=.analyst
    select from list  css=.analyst    test_analyst
    Select from list  css=.instrument  LaChat FIA
    click element  css=.worksheet_add
    wait until page contains  Add Analyses
    # Add all the analyses from our test AR to the new worksheet
    click element  css=#list_select_all
    click element  css=#assign_transition
    wait until page contains element  css=#submit_transition
    # Create TWO Duplicates of slot 1, to test that both are exported once each.
    wait until page contains element  css=#contentview-add_duplicate a
    click element  css=#contentview-add_duplicate a
    wait until page contains element  css=[title='ST-0001-R01']
    click element  css=[title='ST-0001-R01']
    wait until page contains element  css=#contentview-add_duplicate a
    click element  css=#contentview-add_duplicate a
    wait until page contains element  css=[title='ST-0001-R01']
    click element  css=[title='ST-0001-R01']
    # Add TWO controls, to be sure each is exported exactly once.
    wait until page contains element  css=#contentview-add_control a
    click element  css=#contentview-add_control a
    wait until page contains element  css=#worksheet_add_references .bika-listing-table tbody.item-listing-tbody tr
    click element  css=#worksheet_add_references .bika-listing-table tbody.item-listing-tbody tr
    wait until page contains element  css=#contentview-add_control a
    click element  css=#contentview-add_control a
    wait until page contains element  css=#worksheet_add_references .bika-listing-table tbody.item-listing-tbody tr
    click element  css=#worksheet_add_references .bika-listing-table tbody.item-listing-tbody tr
    # Do the export!
    wait until page contains element  css=#contentview-export a
    click element  css=#contentview-export a
    sleep   2
    ${files}    List Files In Directory    ${directory}
    Length Should Be    ${files}    1    Should be one file in the download folder
    ${file}    Join Path    ${directory}    ${files[0]}
    ${actual}  Get File   ${file}
    ${expected}=  catenate  SEPARATOR=\n
    ...  1,[ST-0001-R01] Sample Point 1,1,,1
    ...  2,ST-0001-P1-D01,2,,1
    ...  3,ST-0001-P1-D02,3,,1
    ...  4,QC-001-001,4,,1
    ...  5,QC-001-002,5,,1
    Should be equal  ${expected}  ${actual}
    Remove Directory 	${directory}  recursive=True


Test LaChat QuickChem FIA Importer
    Start browser
    Enable autologin as  Manager
    set autologin username  test_manager
    # Requirements for creating services and ARs:
    ${cat_uid} =  Create Object  bika_setup/bika_analysiscategories  AnalysisCategory  c1  title=test
    ${st_uid} =  Create Object   bika_setup/bika_sampletypes  SampleType  ST1  title=Sample Type   Prefix=ST
    # I will just test two services for a single sample.
    # One of them is Nitrate/Nitrite, to be sure the keywords
    ${service_uid1} =  Create Object  bika_setup/bika_analysisservices  AnalysisService  s1  title=Nitrate/Nitrite  Keyword=NitrateNitrite  Category=${cat_uid}
    ${service_uid2} =  Create Object  bika_setup/bika_analysisservices  AnalysisService  s2  title=Ammonia  Keyword=ammonia  Category=${cat_uid}
    # And then create a new AR with just these two services.
    # We'll set the ClientSampleID to match the first valid result in the XLSX.
    ${ar_uid} =  Create AR  /clients/client-1  analyses=${service_uid1},${service_uid2}  SampleType=${st_uid}   ClientSampleID=A00036896008
    do action for  ${ar_uid}  receive
    # Do the import!
    Go to  ${PLONEURL}
    Click Link  Import
    Wait until page contains  Select a data interface
    Select from list  exim  LaChat QuickChem FIA
    # This instrument supports only CSV
    Element Should Contain  lachat_quickchem_fia_format  CSV
    ${PATH_TO_TEST} =  run keyword  resource_filename
    Choose File  lachat_quickchem_fia_file  ${PATH_TO_TEST}/files/QuickChemFIA.csv
    Click Button  Submit
    Wait until page contains  Log trace
    # Only one AR (two analyses) should have been imported!
    page should contain  End of file reached successfully: 20 objects, 3 analyses, 549 results
    page should contain  ST-0001-R01: ['Analysis NitrateNitrite', 'Analysis ammonia'] imported sucessfully
    page should contain  Import finished successfully: 1 ARs and 2 results updated
    # And we must verify that the results are valid
    go to    ${PLONEURL}/clients/client-1/ST-0001-R01/manage_results
    textfield value should be  css=[selector="Result_ammonia"]  1.68
    textfield value should be  css=[selector="Result_NitrateNitrite"]  11.58

*** Keywords ***

Start browser
    Open browser                        ${PLONEURL}  chrome
    Set selenium speed                  ${SELENIUM_SPEED}
