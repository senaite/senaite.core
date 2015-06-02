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

*** Test Cases ***

Contact is selected, CC Contacts should be automated
  Enable autologin as  LabClerk
  Given an ar add form in client-1 with columns layout and 1 ars
   When I select Rita Mohale from the Contact combogrid in column 0
   Then the CCContact field selections in column 0 should contain Ŝarel Seemonster

SamplePoint is selected, SampleType should be filtered
  Enable autologin as  LabClerk
  Given an ar add form in client-1 with columns layout and 1 ars
   When I select Borehole 12 from the SamplePoint combogrid in column 0
   Then There should be 1 entries in the SampleType combogrid in column 0

Some fields should be filtered depending on the Client
  Enable autologin as  LabClerk
  # Contact
  Given an ar add form in client-1 with columns layout and 1 ars
   Then I can not select Johanna Smith from the Contact combogrid in column 0
  Given an ar add form in client-2 with columns layout and 1 ars
   Then I select Johanna Smith from the Contact combogrid in column 0
  # SamplePoint
  Given an ar add form in client-1 with columns layout and 1 ars
   Then I can not select Klaymore Shaft 1 from the SamplePoint combogrid in column 0
  Given an ar add form in client-2 with columns layout and 1 ars
  debug
   Then I select Klaymore Shaft 1 from the SamplePoint combogrid in column 0

Copy-Across button for various fields/types
  # Contact copy-across
  Given an ar add form in client-1 with columns layout and 3 ars
   When I select Neil Ŝtandard from the Contact combogrid in column 0
    and I click the copy-across button for the Contact field
   Then the Contact value in column 2 should be Neil Ŝtandard
    and the CCContact field selections in column 2 should contain Ŝarel Seemonster
    and the CCContact field selections in column 2 should contain Rita Mohale
  # Remove Rita, and copy again:
  Given an ar add form in client-1 with columns layout and 3 ars
   When I select Neil Ŝtandard from the Contact combogrid in column 0
    and I click the copy-across button for the Contact field
   Then the Contact value in column 2 should be Neil Ŝtandard
    and the CCContact field selections in column 2 should contain Ŝarel Seemonster
    and the CCContact field selections in column 2 should contain Rita Mohale



*** Keywords ***

# --- Given ------------------------------------------------------------------

an ar add form in ${client_id} with ${layout} layout and ${ar_count} ars
    [Documentation]  Load a fresh AR Add form.
    go to  ${PLONEURL}/clients/${client_id}/portal_factory/AnalysisRequest/xxx/ar_add?layout=${layout}&ar_count=${ar_count}
    wait until page contains  xxx

# --- When -------------------------------------------------------------------

I select ${searchterm} from the ${field} combogrid in column ${column}
    [Documentation]  Search and select ${searchterm} from a referencewidget.
    wait until page contains element  css=#${field}-${column}
    Input text  css=#${field}-${column}  ${searchterm}
    sleep  1
    Click Element  xpath=//div[contains(@class,'cg-colItem')][1]

I can not select ${searchterm} from the ${field} combogrid in column ${column}
    [Documentation]  This combogrid should be filtered so the selection should not be possible
    wait until page contains element  css=#${field}-${column}
    Input text  css=#${field}-${column}  ${searchterm}
    sleep  1
    Element should not be visible   xpath=//div[contains(@class,'cg-colItem')][1]

# --- Then -------------------------------------------------------------------

the ${field} field selections in column ${column} should contain ${selection_string}
    [Documentation]  Check that a multivalued referencewidget has a specific selection.
    xpath should match x times  .//div[@id='${field}-${column}-listing']//div[.='${selection_string}']  1

the ${field} value in column ${column} should be ${value}
    [Documentation]  Check that a text-field has a certain value
    textfield value should be  css=#${field}-${column}      ${value}

There should be ${nr} entries in the ${field} combogrid in column ${column}
    Input text  css=#${field}-${column}  \
    sleep  1
    xpath should match x times  //div[contains(@class,'cg-colItem')][1]  ${nr}


