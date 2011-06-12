"""bika mail templates

$Id: mailtemplates.py 2576 2010-11-09 19:40:48Z anneline $
"""
from bika.lims.config import PROJECTNAME

sms = {
    'title': 'sms',
    'description': 'Send an SMS through email gateway',
    'mail_subject': """string: password""",
    'mail_body': """Hi <tal:r replace="options/contact/getFullname"/>, """ +\
                 """results have been submitted for <tal:r replace="python:options['items']"/>. """+\
                 """Visit <tal:r replace="options/lab_url"/> to view them.""",
    }
    
ar_results_csv = {
    'title': 'Analysis results file export mail template',
    'description': 'AR mail template for file export.',
    'mail_subject': 'options/mail_subject',
    'mail_body':
"""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html tal:define="portal python:options['portal']">
<style>
body {
    font-family: Arial, "Lucida Grande", Verdana, Lucida, Helvetica, sans-serif;
    font-size: 10;
    background-color: White;
    color: Black;
    margin: 1em;
    padding: 0;
}

a {
    text-decoration: none;
    color: #436976;
    background-color: transparent;
}
img {
    border: none;
    vertical-align: middle;
}
p {
    margin: 0.5em 0em 1em 0em;
    line-height: 1.5em;
}
p a {
    text-decoration: underline;
}
p a:visited {
    color: Purple;
    background-color: transparent;
}
p a:active {
    color: Red;
    background-color: transparent;
}
p img {
    border: 0;
    margin: 0;
}

hr {
    height: 1px;
    color: #d3d3ad;
    background-color: transparent;
}

h1, h2, h3, h4, h5, h6 {
    color: Black;
    background-color: transparent;
    font-family: Arial, "Lucida Grande", Verdana, Lucida, Helvetica, sans-serif;
    font-size: 69%;
    font-weight: normal;
    margin: 0;
    padding-top: 0.5em;
    border-bottom: 1px solid #636321;
}

h1 a,
h2 a,
h3 a,
h4 a,
h5 a,
h6 a {
    color: Black ! important; 
}

h1 {
    font-size: 160%;
}

h2 {
    font-size: 150%;
}

h3 {
    font-size: 140%;
    border-bottom: none;
    font-weight: bold;
}

h4 {
    font-size: 120%;
    border-bottom: none;
    font-weight: bold;
}

h5 {
    font-size: 100%;
    border-bottom: none;
    font-weight: bold;
}

h6 {
    font-size: 85%;
    border-bottom: none;
    font-weight: bold;
}
.documentDescription {
    font-weight: bold;
    display: block;
    margin: 1em 0em;
    line-height: 1.5em;
}
.documentByLine {
    text-align: left;
    font-size: 85%;
    clear: both;
    font-weight: normal;
    color: #76797c;
}
.documentByLine a {
    text-decoration: underline;
}
.eventDetail {
    font-style: italic;
}

.logos {
    width: 50%
}

.analysisrequest {
    border-collapse: collapse;
    border-left: 1px solid #636321;
    border-bottom: 1px solid #636321;
    font-size: 85%;
    margin: 1em 0em 1em 0em;
}

.analysisrequest th {
    background: #d3d3ad;
    border-top: 1px solid #636321;
    border-right: 1px solid #636321;
    font-weight: normal;
    padding: 0em 1em 0em 1em;
    text-align: left;
}

.analysisrequest .top {
    border-left: 1px solid #636321;
    border-top: 1px solid #636321; ! important;
    border-right: 1px solid #636321; ! important;
    text-align: right ! important;
    padding: 0em 0em 1em 0em;
}
.analysisrequest .odd {
    /*every second line should be shaded */
    background-color: transparent;
}
.analysisrequest .even {
    background-color: #f7f9fa;
}
.analysisrequest .listingCheckbox {
    text-align: center;
}
.analysisrequest td.left {
    text-align: left;
}
.analysisrequest td.contact {
    text-align: left;
}
.analysisrequest td {
    border-right: 1px solid #636321;
    border-top: 1px solid #636321;
    border-bottom: 1px solid #636321;
    padding: 0em 0em;
    vertical-align: top;
    text-align: center;
}
.analysisrequest a:hover {
    text-decoration: underline;
}
.analysisrequest img {
    vertical-align: middle;
}

.analysisrequest .amount {
    text-align: right;
    padding-right: 1em;
}

.remarks {
    border-collapse: collapse;
    border-left: 1px solid #636321;
    border-bottom: 1px solid #636321;
    font-size: 85%;
    margin: 1em 0em 1em 0em;
}

.remarks th {
    background: #d3d3ad;
    border-top: 1px solid #636321;
    border-right: 1px solid #636321;
    font-weight: normal;
    padding: 0em 1em 0em 1em;
    text-align: left;
}
.remarks td {
    border-right: 1px solid #636321;
    border-top: 1px solid #636321;
    border-bottom: 1px solid #636321;
    padding: 0em 1em 0em 1em;
    vertical-align: top;
    text-align: left;
}
.remarks th.tabletitle {
    text-align: center;
}
.discreeter {
    color: &dtml-discreetColor;;
    font-size: 80%;;
    font-weight: normal;
}
</style>
<body>

<tal:block define="
        lab_accredited options/laboratory/LaboratoryAccredited;
        batch python:options['analysis_requests'];
        service_info python:portal.get_services_from_requests(batch);
        services service_info/Services;
        any_accredited service_info/Accredited;
        accredited python:lab_accredited and any_accredited"
    i18n:domain="bika">

<table class="logos">
<tr><td>
<img src="" tal:attributes="src string:${portal/absolute_url}/lab_logo.jpg">
</td>
<td tal:condition="accredited">
<img src="" tal:attributes="src string:${portal/absolute_url}/accreditation_logo.jpg">
</td></tr>
</table>

<span i18n:translate="message_results_attached">The analyses results are attached.</span>
<p>
<span i18n:translate="label_regards">Regards,</span>
<tal:labname replace="options/laboratory/Title"/>
<br>
<table
    tal:define="mngr_info python:here.get_managers_from_requests(batch);
                mngr_ids python:mngr_info['ids'];
                managers python:mngr_info['dict']">
<tr tal:repeat="manager mngr_ids">
<td>
<span 
    tal:condition="python:repeat['manager'].index == 0"
    i18n:translate="label_responsible">Manager:</span>
</td>
<td tal:content="python:managers[manager]['name']">Joe Blogs</td>
<td tal:define="phone python:managers[manager]['phone'];
                email python:managers[manager]['email']">
<img src="" 
    tal:condition="phone"
    tal:attributes="src string:${portal/absolute_url}/telephone.jpg">
<span tal:content="phone">011 555 1112</span>
<span tal:condition="phone">&nbsp&nbsp</span>
<img src="" 
    tal:condition="email"
    tal:attributes="src string:${portal/absolute_url}/email.jpg">
<a  tal:attributes="href string:mailto:${email}"
    tal:content="email">a@b.com</a>
</td>
</tr>
</table>

<hr/>

<div class="discreeter"
    tal:define="global seq_no python:0">

<p>
<span tal:define="global seq_no python:seq_no + 1"
    tal:content="string:$seq_no.">1</span>
<span i18n:translate="disclaimer_results_samples_tested">
Analysis results relate only to the samples tested</span></p>

<!--
<p>
<span tal:define="global seq_no python:seq_no + 1"
    tal:content="string:$seq_no.">1</span>
<span i18n:translate="disclaimer_dry_matter">
Values in brackets denote results on a 'Dry Matter' basis</span></p>
-->

<p>
<span tal:define="global seq_no python:seq_no + 1"
    tal:content="string:$seq_no.">1</span>
<span i18n:translate="disclaimer_no_reproduce">
This document shall not be reproduced except in full, without the written approval of <tal:block replace="options/laboratory/Title" i18n:name="name_lab"/></span></p>

<p tal:define="confidence_level options/laboratory/Confidence|nothing"
    tal:condition="confidence_level">
<span tal:define="global seq_no python:seq_no + 1"
    tal:content="string:$seq_no.">1</span>
<span i18n:translate="disclaimer_confidence_level">
Test results are at a <tal:block replace="confidence_level" i18n:name="lab_confidence"/>% confidence level</span></p>


</div>

<hr/>

</tal:block>
</body>
</html>

"""}

