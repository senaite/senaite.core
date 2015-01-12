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

${client1_factory_url}  ${PLONEURL}/clients/client-1/portal_factory/AnalysisRequest/xxx/ar_add?layout=columns&ar_count=5
${client2_factory_url}  ${PLONEURL}/clients/client-2/portal_factory/AnalysisRequest/yyy/ar_add?layout=columns&ar_count=5

*** Test Cases ***

### First, some general things that are the same for all column layouts

General AR Add javascript tests
    Go to                              ${client1_factory_url}
    wait until page contains           xxx

### When Contact is selected, expand CC Contacts

    select from dropdown               css=#Contact-0        Rita
    xpath should match x times         .//div[contains(@class, 'reference_multi_item')]   1
    select from dropdown               css=#Contact-0        Neil
    xpath should match x times         .//div[contains(@class, 'reference_multi_item')]   2

### Check that ST<-->SP soft-restrictions are in place

    # First: SamplePoint "Borehole 12": only "Water" sampletype should be visible by default
    # but should still be allowed to select non-matching SampleType if we want to (Barley)

    select from dropdown               css=#SamplePoint-0    Borehole
    click element                      css=#SampleType-0
    xpath should match x times         .//div[contains(@class, 'cg-menu-item')]   1
    select from dropdown               css=#SampleType-0     Barley

    # Second: SampleType "Water" should show only two SamplePoints when SamplePoint element is clicked
    # but should still be allowed to select non-matching SamplePoint if we want to (Dispatch)

    select from dropdown               css=#SampleType-1    Water
    click element                      css=#SamplePoint-1
    xpath should match x times         .//div[contains(@class, 'cg-menu-item')]   2
    select from dropdown               css=#SamplePoint-1   Dispatch

### copy-across:

    # contact (reference, multivalued reference, and CC Contacts)
    select from dropdown               css=#Contact-0       Rita
    click element                      css=tr[fieldname='Contact'] img.copybutton
    textfield value should be          css=#Contact-4       Rita Mohale
    xpath should match x times         .//div[contains(@class, 'reference_multi_item')]    5

    # ccemails (regular text field)
    input text                         css=#CCEmails-0       asdf@example.com
    click element                      css=tr[fieldname='CCEmails'] img.copybutton
    textfield value should be          css=#CCEmails-4m

    # select element
    select from list                   css=#PreparationWorkflow-0 select
    click element                      css=tr[fieldname='PreparationWorkflow'] img.copybutton
    list selection should be           css=#PreparationWorkflow-4      Simple one-step

    # Checkboxes
    select checkbox                    css=#ReportDryMatter-0
    click element                      css=tr[fieldname='ReportDryMatter'] img.copybutton
    checkbox should be selected        css=#ReportDryMatter-4

### minimal AR to test AR creation with SamplingWorkflow.
    # This must be done befor the client-filter test, because we must
    # test the filtering of Samples.
    log    minimal AR to test AR creation with SamplingWorkflow   WARN

### sticker printout triggered when setup/labels='register'
    log    sticker printout triggered when setup/labels='register'   WARN


### Client-filter on elements must be respected.
    Go to                              ${client2_factory_url}
    wait until page contains           yyy
		# Contact
		# CCContact
		# InvoiceContact
		# SamplePoint
		# Template
		# Profile
		# Specification



BikaListing AR Add javascript tests

    Enable bikalisting form
    Go to                              ${client1_factory_url}
    wait until page contains           xxx

### Select-all checkbox stuff

    # click path
    select checkbox                    css=input[name='uids:list'][item_title='COD']
    xpath should match x times         .//*[@checked='checked']    6
    unselect checkbox                  css=input[name='uids:list'][item_title='COD']
    xpath should match x times         .//*[@checked='checked']    0