#### copy-across:
#
#    # contact (reference, multivalued reference, and CC Contacts)
#    select from dropdown               css=#Contact-0       Rita
#    click element                      css=tr[fieldname='Contact'] img.copybutton
#    # wait until page contains element   xpath=.//input[@id="Contact-4" and @value="Rita Mohale"]
#    sleep       1
#    textfield value should be          css=#Contact-4       Rita Mohale
#    xpath should match x times         .//div[contains(@class, 'reference_multi_item')]    5
#
#    # ccemails (regular text field)
#    input text                         css=#CCEmails-0       asdf@example.com
#    click element                      css=tr[fieldname='CCEmails'] img.copybutton
#    textfield value should be          css=#CCEmails-4       asdf@example.com
#
#    # Checkboxes
#    select checkbox                    css=#ReportDryMatter-0
#    click element                      css=tr[fieldname='ReportDryMatter'] img.copybutton
#    checkbox should be selected        css=#ReportDryMatter-4
#
#Prices are hidden when Show Prices is disabled
#    Log in                             test_labmanager    test_labmanager
#    Disable Prices
#    Go to                              ${client1_factory_url}
#    wait until page contains           xxx
#
#    page should not contain element    css=span.discount
#    page should not contain element    css=span.subtotal
#    page should not contain element    css=span.vat
#    page should not contain element    css=span.total
#
#### Select-all checkbox stuff ( single-service selector from develop)
#    click element                      css=table[form_id='lab'] th[cat='Water Chemistry']
#    select checkbox                    css=input[name='uids:list'][item_title='COD']
#    xpath should match x times         .//*[@checked='checked']    6
#    unselect checkbox                  css=input[name='uids:list'][item_title='COD']
#    xpath should match x times         .//*[@checked='checked']    0
#
#### AR Templates
#
#    # select COD to see if it is correctly unselected later
#    select checkbox                    css=input[name='uids:list'][item_title='COD']
#
#    # then select a template...
#    select from dropdown               css=#Template-0        Hardness
#    Wait Until Keyword Succeeds 	   5 sec    1 sec    textfield value should be     css=#SamplePoint-0        Borehole 12
#    textfield value should be          css=#SampleType-0      Water
#    textfield value should be          css=#Specification-0   Water
#    checkbox should be selected        css=#ReportDryMatter-0
#    # services
#
#    xpath should match x times         .//td[contains(@class, 'ar.0')]//input[@type='checkbox' and @checked]     4
#    # specifications
#    xpath should match x times         .//td[contains(@class, 'ar.0')]//input[@value="9"]          15
#    xpath should match x times         .//td[contains(@class, 'ar.0')]//input[@value="11"]         15
#    xpath should match x times         .//td[contains(@class, 'ar.0')]//input[@value="10"]         15
#    # partnrs
#    xpath should match x times        .//td[contains(@class, 'ar.0')]//span[@class='partnr' and text()="1"]      2
#
#    # A different template
#
#    select from dropdown               css=#Template-1        Bruma
#    Wait Until Keyword Succeeds 	   5 sec    1 sec    textfield value should be     css=#SamplePoint-1        Bruma Lake
#    # dry matter
#    checkbox should be selected        css=#ReportDryMatter-0
#    # services
#    xpath should match x times         .//td[contains(@class, 'ar.1')]//input[@type='checkbox' and @checked]     7
#    # partnrs
#    xpath should match x times         .//td[contains(@class, 'ar.1')]//span[@class='partnr' and text()="1"]      7
#
#### Price display
#
#    # one of these services is calculated at 25% VAT
#    element text should be      css=td[arnum='0'] span.discount        3.00
#    element text should be      css=td[arnum='0'] span.subtotal        17.00
#    element text should be      css=td[arnum='0'] span.vat             2.38
#    element text should be      css=td[arnum='0'] span.total           19.38
#
#    element text should be      css=td[arnum='1'] span.discount        1.50
#    element text should be      css=td[arnum='1'] span.subtotal        8.50
#    element text should be      css=td[arnum='1'] span.vat             1.19
#    element text should be      css=td[arnum='1'] span.total           9.69
#
#### Analysis Profiles
#
#    # total hardness has three services
#
#    select from dropdown               css=#Profile-2              Hardness
#    wait until page contains element   xpath=.//td[contains(@class, 'ar.2')]//input[@type='checkbox' and @checked]
#    xpath should match x times         .//td[contains(@class, 'ar.2')]//input[@type='checkbox' and @checked]        3
#
#    # trace metals has eight.
#
#    select from dropdown               css=#Profile-3              Trace
#    wait until page contains element   xpath=.//td[contains(@class, 'ar.3')]//input[@type='checkbox' and @checked]
#    xpath should match x times         .//td[contains(@class, 'ar.3')]//input[@type='checkbox' and @checked]        8
#
#### Dependencies
#
#    # selecting Dry Matter should require the 'Moisture' service
#
#    select checkbox                    css=tr[title='Dry Matter'] td[class*='ar.1'] input[type='checkbox']
#    page should contain                Do you want to apply these selections now
#    click element                      xpath=.//button[.//span[contains(text(), 'yes')]]
#    sleep                              .25
#    checkbox should be selected        css=tr[title='Moisture'] td[class*='ar.1'] input[type='checkbox']
#
#    # unselecting Moisture should remove the 'Dry Matter' service
#
#    unselect checkbox                  css=tr[title='Moisture'] td[class*='ar.1'] input[type='checkbox']
#    page should contain                Do you want to remove these selections now
#    click element                      xpath=.//button[.//span[contains(text(), 'yes')]]
#    sleep                              .25
#    checkbox should not be selected    css=tr[title='Dry Matter'] td[class*='ar.1'] input[type='checkbox']
#
#### Report as Dry Matter should select DryMatter and Moisture services
#
#    select checkbox                    css=#ReportDryMatter-4
#    checkbox should be selected        css=tr[title='Dry Matter'] td[class*='ar.4'] input[type='checkbox']
#    checkbox should be selected        css=tr[title='Moisture'] td[class*='ar.4'] input[type='checkbox']
#
#    log   BikaListing when Create Profile button is clicked     WARN
#    log   BikaListing when Sample is selected (secondary AR)     WARN
#    log   BikaListing when copy_from is specified in request     WARN
#
#### Submit and verify one with everything
#
#
#*** Keywords ***
#
#Prices in column ${col_nr} should be: ${discount} ${subtotal} ${vat} ${total}
#    element text should be      xpath=.//input[@id=ar_${col_nr}_discount]    ${discount}
#    element text should be      xpath=.//input[@id=ar_${col_nr}_subtotal]    ${subtotal}
#    element text should be      xpath=.//input[@id=ar_${col_nr}_vat]         ${vat}
#    element text should be      xpath=.//input[@id=ar_${col_nr}_total]       ${total}
#
#Disable Prices
#    go to                       ${PLONEURL}/bika_setup/edit
#    wait until page contains    Password lifetime
#    click link                  fieldsetlegend-accounting
#    unselect checkbox           css=#ShowPrices
#    click button                Save
#    wait until page contains    saved.