ar_results = {
    'title': 'Analysis results mail template',
    'description': 'Default AR mail template.',
    'mail_subject': 'options/mail_subject',
    'mail_body':
"""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html tal:define="portal python:options['portal']">
<style>
body {
    font-family: Arial, "Lucida Grande", Verdana, Lucida, Helvetica, sans-serif;
    font-size: 10;
    background-color: White;
    color: Black;
    margin: 1em;
    padding: 0;
}

a {
    text-decoration: none;
    color: #436976;
    background-color: transparent;
}
img {
    border: none;
    vertical-align: middle;
}
p {
    margin: 0.5em 0em 1em 0em;
    line-height: 1.5em;
}
p a {
    text-decoration: underline;
}
p a:visited {
    color: Purple;
    background-color: transparent;
}
p a:active {
    color: Red;
    background-color: transparent;
}
p img {
    border: 0;
    margin: 0;
}

hr {
    height: 1px;
    color: #d3d3ad;
    background-color: transparent;
}

h1, h2, h3, h4, h5, h6 {
    color: Black;
    background-color: transparent;
    font-family: Arial, "Lucida Grande", Verdana, Lucida, Helvetica, sans-serif;
    font-size: 69%;
    font-weight: normal;
    margin: 0;
    padding-top: 0.5em;
    border-bottom: 1px solid #636321;
}

h1 a,
h2 a,
h3 a,
h4 a,
h5 a,
h6 a {
    color: Black ! important; 
}

h1 {
    font-size: 160%;
}

h2 {
    font-size: 150%;
}

h3 {
    font-size: 140%;
    border-bottom: none;
    font-weight: bold;
}

h4 {
    font-size: 120%;
    border-bottom: none;
    font-weight: bold;
}

h5 {
    font-size: 100%;
    border-bottom: none;
    font-weight: bold;
}

h6 {
    font-size: 85%;
    border-bottom: none;
    font-weight: bold;
}
.documentDescription {
    font-weight: bold;
    display: block;
    margin: 1em 0em;
    line-height: 1.5em;
}
.documentByLine {
    text-align: left;
    font-size: 85%;
    clear: both;
    font-weight: normal;
    color: #76797c;
}
.documentByLine a {
    text-decoration: underline;
}
.eventDetail {
    font-style: italic;
}

.logos {
    width: 50%
}
.legend {
    border-collapse: collapse;
    border-left: &dtml-borderWidth; &dtml-borderStyle; &dtml-globalBorderColor;;
    border-bottom: &dtml-borderWidth; &dtml-borderStyle; &dtml-globalBorderColor;;
    font-size: &dtml-fontSmallSize;;
    margin: 1em 0em 1em 0em;
}
.legend td {
    border-right: &dtml-borderWidth; &dtml-borderStyle; &dtml-globalBorderColor;;
    border-top: &dtml-borderWidth; &dtml-borderStyle; &dtml-globalBorderColor;;
    border-bottom: &dtml-borderWidth; &dtml-borderStyle; &dtml-globalBorderColor;;
    padding: 1em 0em 1em 0em;
    text-align: center;
}

.analysisrequest {
    border-collapse: collapse;
    border-left: 1px solid #636321;
    border-bottom: 1px solid #636321;
    font-size: 85%;
    margin: 1em 0em 1em 0em;
}

.analysisrequest th {
    background: #d3d3ad;
    border-top: 1px solid #636321;
    border-right: 1px solid #636321;
    border-bottom: 1px solid #636321;
    font-weight: normal;
    padding: 0em 1em 0em 1em;
    text-align: left;
}

.analysisrequest .top {
    border-left: 1px solid #636321;
    border-top: 1px solid #636321; ! important;
    border-right: 1px solid #636321; ! important;
    text-align: right ! important;
    padding: 0em 0em 1em 0em;
}
.analysisrequest .odd {
    /*every second line should be shaded */
    background-color: transparent;
}
.analysisrequest .even {
    background-color: #f7f9fa;
}
.analysisrequest .dryhead {
    background-color: #a6b5db;
}
.analysisrequest .drybody {
    background-color: #dae0f0;
}
.analysisrequest .listingCheckbox {
    text-align: center;
}
.analysisrequest td.left {
    text-align: left;
}
.analysisrequest td.contact {
    text-align: left;
}
.analysisrequest td {
    border-right: 1px solid #636321;
    border-top: 1px solid #636321;
    border-bottom: 1px solid #636321;
    padding: 0em 0em;
    vertical-align: top;
    text-align: center;
}
.analysisrequest a:hover {
    text-decoration: underline;
}
.analysisrequest img {
    vertical-align: middle;
}

.analysisrequest .amount {
    text-align: right;
    padding-right: 1em;
}

.remarks {
    border-collapse: collapse;
    border-left: 1px solid #636321;
    border-bottom: 1px solid #636321;
    font-size: 85%;
    margin: 1em 0em 1em 0em;
}

.remarks th {
    background: #d3d3ad;
    border-top: 1px solid #636321;
    border-right: 1px solid #636321;
    font-weight: normal;
    padding: 0em 1em 0em 1em;
    text-align: left;
}
.remarks td {
    border-right: 1px solid #636321;
    border-top: 1px solid #636321;
    border-bottom: 1px solid #636321;
    padding: 0em 1em 0em 1em;
    vertical-align: top;
    text-align: left;
}
.remarks th.tabletitle {
    text-align: center;
}
.category  {
    text-align: left ! important;
    background: #B6C0D1;;
}
.out_of_range {
    color: red;;
}
.retested {
    color: red;;
    font-size: 80%;;
    font-weight: normal;
}
.discreeter {
    color: &dtml-discreetColor;;
    font-size: 80%;;
    font-weight: normal;
}
.address {
    width: 100%
}
.address td {
    width: 50%;
    vertical-align: top;
    font-size: 80%;
}
</style>
<body>

<tal:block define="
        plone_view python:context.restrictedTraverse('@@plone');
        laboratory python:options['laboratory'];
        lab_address python:laboratory.getPostalAddress();
        lab_address python:lab_address and lab_address or laboratory.getBillingAddress();
        lab_address python:lab_address and lab_address or laboratory.getPhysicalAddress();
        lab_accredited python:laboratory.getLaboratoryAccredited();
        lab_url python:options['lab_url'];
        batch python:options['analysis_requests'];
        global columns python:0;
        output_type options/output;
        service_info python:portal.get_services_from_requests(batch);
        services service_info/Services;
        any_accredited service_info/Accredited;
        global dry_matter service_info/DryMatter;
        accredited python:lab_accredited and any_accredited;
        global invoice_exclude python:False;
        global out_of_range python:0;
        contact python:options['contact'] or None"
    i18n:domain="bika">

<table class="logos">
<tr><td>
<img src="" tal:attributes="src string:${lab_url}/logo_print.jpg">
</td>
<td tal:condition="accredited">
<img src="" tal:attributes="src string:${lab_url}/accreditation_print.jpg">
</td></tr>
</table>

<table class="address">
<tr>
<td tal:condition="contact">
<tal:x  tal:define="
        client python:contact.aq_parent;
        contact_address python:contact.getPostalAddress();
        contact_address python:contact_address and contact_address or contact.getBillingAddress();
        contact_address python:contact_address and contact_address or client.getPostalAddress();
        contact_address python:contact_address and contact_address or client.getBillingAddress();
        contact_address python:contact_address and contact_address or contact.getPhysicalAddress();
        contact_address python:contact_address and contact_address or client.getPhysicalAddress()">
<div tal:content="contact/getFullname"></div>
<div tal:content="client/Title"></div>
<div tal:define="address python:contact_address.get('address','')"
    tal:content="structure python:modules['Products.PythonScripts.standard'].newline_to_br(address)"> </div>
<div>
<span tal:content="python:contact_address.get('city','')"></span>,
<span tal:content="python:contact_address.get('state','')"></span>,
<span tal:content="python:contact_address.get('zip','')"></span>
<span tal:content="python:contact_address.get('country','')"></span>
</div>
</tal:x>
</td>

<td tal:condition="python:not contact">&nbsp;</td>

<td>
<div tal:content="laboratory/Title"></div>
<div tal:define="address python:lab_address.get('address','')"
    tal:content="structure python:modules['Products.PythonScripts.standard'].newline_to_br(address)"> </div>
<div>
<span tal:content="python:lab_address.get('city','')"></span>,
<span tal:content="python:lab_address.get('state','')"></span>,
<span tal:content="python:lab_address.get('zip','')"></span>
<span tal:content="python:lab_address.get('country','')"></span>
</div>
</td>
</tr>
</table>

<table class="remarks">
<th class="tabletitle"
    colspan="2"
    i18n:translate="label_attachments">Attachments</th>
<tal:ar tal:repeat="ar batch">
<tr tal:define="attachments ar/getAttachment"
    tal:condition="attachments">

<th tal:content="string:${ar/getRequestID}:">AR:</th>
<td>
<tal:attachment tal:repeat="attachment attachments">
<div
    tal:define="file python:attachment.getAttachmentFile();
                filename file/filename | nothing;
                filesize file/get_size | python:file and len(file) or 0;
                icon file/getBestIcon | nothing">
<img tal:condition="icon" src=""
    tal:attributes="src string:${here/portal_url}/$icon"/>
<a href=""  title="Click to download"
    tal:attributes="href string:${attachment/absolute_url}/at_download/AttachmentFile"
    tal:content=filename>Filename</a>
<span class="discreet" tal:content="python:attachment.getAttachmentType().Title()">Filename</span>
<span class="discreet" tal:content="python:here.lookupMime(file.getContentType())">ContentType</span> &mdash;
<span class="discreet" tal:content="python:'%sKb' % (filesize / 1024)">0Kb</span>
</div>
</tal:attachment>
</td>
</tr>
<tal:analyses tal:repeat="analysis ar/getAnalyses">
<tal:attachments tal:define="attachments analysis/getAttachment">
<tal:attachment tal:repeat="attachment attachments">
<tr>

<th tal:content="string:${ar/getRequestID} - ${analysis/Title}:">AR:</th>
<td>
<div
    tal:define="file python:attachment.getAttachmentFile();
                filename file/filename | nothing;
                filesize file/get_size | python:file and len(file) or 0;
                icon file/getBestIcon | nothing">
<img tal:condition="icon" src=""
    tal:attributes="src string:${here/portal_url}/$icon"/>
<a href=""  title="Click to download"
    tal:attributes="href string:${attachment/absolute_url}/at_download/AttachmentFile"
    tal:content=filename>Filename</a>
<span class="discreet" tal:content="python:attachment.getAttachmentType().Title()">Filename</span>
<span class="discreet" tal:content="python:here.lookupMime(file.getContentType())">ContentType</span> &mdash;
<span class="discreet" tal:content="python:'%sKb' % (filesize / 1024)">0Kb</span>
</div>
</td></tr>
</tal:attachment>
</tal:attachments>
</tal:analyses>
</tal:ar>
</table>

<table
    class="analysisrequest"
    summary="analysis request listing"
    cellpadding="2" cellspacing="0">

<thead>
<tr>
<th i18n:translate="label_client_order_id" i18n:domain="bika">Client Order ID</th>
<td tal:repeat="ar batch"
    tal:attributes="colspan python:ar.getReportDryMatter() and 2 or 1"
    tal:content="ar/getClientOrderNumber">123</td>
</tr>

<tr>
<th i18n:translate="label_clientreference" i18n:domain="bika">Client Reference</th>
<td tal:repeat="ar batch"
    tal:attributes="colspan python:ar.getReportDryMatter() and 2 or 1"
    tal:content="python:ar.getSample().getClientReference()">T01</td>
</tr>

<tr>
<th i18n:translate="label_clientsampleid" i18n:domain="bika">Client Sample ID</th>
<td tal:repeat="ar batch"
    tal:attributes="colspan python:ar.getReportDryMatter() and 2 or 1"
    tal:content="python:ar.getSample().getClientSampleID()">S01</td>
</tr>

<tr>
<th i18n:translate="label_requestid" i18n:domain="bika">Request ID</th>
<td tal:repeat="ar batch" 
    tal:attributes="colspan python:ar.getReportDryMatter() and 2 or 1">
<a href="" tal:content="ar/getRequestID"
    tal:attributes="href ar/absolute_url">AR-00001</a>
<tal:exclude tal:condition="ar/getInvoiceExclude">
<img src="" 
    tal:define="global invoice_exclude python:1"
    tal:attributes="src string:${lab_url}/no_invoice.jpg">
</tal:exclude>
<tal:dry tal:condition="ar/getReportDryMatter">
<img src="" 
    tal:define="global dry_matter python:1"
    tal:attributes="src string:${lab_url}/dry.jpg">
</tal:dry>
</td>
</tr>

<tr>
<th i18n:translate="label_sampleid" i18n:domain="bika">Sample ID</th>
<td tal:repeat="ar batch"
    tal:attributes="colspan python:ar.getReportDryMatter() and 2 or 1">
<a href="" 
    tal:define="sample ar/getSample"
    tal:content="sample/getSampleID"
    tal:attributes="href sample/absolute_url">S-00001</a>
</td>
</tr>

<tr>
<th i18n:translate="label_client" i18n:domain="bika">Client</th>
<td tal:repeat="ar batch"
    tal:attributes="colspan python:ar.getReportDryMatter() and 2 or 1"
    tal:content="ar/aq_parent/Title">Lab client</td>
</tr>

<tr>
<th i18n:translate="label_sampletype" i18n:domain="bika">Sample Type</th>
<td tal:repeat="ar batch"
    tal:attributes="colspan python:ar.getReportDryMatter() and 2 or 1"
    tal:content="python:ar.getSample().getSampleType().Title()">SampleType</td>
</tr>

<tr>
<th i18n:translate="label_samplepoint" i18n:domain="bika">Sample Point</th>
<td tal:repeat="ar batch"
    tal:attributes="colspan python:ar.getReportDryMatter() and 2 or 1">
<span
    tal:define="samplepoint python:ar.getSample().getSamplePoint()"
    tal:content="samplepoint/Title|nothing">SamplePoint</span></td>
</tr>




<tr>
<th i18n:translate="label_datereceived">Date received
</th>
<td tal:repeat="ar batch"
    tal:attributes="colspan python:ar.getReportDryMatter() and 2 or 1"
    tal:content="python:plone_view.toLocalizedTime(ar.getDateReceived(), long_format=1)"
    >2005-01-01 10:00</td>
</tr>

<tr>
<th i18n:translate="label_datepublished">Date published
</th>
<td tal:repeat="ar batch"
    tal:attributes="colspan python:ar.getReportDryMatter() and 2 or 1"
    tal:content="python:plone_view.toLocalizedTime(ar.getDatePublished(), long_format=1)"
    >2005-01-01 10:00</td>
</tr>


<tr>
<th i18n:translate="label_verified_by">Verified by </th>
<td tal:repeat="ar batch"
    tal:attributes="colspan python:ar.getReportDryMatter() and 2 or 1">
<span
    tal:define="verifier python:here.get_analysisrequest_verifier(ar)"
    tal:content="verifier">
</span>
</td>
</tr>

<tr>
<th>
<b i18n:translate="label_analysis_results" i18n:domain="bika">
Analysis results</b>
</th>
<tal:results tal:repeat="ar batch">
<tal:drymatter tal:condition="ar/getReportDryMatter">
<th><b i18n:translate="label_as_fed">As Fed</b></th>
<th class="dryhead"><b i18n:translate="label_dry">Dry</b></th>
</tal:drymatter>
<tal:notdrymatter tal:condition="not:ar/getReportDryMatter">
<th></th>
</tal:notdrymatter>
</tal:results>
</tr>

</thead>

<tbody>
<tal:arcount 
    tal:repeat="ar batch">
<tal:ar 
    tal:define="global columns python:ar.getReportDryMatter() and columns + 2 or columns + 1">
</tal:ar>
</tal:arcount>
<tal:service
    tal:define="global category python:None"
    tal:repeat="service services">
<tr tal:condition="python:service.getCategoryName() != category">
<td class="category" 
        tal:attributes="colspan python:columns + 1"
    tal:define="global category service/getCategoryName"
    tal:content="service/getCategoryName"></td>
</tr>
<tr tal:define="service_unit service/getUnit|nothing">

<th nowrap> 
<span tal:content="service/Title">Alcohol</span>
<em tal:content="service_unit">ml</em>
<img src="" 
    tal:condition="python:dry_matter and service.getReportDryMatter()"
    tal:attributes="src string:${lab_url}/dry_grey.jpg">
<img src="" 
    tal:condition="python:accredited and service.getAccredited()"
    tal:attributes="src string:${lab_url}/accredited_grey.jpg">
</th>

<tal:ars repeat="ar batch">
<div tal:define="
            service_id service/getId;
            analyses python:portal.group_analyses_by_service(ar.getPublishedAnalyses());
            analysis python:analyses.get(service_id, None);
            analysis_found python:analyses.has_key(service_id);
            result analysis/getResult|nothing;
            mou analysis/getUncertainty|nothing">
<tal:result
    tal:condition="analysis_found"
    tal:define="
        sampletype python:ar.getSample().getSampleType();
        sampletype_uid sampletype/UID;
        client_uid ar/aq_parent/UID;
        result_class python:analysis_found and portal.result_in_range(analysis, sampletype_uid, 'client') or '';
        global out_of_range python:result_class == 'out_of_range' and 1 or out_of_range">
<td nowrap align="center"
    tal:attributes="class result_class">
<span tal:content="result">10.00</span>
<img tal:condition="python:result_class == 'out_of_range'"
    src="" tal:attributes="src string:${lab_url}/exclamation.jpg">
<span tal:content="string:(${analysis/getUnit})"
      tal:condition="python:analysis.getUnit() != service_unit"/>
<span tal:content="string:[+/- $mou]"
      tal:condition="mou"/>
<div class="retested"
      tal:condition="analysis/getRetested"
      i18n:translate="retested">retested</div>
</td>
<td class="drybody" tal:condition="ar/getReportDryMatter">
<span tal:condition="analysis/getResultDM"
    tal:content="analysis/getResultDM">10</span>
</td>
</tal:result>
<tal:notanalysis tal:condition="python:not analysis_found">
<td></td>
<td class="drybody" tal:condition="ar/getReportDryMatter"></td>
</tal:notanalysis>
</div>
</tal:ars>
</tr>
</tal:service>

</tbody>

</table>

<table class="remarks">
<th class="tabletitle"
    colspan="2"
    i18n:translate="label_remarks">Remarks</th>
<tr tal:repeat="ar batch">
<th tal:content="string:${ar/getRequestID}:">AR:</th>
<td width=50%
    tal:content="python:ar.getNotes() or default">None</td>
</tr>
</table>


<div tal:repeat="manager mngr_ids"
    tal:define="mngr_info python:here.get_managers_from_requests(batch);
                mngr_ids python:mngr_info['ids'];
                managers python:mngr_info['dict']">
<tal:mngr
    tal:define="email python:managers[manager]['email'];
                phone python:managers[manager]['phone']">

<img src="" 
    tal:condition="signature"
    tal:define="signature python:managers[manager]['signature']"
    tal:attributes="src string:${signature}">
<br>
<span tal:content="python:managers[manager]['name']">Joe Blogs</span>
<span tal:condition="phone">&nbsp&nbsp</span>
<img src="" 
    tal:condition="phone"
    tal:attributes="src string:${portal/absolute_url}/telephone.jpg">
<span tal:content="phone">011 555 1112</span>
<span tal:condition="email">&nbsp&nbsp</span>
<img src="" 
    tal:condition="email"
    tal:attributes="src string:${portal/absolute_url}/email.jpg">
<a  tal:attributes="href string:mailto:${email}"
    tal:content="email">a@b.com</a>
</tal:mngr>
</div>

<hr/>

<div class="discreeter"
    tal:define="global seq_no python:0">
<p tal:condition="out_of_range">
<img src="" tal:attributes="src string:${lab_url}/exclamation.jpg">
<span i18n:translate="legend_out_of_rangex">
Result out of <tal:block replace="string:client" i18n:name="spec"/> specified range
</span>
</p>

<p tal:condition="dry_matter">
<img src="" tal:attributes="src string:${lab_url}/dry.jpg">
<span i18n:translate="disclaimer_dry">
Reported as dry matter</span>
</p>

<p tal:condition="invoice_exclude">
<img src="" tal:attributes="src string:${lab_url}/no_invoice.jpg">
<span i18n:translate="disclaimer_invoice_exclude">
Not invoiced</span>
</p>

<p tal:condition="lab_accredited">
<img src="" tal:attributes="src string:${lab_url}/accredited.jpg">
<span i18n:translate="disclaimer_accred">
Methods included in the <tal:block replace="options/laboratory/AccreditationBody" i18n:name="accreditation_body"/> schedule of Accreditation for this Laboratory. Analysis remarks are not accredited</span>
</p>

<p>
<span tal:define="global seq_no python:seq_no + 1"
    tal:content="string:$seq_no.">1</span>
<span i18n:translate="disclaimer_results_samples_tested">
Analysis results relate only to the samples tested</span></p>

<p>
<span tal:define="global seq_no python:seq_no + 1"
    tal:content="string:$seq_no.">1</span>
<span i18n:translate="disclaimer_no_reproduce">
This document shall not be reproduced except in full, without the written approval of <tal:block replace="options/laboratory/Title" i18n:name="name_lab"/></span></p>

<p tal:define="confidence_level options/laboratory/Confidence|nothing"
    tal:condition="confidence_level">
<span tal:define="global seq_no python:seq_no + 1"
    tal:content="string:$seq_no.">1</span>
<span i18n:translate="disclaimer_confidence_level">
Test results are at a <tal:block replace="confidence_level" i18n:name="lab_confidence"/>% confidence level</span></p>

<p tal:condition="python:output_type == 'email'">
<span tal:define="global seq_no python:seq_no + 1"
    tal:content="string:$seq_no.">1</span>
<span i18n:translate="label_methods_online">
Methods of analysis available by clicking on the 'Request' link</span></p>

</div>

<hr/>
</tal:block>
</body>
</html>



"""}

