Adding new reports
==================

Edit one of the report selection categories to add your report, and the form
that will be displayed to select criteria. This file is currently one of:

    bika/lims/browser/reports/templates/administration.pt
    bika/lims/browser/reports/templates/productivity.pt
    bika/lims/browser/reports/templates/qualitycontrol.pt

Add the following files for your report:

    bika/lims/browser/reports/templates/your_report_name.pt
    bika/lims/browser/reports/your_reort_name.py

Report names should be in the same form as the existing ones:
category_reportname.

It is assumed that report_name.py contains a class called Report.

The Report class should return a dictionary of 'report_title' and
'report_data'
 
In case of an error, the Report class may return a string. This is assumed
to be a template output, and is rendered.