### AR Templates

    # select COD to see if it is correctly unselected later
    select checkbox                    css=input[name='uids:list'][item_title='COD']

    # then select a template...
    select from dropdown               css=#Template-0        Hardness
    Wait Until Keyword Succeeds 	   5 sec    1 sec    textfield value should be     css=#SamplePoint-0        Borehole 12
    textfield value should be          css=#SampleType-0      Water
    textfield value should be          css=#Specification-0   Water
    # dry matter
    checkbox should be selected        css=#ReportDryMatter-0
    # services
    xpath should match x times         .//td[contains(@class, 'ar.0')]//input[@type='checkbox' and @checked]     4
    # specifications
    xpath should match x times         .//td[contains(@class, 'ar.0')]//input[@value="9"]          20
    xpath should match x times         .//td[contains(@class, 'ar.0')]//input[@value="11"]         20
    xpath should match x times         .//td[contains(@class, 'ar.0')]//input[@value="10"]         20
    # partnrs
    xpath should match x times        .//td[contains(@class, 'ar.0')]//span[@class='partnr' and text()="1"]      4

    # A different template
    select from dropdown               css=#Template-1        Bruma
    Wait Until Keyword Succeeds 	   5 sec    1 sec    textfield value should be     css=#SamplePoint-1        Bruma Lake
    # dry matter
    checkbox should be selected        css=#ReportDryMatter-0
    # services
    xpath should match x times         .//td[contains(@class, 'ar.1')]//input[@type='checkbox' and @checked]     7
    # partnrs
    xpath should match x times         .//td[contains(@class, 'ar.1')]//span[@class='partnr' and text()="1"]      7

### Price display

    # one of these services is calculated at 25% VAT
    element text should be      css=td[arnum='0'] span.discount        6.00
    element text should be      css=td[arnum='0'] span.subtotal        34.00
    element text should be      css=td[arnum='0'] span.vat             5.70
    element text should be      css=td[arnum='0'] span.total           39.69

    element text should be      css=td[arnum='1'] span.discount        1.50
    element text should be      css=td[arnum='1'] span.subtotal        8.50
    element text should be      css=td[arnum='1'] span.vat             1.19
    element text should be      css=td[arnum='1'] span.total           9.69

### Analysis Profiles

    # total hardness has three services

    select from dropdown               css=#Profile-2              Hardness
    wait until page contains element   xpath=.//td[contains(@class, 'ar.2')]//input[@type='checkbox' and @checked]
    xpath should match x times         .//td[contains(@class, 'ar.2')]//input[@type='checkbox' and @checked]        3

    # trace metals has eight.

    select from dropdown               css=#Profile-3              Trace
    wait until page contains element   xpath=.//td[contains(@class, 'ar.3')]//input[@type='checkbox' and @checked]
    xpath should match x times         .//td[contains(@class, 'ar.3')]//input[@type='checkbox' and @checked]        8

### Dependencies

    # selecting Dry Matter should require the 'Moisture' service

    select checkbox                    css=tr[title='Dry Matter'] td[class*='ar.1'] input[type='checkbox']
    page should contain                Do you want to apply these selections now
    click element                      xpath=.//button[.//span[contains(text(), 'yes')]]
    sleep                              .25
    checkbox should be selected        css=tr[title='Moisture'] td[class*='ar.1'] input[type='checkbox']

    # unselecting Moisture should remove the 'Dry Matter' service

    unselect checkbox                  css=tr[title='Moisture'] td[class*='ar.1'] input[type='checkbox']
    page should contain                Do you want to remove these selections now
    click element                      xpath=.//button[.//span[contains(text(), 'yes')]]
    sleep                              .25
    checkbox should not be selected    css=tr[title='Dry Matter'] td[class*='ar.1'] input[type='checkbox']

### Report as Dry Matter should select DryMatter and Moisture services

    select checkbox                    css=#ReportDryMatter-4
    checkbox should be selected        css=tr[title='Dry Matter'] td[class*='ar.4'] input[type='checkbox']
    checkbox should be selected        css=tr[title='Moisture'] td[class*='ar.4'] input[type='checkbox']

    log   BikaListing when Create Profile button is clicked     WARN
    log   BikaListing when Sample is selected (secondary AR)     WARN
    log   BikaListing when copy_from is specified in request     WARN



### Submit and verify one with everything

SingleService AR Add javascript tests

    Enable singleservice form
    Go to                              ${client1_factory_url}
    wait until page contains           xxx