ar_query_results = {
    'title': 'Analysis query results mail template',
    'description': 'Query result mail template.',
    'mail_subject': 'string:Results for query on analysis requests',
    'mail_body':
"""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html tal:define="portal python:options['portal']">
<style>
body {
    font-family: Arial, "Lucida Grande", Verdana, Lucida, Helvetica, sans-serif;
    font-size: 10;
    background-color: White;
    color: Black;
    margin: 1em;
    padding: 0;
}

a {
    text-decoration: none;
    color: #436976;
    background-color: transparent;
}
img {
    border: none;
    vertical-align: middle;
}
p {
    margin: 0.5em 0em 1em 0em;
    line-height: 1.5em;
}
p a {
    text-decoration: underline;
}
p a:visited {
    color: Purple;
    background-color: transparent;
}
p a:active {
    color: Red;
    background-color: transparent;
}
p img {
    border: 0;
    margin: 0;
}

hr {
    height: 1px;
    color: #d3d3ad;
    background-color: transparent;
}

h1, h2, h3, h4, h5, h6 {
    color: Black;
    background-color: transparent;
    font-family: Arial, "Lucida Grande", Verdana, Lucida, Helvetica, sans-serif;
    font-size: 69%;
    font-weight: normal;
    margin: 0;
    padding-top: 0.5em;
    border-bottom: 1px solid #636321;
}

h1 a,
h2 a,
h3 a,
h4 a,
h5 a,
h6 a {
    color: Black ! important; 
}

h1 {
    font-size: 160%;
}

h2 {
    font-size: 150%;
}

h3 {
    font-size: 140%;
    border-bottom: none;
    font-weight: bold;
}

h4 {
    font-size: 120%;
    border-bottom: none;
    font-weight: bold;
}

h5 {
    font-size: 100%;
    border-bottom: none;
    font-weight: bold;
}

h6 {
    font-size: 85%;
    border-bottom: none;
    font-weight: bold;
}
.documentDescription {
    font-weight: bold;
    display: block;
    margin: 1em 0em;
    line-height: 1.5em;
}
.documentByLine {
    text-align: left;
    font-size: 85%;
    clear: both;
    font-weight: normal;
    color: #76797c;
}
.documentByLine a {
    text-decoration: underline;
}
.eventDetail {
    font-style: italic;
}

.logos {
    width: 50%
}

.analysisrequest {
    border-collapse: collapse;
    border-left: 1px solid #636321;
    border-bottom: 1px solid #636321;
    font-size: 85%;
    margin: 1em 0em 1em 0em;
}

.analysisrequest th {
    background: #d3d3ad;
    border-top: 1px solid #636321;
    border-right: 1px solid #636321;
    font-weight: normal;
    padding: 0em 1em 0em 1em;
    text-align: left;
}

.analysisrequest .top {
    border-left: 1px solid #636321;
    border-top: 1px solid #636321; ! important;
    border-right: 1px solid #636321; ! important;
    text-align: right ! important;
    padding: 0em 0em 1em 0em;
}
.analysisrequest .odd {
    /*every second line should be shaded */
    background-color: transparent;
}
.analysisrequest .even {
    background-color: #f7f9fa;
}
.analysisrequest .listingCheckbox {
    text-align: center;
}
.analysisrequest td.left {
    text-align: left;
}
.analysisrequest td.contact {
    text-align: left;
}
.analysisrequest td {
    border-right: 1px solid #636321;
    border-top: 1px solid #636321;
    border-bottom: 1px solid #636321;
    padding: 0em 0em;
    vertical-align: top;
    text-align: center;
}
.analysisrequest a:hover {
    text-decoration: underline;
}
.analysisrequest img {
    vertical-align: middle;
}

.analysisrequest .amount {
    text-align: right;
    padding-right: 1em;
}

.analysisrequest th.tabletitle {
    text-align: center;
}

.analysisrequest .discreet {
    color: gray;;
    font-size: 69%;;
    font-weight: normal;
}
.analysisrequest .dryhead {
    background-color: #a6b5db;
}
.analysisrequest .drybody {
    background-color: #dae0f0;
}
.analysismethod {
    border-collapse: collapse;
    border-top: 1px solid #636321;
    border-right: 1px solid #636321;
    border-left: 1px solid #636321;
    border-bottom: 1px solid #636321;
    font-size: 85%;
    text-align: left;
    margin: 1em 0em 1em 0em;
    padding: 0em 1em 0em 1em;
}

.analysismethod th {
    border-top: 1px solid #636321;
    border-right: 1px solid #636321;
    background: #d3d3ad;
    text-align: left;
    font-weight: normal;
    margin: 1em 0em 1em 0em;
}

.analysismethod td {
    border-right: 1px solid #636321;
    border-top: 1px solid #636321;
    border-bottom: 1px solid #636321;
    margin: 1em 0em 1em 0em;
}
.analysismethod th.tabletitle {
    text-align: center;
}
.category  {
    text-align: left ! important;
    background: #B6C0D1;;
}
.remarks {
    border-collapse: collapse;
    border-left: 1px solid #636321;
    border-bottom: 1px solid #636321;
    font-size: 85%;
    margin: 1em 0em 1em 0em;
}

.remarks th {
    background: #d3d3ad;
    border-top: 1px solid #636321;
    border-right: 1px solid #636321;
    font-weight: normal;
    padding: 0em 1em 0em 1em;
    text-align: left;
}
.remarks td {
    border-right: 1px solid #636321;
    border-top: 1px solid #636321;
    border-bottom: 1px solid #636321;
    padding: 0em 1em 0em 1em;
    vertical-align: top;
    text-align: left;
}
.remarks th.tabletitle {
    text-align: center;
}
.discreet {
    color: gray;;
    font-size: 69%;;
    font-weight: normal;
}
.out_of_range {
    color: red;;
}
.retested {
    color: red;;
    font-size: 80%;;
    font-weight: normal;
}
.discreeter {
    color: &dtml-discreetColor;;
    font-size: 80%;;
    font-weight: normal;
}
.address {
    width: 100%
}
.address td {
    width: 50%;
    vertical-align: top;
    font-size: 80%;
}
</style>
<body>

<!-- actual list of objects, either searchresults or folder contents -->
<tal:block
    tal:define="
        plone_view python:context.restrictedTraverse('@@plone');
        laboratory python:options['laboratory'];
        lab_address python:laboratory.getPostalAddress();
        lab_address python:lab_address and lab_address or laboratory.getBillingAddress();
        lab_address python:lab_address and lab_address or laboratory.getPhysicalAddress();
        contact python:options['contact'];

        lab_accredited python:laboratory.getLaboratoryAccredited();
        here python:options['portal'];
        request python:options['request'];
        results python:options['results'];
        ar_batch python:[b.getObject() for b in results];
        service_info python:here.get_services_from_query_result(ar_batch);
        services service_info/Services;
        any_accredited service_info/Accredited;
        accredited python:lab_accredited and any_accredited;
        global tf python:0;
        global nr python:0;
        global out_of_range python:0;
        global dry_matter python:0;
        global invoice_exclude python:0;
        global columns python:0;
        is_client here/member_is_client;
        default_spec python:test(is_client, 'client', 'lab');  
        specification request/specification | default_spec;

        query_client python:request.query_client and context.reference_catalog.lookupObject(request.query_client) or None;
        query_contact python:request.query_contact and context.reference_catalog.lookupObject(request.query_contact) or None;
        address_contact python:contact and contact or query_contact"
    i18n:domain="bika">

<table class="logos">
<tr><td>
<img src="" tal:attributes="src string:${portal/absolute_url}/lab_logo.jpg">
</td>
<td tal:condition="accredited">
<img src="" tal:attributes="src string:${portal/absolute_url}/accreditation_logo.jpg">
</td></tr>
</table>

<table class="address">
<tr>
<td tal:condition="address_contact">
<tal:x  tal:define="
        client python:address_contact.aq_parent;
        contact_address python:address_contact.getPostalAddress();
        contact_address python:contact_address and contact_address or address_contact.getBillingAddress();
        contact_address python:contact_address and contact_address or client.getPostalAddress();
        contact_address python:contact_address and contact_address or client.getBillingAddress();
        contact_address python:contact_address and contact_address or address_contact.getPhysicalAddress();
        contact_address python:contact_address and contact_address or client.getPhysicalAddress()">
<div tal:content="address_contact/getFullname"></div>
<div tal:content="client/Title"></div>
<div tal:define="address python:contact_address.get('address','')"
    tal:content="structure python:modules['Products.PythonScripts.standard'].newline_to_br(address)"> </div>
<div tal:content="python:'%s, %s, %s, %s' %(contact_address.get('city',''), contact_address.get('state',''), contact_address.get('zip',''), contact_address.get('country',''))"></div>
</tal:x>
</td>

<td tal:condition="python:(not address_contact) and query_client">
<tal:y  tal:define="
        client_address python:query_client.getPostalAddress();
        client_address python:client_address and client_address or query_client.getBillingAddress();
        client_address python:client_address and client_address or query_client.getPhysicalAddress()">
<div tal:content="query_client/Title"></div>
<div tal:define="address python:client_address.get('address','')"
    tal:content="structure python:modules['Products.PythonScripts.standard'].newline_to_br(address)"> </div>
<div tal:content="python:'%s, %s, %s, %s' %(client_address.get('city',''), client_address.get('state',''), client_address.get('zip',''), client_address.get('country',''))"></div>
</tal:y>
</td>

<td tal:condition="python:(not address_contact) and (not query_client)">&nbsp;</td>

<td>
<div tal:content="laboratory/Title"></div>
<div tal:define="address python:lab_address.get('address','')"
    tal:content="structure python:modules['Products.PythonScripts.standard'].newline_to_br(address)"> </div>
<div tal:content="python:'%s, %s, %s, %s' %(lab_address.get('city',''), lab_address.get('state',''), lab_address.get('zip',''), lab_address.get('country',''))"></div>
</td>
</tr>
</table>

<table class="remarks">
<th class="tabletitle"
    colspan="2"
    i18n:translate="label_attachments">Attachments</th>
<tal:ar tal:repeat="ar ar_batch">
<tr tal:define="attachments ar/getAttachment"
    tal:condition="attachments">

<th tal:content="string:${ar/getRequestID}:">AR:</th>
<td>
<tal:attachment tal:repeat="attachment attachments">
<div
    tal:define="file python:attachment.getAttachmentFile();
                filename file/filename | nothing;
                filesize file/get_size | python:file and len(file) or 0;
                icon file/getBestIcon | nothing">
<img tal:condition="icon" src=""
    tal:attributes="src string:${here/portal_url}/$icon"/>
<a href=""  title="Click to download"
    tal:attributes="href string:${attachment/absolute_url}/at_download/AttachmentFile"
    tal:content=filename>Filename</a>
<span class="discreet" tal:content="python:attachment.getAttachmentType().Title()">Filename</span>
<span class="discreet" tal:content="python:here.lookupMime(file.getContentType())">ContentType</span> &mdash;
<span class="discreet" tal:content="python:'%sKb' % (filesize / 1024)">0Kb</span>
</div>
</tal:attachment>
</td>
</tr>
<tal:analyses tal:repeat="analysis ar/getAnalyses">
<tal:attachments tal:define="attachments analysis/getAttachment">
<tal:attachment tal:repeat="attachment attachments">
<tr>

<th tal:content="string:${ar/getRequestID} - ${analysis/Title}:">AR:</th>
<td>
<div
    tal:define="file python:attachment.getAttachmentFile();
                filename file/filename | nothing;
                filesize file/get_size | python:file and len(file) or 0;
                icon file/getBestIcon | nothing">
<img tal:condition="icon" src=""
    tal:attributes="src string:${here/portal_url}/$icon"/>
<a href=""  title="Click to download"
    tal:attributes="href string:${attachment/absolute_url}/at_download/AttachmentFile"
    tal:content=filename>Filename</a>
<span class="discreet" tal:content="python:attachment.getAttachmentType().Title()">Filename</span>
<span class="discreet" tal:content="python:here.lookupMime(file.getContentType())">ContentType</span> &mdash;
<span class="discreet" tal:content="python:'%sKb' % (filesize / 1024)">0Kb</span>
</div>
</td></tr>
</tal:attachment>
</tal:attachments>
</tal:analyses>
</tal:ar>
</table>

<table
    class="analysisrequest"
    summary="analysis request listing"
    cellpadding="2" cellspacing="0"
    tal:condition="ar_batch"
    i18n:domain="bika">

<thead>
<tr>
<th i18n:translate="label_client_order_id">Client Order ID</th>
<td tal:repeat="ar ar_batch"
    tal:attributes="colspan python:ar.getReportDryMatter() and 2 or 1"
    tal:content="python:ar.getClientOrderNumber()">123</td>
</tr>

<tr>
<th i18n:translate="label_clientreference">Client Reference</th>
<td tal:repeat="ar ar_batch"
    tal:attributes="colspan python:ar.getReportDryMatter() and 2 or 1"
    tal:content="python:ar.getSample().getClientReference()">T01</td>
</tr>

<tr>
<th i18n:translate="label_clientsampleid">Client Sample ID</th>
<td tal:repeat="ar ar_batch"
    tal:attributes="colspan python:ar.getReportDryMatter() and 2 or 1"
    tal:content="python:ar.getSample().getClientSampleID()">S01</td>
</tr>
<tr>
<th i18n:translate="label_requestid">Request ID</th>
<td tal:repeat="ar ar_batch" 
    tal:attributes="colspan python:ar.getReportDryMatter() and 2 or 1">
<a href="" tal:content="ar/getRequestID"
    tal:attributes="href ar/absolute_url">AR-00001</a>
<tal:exclude tal:condition="ar/getInvoiceExclude">
<img src="" 
    tal:define="global invoice_exclude python:1"

    tal:attributes="src string:${portal/absolute_url}/no_invoice.jpg">
</tal:exclude>
<tal:dry tal:condition="ar/getReportDryMatter">
<img src="" 
    tal:define="global dry_matter python:1"
    tal:attributes="src string:${portal/absolute_url}/dry.jpg">
</tal:dry>
</td>
</tr>

<tr>
<th i18n:translate="label_sampleid">Sample ID</th>
<td tal:repeat="ar ar_batch" 
    tal:attributes="colspan python:ar.getReportDryMatter() and 2 or 1">
<a href="" tal:content="python:ar.getSample().getSampleID()"
    tal:attributes="href python:ar.getSample().absolute_url()">S-00001</a>
</td>
</tr>

<tr>
<th i18n:translate="label_client">Client</th>
<td tal:repeat="ar ar_batch"
    tal:attributes="colspan python:ar.getReportDryMatter() and 2 or 1"
    tal:content="python:ar.aq_parent.Title()">Lab client</td>
</tr>

<tr>
<th i18n:translate="label_contact">Contact</th>
<td tal:repeat="ar ar_batch"
    tal:attributes="colspan python:ar.getReportDryMatter() and 2 or 1"
    tal:content="python:ar.getContact().Title()">Fred</td>
</tr>

<tr>
<th i18n:translate="label_arprofiles">Profile</th>
<td tal:repeat="ar ar_batch"
    tal:attributes="colspan python:ar.getReportDryMatter() and 2 or 1">
    <span
    tal:define="profile python:ar.getProfile() and ar.getProfile().getProfileTitle() or ''"
    tal:content="profile">pr01</span>
</td>
</tr>

<tr>
<th i18n:translate="label_sampletype">Sample Type</th>
<td tal:repeat="ar ar_batch"
    tal:attributes="colspan python:ar.getReportDryMatter() and 2 or 1"
    tal:content="python:ar.getSample().getSampleType().Title()">SampleType</td>
</tr>

<tr>
<th i18n:translate="label_samplepoint">Sample Point</th>
<td tal:repeat="ar ar_batch"
    tal:attributes="colspan python:ar.getReportDryMatter() and 2 or 1">
<span
    tal:define="samplepoint python:ar.getSample().getSamplePoint()"
    tal:content="samplepoint/Title|nothing">SamplePoint</span></td>
</tr>


<tr>
<th i18n:translate="label_datesampled">Date sampled
</th>
<td tal:repeat="ar ar_batch"
    tal:attributes="colspan python:ar.getReportDryMatter() and 2 or 1">
<span 
    tal:define="date_sampled python:ar.getSample().getDateSampled()"
    tal:condition="date_sampled"
    tal:content="python:plone_view.toLocalizedTime(date_sampled)">2005-01-01 10:00</span>
</td>
</tr>

<tr>
<th i18n:translate="label_daterequested">Date requested
</th>
<td tal:repeat="ar ar_batch"
    tal:attributes="colspan python:ar.getReportDryMatter() and 2 or 1"
    tal:content="python:plone_view.toLocalizedTime(ar.getDateRequested())">2005-01-01 10:00</td>
</tr>

<tr>
<th i18n:translate="label_datereceived">Date received
</th>
<td tal:repeat="ar ar_batch"
    tal:attributes="colspan python:ar.getReportDryMatter() and 2 or 1">
<span
    tal:define="date_received ar/getDateReceived|nothing"
    tal:condition="date_received"
    tal:content="python:plone_view.toLocalizedTime(date_received)">2005-01-01 10:00</span>
</td>
</tr>

<tr>
<th i18n:translate="label_datepublished">Date published
</th>
<td tal:repeat="ar ar_batch"
    tal:attributes="colspan python:ar.getReportDryMatter() and 2 or 1">
<span
    tal:define="date_published ar/getDatePublished|nothing"
    tal:condition="date_published"
    tal:content="python:plone_view.toLocalizedTime(date_published)">2005-01-01 10:00</span>
</td>
</tr>

<tr>
<th i18n:translate="label_status">Status
</th>
<td tal:repeat="ar ar_batch"
    tal:attributes="colspan python:ar.getReportDryMatter() and 2 or 1"
    tal:content="python:here.portal_workflow.getInfoFor(ar, 'review_state', '').replace('_', ' ')">sample_due</td>
</tr>

<tr>
<th i18n:translate="label_submitted_by">Submitted by </th>
<td tal:repeat="ar ar_batch"
    tal:attributes="colspan python:ar.getReportDryMatter() and 2 or 1"
    tal:content="python:ar.getSample().getSubmittedByName()">Joe Splane
</td>
</tr>

<tr>
<th i18n:translate="label_verified_by">Verified by </th>
<td tal:repeat="ar ar_batch"
    tal:attributes="colspan python:ar.getReportDryMatter() and 2 or 1">
<span
    tal:define="verifier python:here.get_analysisrequest_verifier(ar)"
    tal:content="verifier">
</span>
</td>
</tr>

<tr>
<th>
<b i18n:translate="label_analysis_results" i18n:domain="bika">
Analysis results</b>
</th>
<tal:results tal:repeat="ar ar_batch">
<tal:drymatter tal:condition="ar/getReportDryMatter">
<th><b i18n:translate="label_as_fed">As Fed</b></th>
<th class="dryhead"><b i18n:translate="label_dry">Dry</b></th>
</tal:drymatter>
<tal:notdrymatter tal:condition="not:ar/getReportDryMatter">
<th></th>
</tal:notdrymatter>
</tal:results>
</tr>
</thead>

<tbody>
<tal:arcount 
    tal:repeat="ar ar_batch">
<tal:ar 
    tal:define="global columns python:ar.getReportDryMatter() and columns + 2 or columns + 1">
</tal:ar>
</tal:arcount>
<tal:service
    tal:define="global category python:None"
    tal:repeat="service services">
<tr tal:condition="python:service.getCategoryName() != category">
<td class="category" 
        tal:attributes="colspan python:columns + 1"
    tal:define="global category service/getCategoryName"
    tal:content="service/getCategoryName"></td>
</tr>
<tr tal:define="service_unit service/getUnit|nothing">
<th nowrap>
<span tal:content="service/Title">Alcohol</span>
<em tal:content="service_unit">ml</em>
<img src="" 
    tal:condition="python:dry_matter and service.getReportDryMatter()"
    tal:attributes="src string:${portal/absolute_url}/dry.jpg">
<img src="" 
    tal:condition="python:accredited and service.getAccredited()"
    tal:attributes="src string:${portal/absolute_url}/accredited.jpg">
</th>

<tal:block repeat="ar ar_batch">
<tal:notfound
    tal:condition="python:service.getId() not in ar.objectIds()">
<td> </td>
<td tal:condition="ar/getReportDryMatter"> </td>
</tal:notfound>
<tal:x condition="python:service.getId() in ar.objectIds()">
<tal:result 
    tal:define="
        service_id service/getId;
        analysis python:ar[service_id];
        result analysis/getResult|nothing;
        is_client here/member_is_client; 
        verified python:here.portal_workflow.getInfoFor(analysis, 'review_state', '') in ['verified', 'published'];
        requested python:not here.portal_workflow.getInfoFor(analysis, 'review_state', '') in ['not_requested']">
<tal:view
    tal:condition="python:(is_client and verified) or (result and requested and not is_client)">
<div tal:define="
        sampletype python:ar.getSample().getSampleType();
        sampletype_uid sampletype/UID;
        client_uid python:ar.aq_parent.UID();
        result_class python:here.result_in_range(analysis, sampletype_uid, specification);
        global out_of_range python:result_class == 'out_of_range' and 1 or out_of_range">
<td nowrap align="center"
      tal:attributes="class result_class">
<span tal:content="result">10.00</span>
<img tal:condition="python:result_class == 'out_of_range'"
    src="" tal:attributes="src string:${portal/absolute_url}/exclamation.jpg">
<em tal:condition="python:analysis.getUnit() != service_unit"
    tal:content="string:(${analysis/getUnit})"/>
<div class="retested"
      tal:condition="analysis/getRetested"
      i18n:translate="retested">retested</div>
</td>
<td tal:condition="ar/getReportDryMatter">
<span tal:condition="analysis/getResultDM"
    tal:content="analysis/getResultDM">10</span>
</td>
</div>
</tal:view>
<tal:viewnothing
    tal:condition="python:requested and not result">
<td>
<span class="discreet" 
    tal:define="global tf python:1"
    i18n:translate="label_tofollow">TF</span>
</td>
<td tal:condition="ar/getReportDryMatter">
<img src="" 
    tal:condition="service/getReportDryMatter"
    tal:attributes="src string:${portal/absolute_url}/to_follow.png">
</td>
</tal:viewnothing>

<tal:notrequested
    tal:condition="python:not requested and result">
<td>
<span class="discreet" 
    tal:define="global nr python:1"
    i18n:translate="label_notrequested">NR</span>
</td>
<td tal:condition="ar/getReportDryMatter">
<img src="" 
    tal:condition="service/getReportDryMatter"
    tal:attributes="src string:${portal/absolute_url}/to_follow.png">
</td>
</tal:notrequested>

<tal:noview
    tal:condition="python:result and requested and is_client and not verified">
<td>
<span class="discreet" 
    tal:define="global tf python:1"
    i18n:translate="label_tofollow">TF</span>
</td>
<td tal:condition="ar/getReportDryMatter">
<img src="" 
    tal:condition="service/getReportDryMatter"
    tal:attributes="src string:${portal/absolute_url}/to_follow.png">
</td>
</tal:noview>
</tal:result>
</tal:x>

</tal:block>
</tr>
</tal:service>

</tbody>

</table>

<table class="remarks">
<th class="tabletitle"
    colspan="2"
    i18n:translate="label_remarks">Remarks</th>
<tr tal:repeat="ar ar_batch">
<th tal:content="string:${ar/getRequestID}:">AR:</th>
<td tal:content="python:ar.getNotes() or default">None</td>
</tr>
</table>

<div class="discreeter"
    tal:define="global seq_no python:0">

<p tal:condition="out_of_range">
<img src="" tal:attributes="src string:${portal/absolute_url}/exclamation.jpg">
<span i18n:translate="legend_out_of_rangex">
Result out of <tal:block replace="specification" i18n:name="spec"/> specified range
</span>
</p>

<p tal:condition="tf">
<img src="" tal:attributes="src string:${portal/absolute_url}/to_follow.jpg">
<span i18n:translate="description_tofollow">Results to follow</span>
</p>

<p tal:condition="nr">
<img src="" tal:attributes="src string:${portal/absolute_url}/not_requested.jpg">
<span i18n:translate="description_notrequested">Results not requested</span>
</p>

<p tal:condition="dry_matter">
<img src="" tal:attributes="src string:${portal/absolute_url}/dry.jpg">
<span i18n:translate="disclaimer_dry">
Reported as dry matter</span>
</p>

<p tal:condition="invoice_exclude">
<img src="" tal:attributes="src string:${portal/absolute_url}/no_invoice.jpg">
<span i18n:translate="disclaimer_invoice_exclude">
Not invoiced</span>
</p>

<p tal:condition="accredited">
<img src="" tal:attributes="src string:${portal/absolute_url}/accredited.jpg">
<span i18n:translate="disclaimer_accred">
Methods included in the <tal:block replace="context/bika_labinfo/laboratory/AccreditationBody" i18n:name="accreditation_body"/> schedule of Accreditation for this Laboratory. Analysis remarks are not accredited</span>
</p>

<p>
<span tal:define="global seq_no python:seq_no + 1"
    tal:content="string:$seq_no.">1</span>
<span i18n:translate="disclaimer_results_samples_tested">
Analysis results relate only to the samples tested</span></p>

<p>
<span tal:define="global seq_no python:seq_no + 1"
    tal:content="string:$seq_no.">1</span>
<span i18n:translate="disclaimer_no_reproduce">
This document shall not be reproduced except in full, without the written approval of <tal:block replace="context/bika_labinfo/laboratory/Title" i18n:name="name_lab"/></span></p>

<p tal:define="confidence_level context/bika_labinfo/laboratory/Confidence|nothing"
    tal:condition="confidence_level">
<span tal:define="global seq_no python:seq_no + 1"
    tal:content="string:$seq_no.">1</span>
<span i18n:translate="disclaimer_confidence_level">
Test results are at a <tal:block replace="confidence_level" i18n:name="lab_confidence"/>% confidence level</span></p>

<p> 
<span tal:define="global seq_no python:seq_no + 1"
    tal:content="string:$seq_no.">1</span>
<span i18n:translate="label_methods_online">
Methods of analysis available by clicking on the 'Request' link</span></p>

</div>
</tal:block>


</body>
</html>

"""}

