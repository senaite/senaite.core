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
Suite Teardown   Close All Browsers

Library          DebugLibrary

*** Variables ***

${ar_factory_url}  portal_factory/AnalysisRequest/xxx/ar_add

*** Test Cases ***

### First, some general things that are the same for all column layouts

General AR Add javascript tests
    Go to                              ${PLONEURL}/clients/client-1/${ar_factory_url}
    wait until page contains           xxx

# When Contact is selected, expand CC Contacts

    select from dropdown               css=tr[fieldname='Contact'] td[arnum='0'] input[type='text']       Rita
    xpath should match x times         .//div[contains(@class, 'reference_multi_item')]   1
    select from dropdown               css=tr[fieldname='Contact'] td[arnum='0'] input[type='text']       Neil
    xpath should match x times         .//div[contains(@class, 'reference_multi_item')]   2

# Check that ST<-->SP soft-restrictions are in place

    # First: SamplePoint "Borehole 12": only "Water" sampletype should be visible by default
    # but should still be allowed to select non-matching SampleType if we want to (Barley)
    select from dropdown               css=tr[fieldname='SamplePoint'] td[arnum='0'] input[type='text']   Borehole
    click element                      css=tr[fieldname='SampleType'] td[arnum='0'] input[type='text']
    xpath should match x times         .//div[contains(@class, 'cg-menu-item')]   1
    select from dropdown               css=tr[fieldname='SampleType'] td[arnum='0'] input[type='text']    Barley

    # Second: SampleType "Water" should show only two SamplePoints when SamplePoint element is clicked
    # but should still be allowed to select non-matching SamplePoint if we want to (Dispatch)
    select from dropdown               css=tr[fieldname='SampleType'] td[arnum='1'] input[type='text']    Water
    click element                      css=tr[fieldname='SamplePoint'] td[arnum='1'] input[type='text']
    xpath should match x times         .//div[contains(@class, 'cg-menu-item')]   2
    select from dropdown               css=tr[fieldname='SamplePoint'] td[arnum='1'] input[type='text']   Dispatch

# when Report as Dry Matter is selected

    select checkbox                    css=tr[fieldname='ReportDryMatter'] td[arnum='0'] input[type='checkbox']
    log  XXX  warn
    #Check that DryMatterService is selected.
    #Check that prices are correctly calculated

# generic copy-across: select, checkbox, plain-textfield, reference-textfield

    log  XXX copy-across general   WARN

# copy-across: drymatter, template, profile, contact-with-cc, cc, samplepoint<->sampletype

    log  XXX copy-across specific  WARN

BikaListing AR Add javascript tests

    Enable bikalisting form
    Go to                              ${PLONEURL}/clients/client-1/${ar_factory_url}
    wait until page contains           xxx



SingleService AR Add javascript tests

    Enable singleservice form
    Go to                              ${PLONEURL}/clients/client-1/${ar_factory_url}
    wait until page contains           xxx

# AR Templates

    # first select a random service (all columns), to be sure it is unselected
    # again when template/profile are
    select checkbox                    css=input[name='uids:list']
    xpath should match x times         .//*[@checked='checked']    5
    select from dropdown               css=#singleservice    cod
    wait until page contains           COD
    # then select a template...
    select from dropdown               css=tr[fieldname='Template'] td[arnum='0'] input[type='text']        Hardness
    Wait Until Keyword Succeeds 	   5 sec    1 sec    textfield value should be     css=tr[fieldname='SamplePoint'] td[arnum='0'] input[type='text']        Borehole 12
    # check field values are filled correctly
    textfield value should be          css=tr[fieldname='SampleType'] td[arnum='0'] input[type='text']      Water
    textfield value should be          css=tr[fieldname='Specification'] td[arnum='0'] input[type='text']   Water
    # in column 0: 4 checkboxes checked (includes drymatter) and 4 with specs.
    xpath should match x times         .//td[@arnum='0']//input[@type='checkbox' and @checked]     4
    # in column 0: 4 total fields with 9/10/11 values present in them
    xpath should match x times         .//td[@arnum='0']//input[@value="9"]                        4
    xpath should match x times         .//td[@arnum='0']//input[@value="11"]                       4
    xpath should match x times         .//td[@arnum='0']//input[@value="10"]                       4
    # in column 0: there should be three partnr spans with "1" in them
    xpath should match x times        .//td[@arnum='0']//span[@class='partnr' and text()="1"]      3

    # A different template
    select from dropdown               css=tr[fieldname='Template'] td[arnum='0'] input[type='text']        Bruma
    Wait Until Keyword Succeeds 	   5 sec    1 sec    textfield value should be     css=tr[fieldname='SamplePoint'] td[arnum='0'] input[type='text']        Bruma Lake
    # in column 0: 7 selections, 9 with specs
    xpath should match x times         .//td[@arnum='0']//input[@type='checkbox' and @checked]     7
    # in column 0: 9 total fields with 9/10/11 values present in them
    xpath should match x times         .//td[@arnum='0']//input[@value="9"]                        9
    xpath should match x times         .//td[@arnum='0']//input[@value="11"]                       9
    xpath should match x times         .//td[@arnum='0']//input[@value="10"]                       9
    # in column 0: there should be three partnr spans with "1" in them
    xpath should match x times        .//td[@arnum='0']//span[@class='partnr' and text()="1"]      7

# Analysis Profiles

    # total hardness has three services
    select from dropdown               css=tr[fieldname='Profile'] td[arnum='1'] input[type='text']         Hardness
    xpath should match x times         .//td[@arnum='1']/input[@type='checkbox' and @checked]      3
    # trace metals has eight.
    select from dropdown               css=tr[fieldname='Profile'] td[arnum='1'] input[type='text']         Trace
    xpath should match x times         .//td[@arnum='1']/input[@type='checkbox' and @checked]      8

# Manually adding/removing services

    # Should not allow duplicating service rows
    select from dropdown               css=#singleservice    cod
    select from dropdown               css=#singleservice    cod
    xpath should match x times         .//tr[@keyword='COD']      1



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

Enable singleservice form
    go to                       ${PLONEURL}/bika_setup/edit
    wait until page contains    Password lifetime
    click link                  fieldsetlegend-analyses
    wait until page contains    AR Add service selector
    select from list            ARAddServiceSelector     Single service selection form
    click button                Save
    wait until page contains    saved.

Enable bikalisting form
    go to                       ${PLONEURL}/bika_setup/edit
    wait until page contains    Password lifetime
    click link                  fieldsetlegend-analyses
    wait until page contains    AR Add service selector
    select from list            ARAddServiceSelector     Categorised service list form
    click button                Save
    wait until page contains    saved.

