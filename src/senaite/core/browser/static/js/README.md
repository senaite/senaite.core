# SENAITE CORE LEGACY JS

Please see https://github.com/senaite/senaite.core/pull/2719 for details


## Legacy scripts

Legacy controller scripts are located in `senaite.core/src/senaite/core/browser/static/js`
and are managed by `senaite.core.loader.js` based on a CSS selector mapping.


### senaite.core.analysisrequest.add.js

This controller is loaded for the sample add form, e.g. `/senaite/samples/ar_add`.


**☝️ Notes**

  - This file is compiled from a `coffee` source!


**Changes**

  - Uses now `senaite.core.globals.portalMessage` instead of `bika.lims.portalMessage`


### senaite.core.analysisrequest.js

This controller is loaded for sample view, e.g. `/senaite/samples/clients/client-1/H2O-0001`.

**Changes**

  - Removed unused event handlers
  - Removed unused controllers `AnalysisRequestViewView` and `AnalysisRequestAnalysesView`

**What does it do?**

  - Handle the lookup and insertion of interpretation templates


### senaite.core.bikasetup.js

This controller is loaded for the old bika setup view, e.g. `/senaite/bika_setup`.

**☝️ Notes**

  - Functionality should be refactored to an edit form adapter


**What does it do?**

  - Ensures that if `Allow access to worksheets only to assigned analysts` is
    selected on the `Security` tab, that the checkbox `Only lab managers can
    create and manage worksheets` is selected as well (and prevents unchecking).

  - Shows the field `Multi Verification type` if `Number of required verifications` is > 0



### senaite.core.calculation.edit.js

This controller is loaded for the calculation edit view, e.g. `/senaite/bika_setup/bika_calculations/calculation-1`.

**☝️ Notes**

  - This file can be removed as soon as https://github.com/senaite/senaite.core/pull/2600 is merged!

**What does it do?**

  - Hides the `more` button of the test parameters datagrid field
  - Adds a new row for the test parameters if a new keyword in brackets was
    added to the formula field, e.g.`[x_interim]`


### senaite.core.client.js

This controller is loaded for the client edit view, e.g. `/senaite/clients/client-1`.

**☝️ Notes**

  - Functionality should be refactored to an edit form adapter

**What does it do?**

  - Shows the `Custom decimal mark` field if the checkbox `Default decimal mark` is unchecked


### senaite.core.common.js

This controller is *always* loaded, i.e. for the `html` CSS selector (see `senaite.core.loader`).

**☝️ Notes**

  - Global functions should be moved to `senaite.core.js`

**What does it do?**

It creates the `senaite.core.globals` namespace and provides the followin global functions in it:

  - `portalMessage`: Display a status message
  - `log`: Logs into the server log with `logger.info`
  - `warning`: Logs into the server log with `logger.warn`
  - `error`: Logs into the server log with `logger.error`
  - `jsonapi_read`: Provides access the the JSON API read functionality, e.g. to load interpretation templates:

  ```javascript
      const request_data = {
        catalog_name: "uid_catalog",
        UID: template_uid,
        include_fields: ["text"]
      };

      window.senaite.core.globals.jsonapi_read(request_data, (data) => {
        if (data.objects.length === 1) {
          const text = data.objects[0].text;
          tinymce.get(container_id).insertContent(text);
        }
      });
  ```

### senaite.core.graphics.controlchart.js

Wrapper class for D3 control chart used for QC samples, e.g. in

  - senaite.core.instrument.js
  - senaite.core.referencesample.js

**☝️ Notes**

  - Does not act as a controller and is instantiated manually, e.g.:
    `const chart = new ControlChart();`

**What does it do?**

  - Renders a D3 control chart for referenceanalyses, e.g.:
    `/senaite/bika_setup/bika_instruments/instrument-1/referenceanalyses`
    `/senaite/setup/suppliers/supplier-1/QC-001/analyses`


### senaite.core.graphics.range.js

Wrapper class for D3 control range chart.

**☝️ Notes**

Currently not used, but kept for reference!


### senaite.core.instrument.js