order_query_results = {
    'title': 'Order query mail template',
    'description': 'Email order query template.',
    'mail_subject': 'string:Results for query on orders',
    'mail_body':
"""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html tal:define="portal python:options['portal']">
<style>
body {
    font-family: Arial, "Lucida Grande", Verdana, Lucida, Helvetica, sans-serif;
    font-size: 10;
    background-color: White;
    color: Black;
    margin: 1em;
    padding: 0;
}

a {
    text-decoration: none;
    color: #436976;
    background-color: transparent;
}
img {
    border: none;
    vertical-align: middle;
}
p {
    margin: 0.5em 0em 1em 0em;
    line-height: 1.5em;
}
p a {
    text-decoration: underline;
}
p a:visited {
    color: Purple;
    background-color: transparent;
}
p a:active {
    color: Red;
    background-color: transparent;
}
p img {
    border: 0;
    margin: 0;
}

hr {
    height: 1px;
    color: #d3d3ad;
    background-color: transparent;
}

h1, h2, h3, h4, h5, h6 {
    color: Black;
    background-color: transparent;
    font-family: Arial, "Lucida Grande", Verdana, Lucida, Helvetica, sans-serif;
    font-size: 69%;
    font-weight: normal;
    margin: 0;
    padding-top: 0.5em;
    border-bottom: 1px solid #636321;
}

h1 a,
h2 a,
h3 a,
h4 a,
h5 a,
h6 a {
    color: Black ! important; 
}

h1 {
    font-size: 160%;
}

h2 {
    font-size: 150%;
}

h3 {
    font-size: 140%;
    border-bottom: none;
    font-weight: bold;
}

h4 {
    font-size: 120%;
    border-bottom: none;
    font-weight: bold;
}

h5 {
    font-size: 100%;
    border-bottom: none;
    font-weight: bold;
}

h6 {
    font-size: 85%;
    border-bottom: none;
    font-weight: bold;
}
.documentDescription {
    font-weight: bold;
    display: block;
    margin: 1em 0em;
    line-height: 1.5em;
}
.documentByLine {
    text-align: left;
    font-size: 85%;
    clear: both;
    font-weight: normal;
    color: #76797c;
}
.documentByLine a {
    text-decoration: underline;
}
.eventDetail {
    font-style: italic;
}

.listing,
.stx table {
    /* The default table for document listings. Contains name, document types, modification times etc in a file-browser-like fashion */
    border-collapse: collapse;
    border-left: &dtml-borderWidth; &dtml-borderStyle; &dtml-globalBorderColor;;
    border-bottom: &dtml-borderWidth; &dtml-borderStyle; &dtml-globalBorderColor;;
    font-size: &dtml-fontSmallSize;;
    margin: 1em 0em 1em 0em;
}
.listing th,
.stx table th {
    background: &dtml-globalBackgroundColor;;
    border-top: &dtml-borderWidth; &dtml-borderStyle; &dtml-globalBorderColor;;
    border-bottom: &dtml-borderWidth; &dtml-borderStyle; &dtml-globalBorderColor;;
    border-right: &dtml-borderWidth; &dtml-borderStyle; &dtml-globalBorderColor;;
    font-weight: normal;
    padding: 0em 1em 0em 1em;
    text-decoration: underline;
    text-transform: &dtml-textTransform;;
}
.listing .top {
    border-left: &dtml-borderWidth; &dtml-borderStyle; &dtml-backgroundColor;;
    border-top: &dtml-borderWidth; &dtml-borderStyle; &dtml-backgroundColor; ! important;
    border-right: &dtml-borderWidth; &dtml-borderStyle; &dtml-backgroundColor; ! important;
    text-align: right ! important;
    padding: 0em 0em 1em 0em;
}
.listing .odd {
    /*every second line should be shaded */
    background-color: &dtml-oddRowBackgroundColor;;
}
.listing .even {
    background-color: &dtml-evenRowBackgroundColor;;
}
.listing .listingCheckbox {
    text-align: center;
}
.listing td,
.stx table td {
    border-right: &dtml-borderWidth; &dtml-borderStyle; &dtml-globalBorderColor;;
    padding: 0em 1em;
    text-align: left;
}
.listing a:hover {
    text-decoration: underline;
}
.listing img {
    vertical-align: middle;
}
.address {
    width: 100%
}
.address td {
    width: 50%;
    vertical-align: top;
}
</style>
<body>

<!-- actual list of objects, either searchresults or folder contents -->
<tal:block
    tal:define="
        plone_view python:context.restrictedTraverse('@@plone');
        laboratory python:options['laboratory'];
        lab_address python:laboratory.getPostalAddress();
        lab_address python:lab_address and lab_address or laboratory.getBillingAddress();
        lab_address python:lab_address and lab_address or laboratory.getPhysicalAddress();
        contact python:options['contact'];

        here python:options['portal'];
        request python:options['request'];
        results python:options['results'];
        orders python:[b.getObject() for b in results]"
    i18n:domain="bika">

<img src="" tal:attributes="src string:${portal/absolute_url}/lab_logo.jpg">

<table class="address">
<tr>
<td tal:condition="contact">
<tal:x   tal:define="
        client python:contact.aq_parent;
        contact_address python:contact.getPostalAddress();
        contact_address python:contact_address and contact_address or contact.getBillingAddress();
        contact_address python:contact_address and contact_address or client.getPostalAddress();
        contact_address python:contact_address and contact_address or client.getBillingAddress();
        contact_address python:contact_address and contact_address or contact.getPhysicalAddress();
        contact_address python:contact_address and contact_address or client.getPhysicalAddress()">
<div tal:content="contact/getFullname"></div>
<div tal:content="client/Title"></div>
<div tal:define="address python:contact_address.get('address','')"
    tal:content="structure python:modules['Products.PythonScripts.standard'].newline_to_br(address)"> </div>
<div tal:content="python:contact_address.get('city','')"></div>
<div tal:content="python:contact_address.get('state','')"></div>
<div tal:content="python:contact_address.get('zip','')"></div>
<div tal:content="python:contact_address.get('country','')"></div>
</tal:x>
</td>
<td tal:condition="python:not contact">&nbsp;</td>
<td>
<div tal:content="laboratory/Title"></div>
<div tal:define="address python:lab_address.get('address','')"
    tal:content="structure python:modules['Products.PythonScripts.standard'].newline_to_br(address)"> </div>
<div tal:content="python:lab_address.get('city','')"></div>
<div tal:content="python:lab_address.get('state','')"></div>
<div tal:content="python:lab_address.get('zip','')"></div>
<div tal:content="python:lab_address.get('country','')"></div>
</td>
</tr>
</table>

<table
    class="listing"
    summary="order listing"
    cellpadding="2" cellspacing="0"
    tal:condition="orders"
    i18n:domain="bika">

<thead>

<tr>
<th i18n:translate="label_ordernumber">Order number</th>
<th i18n:translate="label_client">Client</th>
<th i18n:translate="label_orderdate">Order date</th>
<th i18n:translate="label_datedispatched">Date dispatched</th>
</thead>

<tbody>
<tr tal:repeat="order orders">
<td><a href="#" tal:attributes="href order/absolute_url"
    tal:content="python:order.getOrderNumber()">Order 1234</a></td>
<td tal:define="client nocall:order/aq_parent"
    tal:content="client/Title">Client Name</td>
<td tal:content="python:plone_view.toLocalizedTime(order.getOrderDate(), long_format=1)">2005-01-01</td>
<td tal:content="python:plone_view.toLocalizedTime(order.getDateDispatched(), long_format=1)">2005-01-01</td>
</tr>
</tbody>

</table>

</tal:block>

</body>
</html>
"""}