### Select-all checkbox stuff

    select checkbox                    css=input[name='uids:list']
    xpath should match x times         .//*[@checked='checked']    6
    unselect checkbox                  css=input[name='uids:list']
    xpath should match x times         .//*[@checked='checked']    0

### AR Templates

    # select COD to see if it is correctly unselected later
    select checkbox                    css=input[name='uids:list']
    select from dropdown               css=#singleservice    cod
    wait until page contains           COD

    # select a template...
    select from dropdown               css=#Template-0           Hardness
    Wait Until Keyword Succeeds 	   5 sec    1 sec    textfield value should be     css=#SamplePoint-0        Borehole 12
    textfield value should be          css=#SampleType-0          Water
    textfield value should be          css=#Specification-0       Water
    # dry matter
    checkbox should be selected        css=#ReportDryMatter-0
    # selected services
    xpath should match x times         .//td[contains(@class, 'ar.0')]//input[@type='checkbox' and @checked]     4
    # spec values
    xpath should match x times         .//td[contains(@class, 'ar.0')]//input[@value="9"]                        5
    xpath should match x times         .//td[contains(@class, 'ar.0')]//input[@value="11"]                       5
    xpath should match x times         .//td[contains(@class, 'ar.0')]//input[@value="10"]                       5
    # partnrs
    xpath should match x times        .//td[contains(@class, 'ar.0')]//span[@class='partnr' and text()="1"]      4

    # A different template
    select from dropdown               css=#Template-0            Bruma
    Wait Until Keyword Succeeds 	   5 sec    1 sec    textfield value should be     css=#SamplePoint-0        Bruma Lake
    # dry matter
    checkbox should be selected        css=#ReportDryMatter-0
    # selected services
    xpath should match x times         .//td[contains(@class, 'ar.0')]//input[@type='checkbox' and @checked]     7
    # spec values
    xpath should match x times         .//td[contains(@class, 'ar.0')]//input[@value="9"]                        10
    xpath should match x times         .//td[contains(@class, 'ar.0')]//input[@value="11"]                       10
    xpath should match x times         .//td[contains(@class, 'ar.0')]//input[@value="10"]                       10
    # partnrs
    xpath should match x times        .//td[contains(@class, 'ar.0')]//span[@class='partnr' and text()="1"]      7

### Price display

    wait until page contains           10.50
    wait until page contains           59.50
    wait until page contains           9.27
    wait until page contains           68.76

### Analysis Profiles

    # total hardness has three services
    select from dropdown               css=#Profile-1         Hardness
    xpath should match x times         .//td[contains(@class, 'ar.1')]//input[@type='checkbox' and @checked]      3

    # trace metals has eight.
    select from dropdown               css=#Profile-1         Trace
    xpath should match x times         .//td[contains(@class, 'ar.1')]//input[@type='checkbox' and @checked]      8

### Manually adding/removing services

    # Should not allow duplicating service rows
    select from dropdown               css=#singleservice    cod
    select from dropdown               css=#singleservice    cod
    xpath should match x times         .//tr[@keyword='COD']      1

### Dependencies

    # selecting Dry Matter should require the 'Moisture' service
    select checkbox                    css=tr[title='Dry Matter'] td[class*='ar.1'] input[type='checkbox']
    page should contain                Do you want to apply these selections now
    click element                      xpath=.//button[.//span[contains(text(), 'yes')]]
    sleep                              .25
    checkbox should be selected        css=tr[title='Moisture'] td[class*='ar.1'] input[type='checkbox']

    # unselecting Moisture should remove the 'Dry Matter' service
    unselect checkbox                  css=tr[title='Moisture'] td[class*='ar.1'] input[type='checkbox']
    page should contain                Do you want to remove these selections now
    click element                      xpath=.//button[.//span[contains(text(), 'yes')]]
    sleep                              .25
    checkbox should not be selected    css=tr[title='Dry Matter'] td[class*='ar.1'] input[type='checkbox']


    log   SingleService when Create Profile button is clicked     WARN
    log   SingleService when Sample is selected (secondary AR)     WARN
    log   SingleService when copy_from is specified in request     WARN

### Submit and verify one with everything



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