This file contains the following 3 controllers:

  - `InstrumentEditView`: Loaded for the instrument edit form
  - `InstrumentCertificationEditView`: Loaded for the instrument certification edit form
  - `InstrumentReferenceAnalysesView`: Loaded for the instrument QC samples tab

**What does it do?**

`InstrumentEditView`

  - Add new rows to the `Result files folders` datagrid field when the `Import Data Interface` selection changed
  - Ensures that at least one empty row remains if all instrument interfaces are deselected


`InstrumentCertificationEditView`

  - Hides the `Agency` field if `Internal Certificate` is checked

`InstrumentReferenceAnalysesView`

  - Loads the D3js control chart for the selected QC sample and reference analysis
  - Filters the listing view depending on the selected reference analysis
  - Handles chart updates on interpolation change
  - Handles click events on the chart datapoints
  - Provides a print functionality


### senaite.core.loader.js

Dynamic loader for view controllers based on found CSS selectors

**☝️ Notes**

  - Instantiated controllers can be accessed via `senaite.core.controllers.<ControllerClassName>`
  - Controllers can be loaded via `senaite.core.globals.loadControllers()`

**What does it do?**

  - Provides the `senaite.core.controllers` namespace
  - Dynamically load controllers


### senaite.core.referencesample.js

This controller is loaded for reference sample analyses, e.g. `/senaite/setup/suppliers/supplier-1/QC-001/analyses`.

**What does it do?**

  - Loads the D3js control chart for the reference analyses of the sample
  - Filters the listing view depending on the selected reference analysis
  - Handles chart updates on interpolation change
  - Handles click events on the chart datapoints
  - Provides a print functionality


### senaite.core.site.js

This controller is *always* loaded, i.e. for the `html` CSS selector (see `senaite.core.loader`).

**☝️ Notes**

  We have partially duplicated code provided by `window.site`, which is set in `senaite.core.js`

**What does it do?**

  - Handles `ajaxStart`, `ajaxStop` and `ajaxError` events to show/hide the loader at the top of the screen
  - Allows to read/write cookies (moved to `window.site` )
  - Handles `keyup`, `keypress` and `paste` events for integer/float fields to ensure propper input
  - Handles overlays, e.g. when clicking on the info icon of a sample analysis
  - Provides the method `notify_in_panel` which shows a short notification on the screen
    (currently only used in `senaite.core.worksheet.js`)


### senaite.core.utils.attachments.js

This controller is loaded when the Attachments Viewlet is loaded, e.g. for Samples and Worksheets.

**What does it do?**

  - Dynamically enable/disable the "Add" button to ensure a file is attached


### senaite.core.utils.barcode.js

This controller is loaded when a barcode or qrcode element was found, e.g. for the sticker view
`/senaite/samples/clients/client-1/H2O-001/sticker`

**☝️ Notes**

This controller depends on the following third party libraries:

  - `jquery-barcode-2.2.0.min.js`
  - `jquery-qrcode-0.17.0.min.js`

Dependencies are located in `senaite.core/src/senaite/core/browser/static/thirdparty`


**What does it do?**

  - Uses `jQuery.barcode` to render barcodes
  - Uses `jQuery.qrcode` to render barcodes


### senaite.core.worksheet.js

This file contains the following 2 controllers:
  - `WorksheetFolderView`: Loaded for the worksheet folder listing, e.g. `/senaite/worksheets`.
  - `WorksheetManageResultsView`: Loaded for a worksheet, e.g. `/senaite/worksheets/WS-001`

#### WorksheetFolderView

**☝️ Notes**

The `WorksheetFolderView` JS depends currently on a hidden input field
`input.templateinstruments` where a static template uid -> instrument uid
mapping is provided.

**What does it do?**

  - Select propper instrument if the template changes
  - Display a panel notification if an instrument is selected

#### WorksheetManageResultsView

**What does it do?**

  - Handles analyst changes (auto-save)
  - Handles instrument changes (auto-save)
  - Shows Sample remarks in overlay
  - Allows to set wide interims


### senaite.core.worksheet.print.js

This controller is loaded for the worksheet print view, e.g. `/senaite/worksheets/WS-001/print`.

**What does it do?**

  - Reloads the view when a template is changed
  - Render barcodes
  - Handles the print button event