invoice_query_results = {
    'title': 'Email invoice query template',
    'description': 'Email invoice query template.',
    'mail_subject': 'string:Results for query on invoices',
    'mail_body':
"""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html tal:define="portal python:options['portal']">
<style>
body {
    font-family: Arial, "Lucida Grande", Verdana, Lucida, Helvetica, sans-serif;
    font-size: 10;
    background-color: White;
    color: Black;
    margin: 1em;
    padding: 0;
}

a {
    text-decoration: none;
    color: #436976;
    background-color: transparent;
}
img {
    border: none;
    vertical-align: middle;
}
p {
    margin: 0.5em 0em 1em 0em;
    line-height: 1.5em;
}
p a {
    text-decoration: underline;
}
p a:visited {
    color: Purple;
    background-color: transparent;
}
p a:active {
    color: Red;
    background-color: transparent;
}
p img {
    border: 0;
    margin: 0;
}

hr {
    height: 1px;
    color: #d3d3ad;
    background-color: transparent;
}

h1, h2, h3, h4, h5, h6 {
    color: Black;
    background-color: transparent;
    font-family: Arial, "Lucida Grande", Verdana, Lucida, Helvetica, sans-serif;
    font-size: 69%;
    font-weight: normal;
    margin: 0;
    padding-top: 0.5em;
    border-bottom: 1px solid #636321;
}

h1 a,
h2 a,
h3 a,
h4 a,
h5 a,
h6 a {
    color: Black ! important; 
}

h1 {
    font-size: 160%;
}

h2 {
    font-size: 150%;
}

h3 {
    font-size: 140%;
    border-bottom: none;
    font-weight: bold;
}

h4 {
    font-size: 120%;
    border-bottom: none;
    font-weight: bold;
}

h5 {
    font-size: 100%;
    border-bottom: none;
    font-weight: bold;
}

h6 {
    font-size: 85%;
    border-bottom: none;
    font-weight: bold;
}
.documentDescription {
    font-weight: bold;
    display: block;
    margin: 1em 0em;
    line-height: 1.5em;
}
.documentByLine {
    text-align: left;
    font-size: 85%;
    clear: both;
    font-weight: normal;
    color: #76797c;
}
.documentByLine a {
    text-decoration: underline;
}
.eventDetail {
    font-style: italic;
}

.listing,
.stx table {
    /* The default table for document listings. Contains name, document types, modification times etc in a file-browser-like fashion */
    border-collapse: collapse;
    border-left: &dtml-borderWidth; &dtml-borderStyle; &dtml-globalBorderColor;;
    border-bottom: &dtml-borderWidth; &dtml-borderStyle; &dtml-globalBorderColor;;
    font-size: &dtml-fontSmallSize;;
    margin: 1em 0em 1em 0em;
}
.listing th,
.stx table th {
    background: &dtml-globalBackgroundColor;;
    border-top: &dtml-borderWidth; &dtml-borderStyle; &dtml-globalBorderColor;;
    border-bottom: &dtml-borderWidth; &dtml-borderStyle; &dtml-globalBorderColor;;
    border-right: &dtml-borderWidth; &dtml-borderStyle; &dtml-globalBorderColor;;
    font-weight: normal;
    padding: 0em 1em 0em 1em;
    text-decoration: underline;
    text-transform: &dtml-textTransform;;
}
.listing .top {
    border-left: &dtml-borderWidth; &dtml-borderStyle; &dtml-backgroundColor;;
    border-top: &dtml-borderWidth; &dtml-borderStyle; &dtml-backgroundColor; ! important;
    border-right: &dtml-borderWidth; &dtml-borderStyle; &dtml-backgroundColor; ! important;
    text-align: right ! important;
    padding: 0em 0em 1em 0em;
}
.listing .odd {
    /*every second line should be shaded */
    background-color: &dtml-oddRowBackgroundColor;;
}
.listing .even {
    background-color: &dtml-evenRowBackgroundColor;;
}
.listing .listingCheckbox {
    text-align: center;
}
.listing td,
.stx table td {
    border-right: &dtml-borderWidth; &dtml-borderStyle; &dtml-globalBorderColor;;
    padding: 0em 1em;
    text-align: left;
}
.listing a:hover {
    text-decoration: underline;
}
.listing img {
    vertical-align: middle;
}
.address {
    width: 100%
}
.address td {
    width: 50%;
    vertical-align: top;
}
</style>
<body>

<!-- actual list of objects, either searchresults or folder contents -->
<tal:block
    tal:define="
        plone_view python:context.restrictedTraverse('@@plone');
        laboratory python:options['laboratory'];
        lab_address python:laboratory.getPostalAddress();
        lab_address python:lab_address and lab_address or laboratory.getBillingAddress();
        lab_address python:lab_address and lab_address or laboratory.getPhysicalAddress();
        contact python:options['contact'];

        here python:options['portal'];
        request python:options['request'];
        results python:options['results'];
        invoices python:[b.getObject() for b in results]"
    i18n:domain="bika">

<img src="" tal:attributes="src string:${portal/absolute_url}/lab_logo.jpg">

<table class="address">
<tr>
<td tal:condition="contact">
<tal:x  tal:define="
        client python:contact.aq_parent;
        contact_address python:contact.getPostalAddress();
        contact_address python:contact_address and contact_address or contact.getBillingAddress();
        contact_address python:contact_address and contact_address or client.getPostalAddress();
        contact_address python:contact_address and contact_address or client.getBillingAddress();
        contact_address python:contact_address and contact_address or contact.getPhysicalAddress();
        contact_address python:contact_address and contact_address or client.getPhysicalAddress()">
<div tal:content="contact/getFullname"></div>
<div tal:content="client/Title"></div>
<div tal:define="address python:contact_address.get('address','')"
    tal:content="structure python:modules['Products.PythonScripts.standard'].newline_to_br(address)"> </div>
<div tal:content="python:contact_address.get('city','')"></div>
<div tal:content="python:contact_address.get('state','')"></div>
<div tal:content="python:contact_address.get('zip','')"></div>
<div tal:content="python:contact_address.get('country','')"></div>
</tal:x>
</td>
<td tal:condition="python:not contact">&nbsp;</td>
<td>
<div tal:content="laboratory/Title"></div>
<div tal:define="address python:lab_address.get('address','')"
    tal:content="structure python:modules['Products.PythonScripts.standard'].newline_to_br(address)"> </div>
<div tal:content="python:lab_address.get('city','')"></div>
<div tal:content="python:lab_address.get('state','')"></div>
<div tal:content="python:lab_address.get('zip','')"></div>
<div tal:content="python:lab_address.get('country','')"></div>
</td>
</tr>
</table>

<table
    class="listing"
    summary="invoice listing"
    cellpadding="2" cellspacing="0"
    tal:condition="invoices"
    i18n:domain="bika">

<thead>
<tr>
<th i18n:translate="label_invoicenumber">Invoice number</th>
<th i18n:translate="label_client">Client</th>
<th i18n:translate="label_invoicedate">Invoice date</th>
</thead>

<tbody>
<tr tal:repeat="invoice invoices">
<td><a href="#" tal:attributes="href invoice/absolute_url"
    tal:content="invoice/getInvoiceNumber">Invoice 1234</a></td>
<td tal:define="client invoice/getClient"
    tal:content="client/Title">Client Name</td>
<td tal:content="python:plone_view.toLocalizedTime(invoice.getInvoiceDate(), long_format=1)">2005-01-01</td>
</tr>
</tbody>

</table>

</tal:block>

</body>
</html>
"""}

mail_pricelist = {
    'title': 'Pricelist mail template',
    'description': 'Pricelist mail template',
    'mail_subject': 'options/pricelist/Title',
    'mail_body':
"""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html tal:define="portal python:options['portal']">
<style>
body {
    font-family: Arial, "Lucida Grande", Verdana, Lucida, Helvetica, sans-serif;
    font-size: 10;
    background-color: White;
    color: Black;
    margin: 1em;
    padding: 0;
}

a {
    text-decoration: none;
    color: #436976;
    background-color: transparent;
}
img {
    border: none;
    vertical-align: middle;
}
p {
    margin: 0.5em 0em 1em 0em;
    line-height: 1.5em;
}
p a {
    text-decoration: underline;
}
p a:visited {
    color: Purple;
    background-color: transparent;
}
p a:active {
    color: Red;
    background-color: transparent;
}
p img {
    border: 0;
    margin: 0;
}

hr {
    height: 1px;
    color: #d3d3ad;
    background-color: transparent;
}

h1, h2, h3, h4, h5, h6 {
    color: Black;
    background-color: transparent;
    font-family: Arial, "Lucida Grande", Verdana, Lucida, Helvetica, sans-serif;
    font-size: 69%;
    font-weight: normal;
    margin: 0;
    padding-top: 0.5em;
    border-bottom: 1px solid #636321;
}

h1 a,
h2 a,
h3 a,
h4 a,
h5 a,
h6 a {
    color: Black ! important; 
}

h1 {
    font-size: 160%;
}

h2 {
    font-size: 150%;
}

h3 {
    font-size: 140%;
    border-bottom: none;
    font-weight: bold;
}

h4 {
    font-size: 120%;
    border-bottom: none;
    font-weight: bold;
}

h5 {
    font-size: 100%;
    border-bottom: none;
    font-weight: bold;
}

h6 {
    font-size: 85%;
    border-bottom: none;
    font-weight: bold;
}

.logos {
    width: 50%
}

.invoice {
    border-collapse: collapse;
    border-left: &dtml-borderWidth; &dtml-borderStyle; &dtml-globalBorderColor;;
    border-bottom: &dtml-borderWidth; &dtml-borderStyle; &dtml-globalBorderColor;;
    font-size: &dtml-fontSmallSize;;
    margin: 1em 0em 1em 0em;
    width: 100%
}

.invoice th {
    border-top: &dtml-borderWidth; &dtml-borderStyle; &dtml-globalBorderColor;;
    border-right: &dtml-borderWidth; &dtml-borderStyle; &dtml-globalBorderColor;;
    padding: 0em 1em 0em 1em;
    text-align: left;
}

.invoice .top {
    border-left: &dtml-borderWidth; &dtml-borderStyle; &dtml-backgroundColor;;
    border-top: &dtml-borderWidth; &dtml-borderStyle; &dtml-backgroundColor; ! important;
    border-right: &dtml-borderWidth; &dtml-borderStyle; &dtml-backgroundColor; ! important;
    text-align: right ! important;
    padding: 0em 0em 1em 0em;
}
.invoice td {
    border-right: &dtml-borderWidth; &dtml-borderStyle; &dtml-globalBorderColor;;
    border-top: &dtml-borderWidth; &dtml-borderStyle; &dtml-globalBorderColor;;
    border-bottom: &dtml-borderWidth; &dtml-borderStyle; &dtml-globalBorderColor;;
    padding-left: 1em;
    vertical-align: top;
}

.invoice a:hover {
    text-decoration: underline;
}

.invoice img {
    vertical-align: middle;
}

.invoice .amount {
    text-align: right;
    padding-right: 1em;
}
</style>

<body>


<tal:block define="pricelist python:options['pricelist'];
                   here python:portal;
                   request python:options['request']; 
                   lab_accredited python:context.bika_labinfo.laboratory.getLaboratoryAccredited()"
    i18n:domain="bika">

<table class="logos">
<tr><td>
<img src="" tal:attributes="src string:${portal/absolute_url}/lab_logo.jpg">
</td>
<td tal:condition="lab_accredited">
<img src="" tal:attributes="src string:${portal/absolute_url}/accreditation_logo.jpg">
</td></tr>
</table>

<metal:block use-macro="here/pricelist_print/macros/pricelist"/>
</tal:block>

</body>
</html>
"""}


mail_standardsamples = {
    'title': 'Standard samples mail template',
    'description': 'Standard samples mail template',
    'mail_subject': 'string:Standard samples',
    'mail_body':
"""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html tal:define="portal python:options['portal']">

<head>
<style>
body {
    font-family: Arial, "Lucida Grande", Verdana, Lucida, Helvetica, sans-serif;
    font-size: 10;
    background-color: White;
    color: Black;
    margin: 1em;
    padding: 0;
}

img {
    border: none;
    vertical-align: middle;
}

h1 {
    font-size: 200%;
}

table {
    border-collapse:collapse;
    margin: 1px 0em 1px 0em;
}
tr {
    page-break-inside: avoid;
}
th {
    border: 1px solid Black;
    padding: 2px 1em 2px 1em;
    text-align: left;
}
td {
    border: 1px solid Black;
    padding: 2px 1em 2px 1em;
}
th.low {
    vertical-align: bottom;
}
td.low {
    vertical-align: bottom;
}
hr.narrow {
    margin: 2px 0em 2px 0em;
    height: 1px;
    color: Black;
    background-color: Black;
}

</style>
</head>

<body>

<tal:block define="here python:portal"
           i18n:domain="bika">

<img src="" tal:attributes="src string:${portal/absolute_url}/lab_logo.jpg">
<metal:block use-macro="here/standardsamples_print/macros/standardsamples"/>
</tal:block>

</body>
</html>
"""}


mail_standardstocks = {
    'title': 'Standard stocks mail template',
    'description': 'Standard stocks mail template',
    'mail_subject': 'string:Standard stocks',
    'mail_body':
"""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html tal:define="portal python:options['portal']">

<head>
<style>
body {
    font-family: Arial, "Lucida Grande", Verdana, Lucida, Helvetica, sans-serif;
    font-size: 10;
    background-color: White;
    color: Black;
    margin: 1em;
    padding: 0;
}

img {
    border: none;
    vertical-align: middle;
}

h1 {
    font-size: 200%;
}

table {
    border-collapse:collapse;
    margin: 1px 0em 1px 0em;
}
tr {
    page-break-inside: avoid;
}
th {
    border: 1px solid Black;
    padding: 2px 1em 2px 1em;
    text-align: left;
}
td {
    border: 1px solid Black;
    padding: 2px 1em 2px 1em;
}

</style>
</head>

<body>

<tal:block define="here python:portal"
           i18n:domain="bika">

<img src="" tal:attributes="src string:${portal/absolute_url}/lab_logo.jpg">
<metal:block use-macro="here/standardstocks_print/macros/standardstocks"/>
</tal:block>

</body>
</html>
"""}

templates = {
    PROJECTNAME: {
        'attributes': {'title':'bika mail templates',},
        'templates': {
            'ar_results_csv': ar_results_csv,
            'ar_results': ar_results,
            'SMS': sms,
            'ar_query_results': ar_query_results, 
            'order_query_results': order_query_results, 
            'invoice_query_results': invoice_query_results, 
            'mail_pricelist': mail_pricelist, 
            'mail_standardsamples': mail_standardsamples, 
            'mail_standardstocks': mail_standardstocks, 
        }
    }
}
