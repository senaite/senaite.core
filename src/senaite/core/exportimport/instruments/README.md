# SENAITE Instrument Import

This package contains the framework for file-based instrument importers and parsers.


## Registering a custom Instrument Importer

To hook in a custom instrument importer, a basic import view needs to be provided.

Therefore, an import adapter needs to be registered.

In `configure.zcml`:

``` xml
  <adapter
    for="*"
    factory=".my_instrument.MyInstrumentImporter"
    provides="senaite.core.exportimport.instruments.IInstrumentImportInterface"/>
```


In `my_instrument.py`:

``` python
    from bika.lims import api
    from senaite.core.exportimport.instruments import IInstrumentAutoImportInterface
    from senaite.core.exportimport.instruments import IInstrumentImportInterface
    from senaite.core.exportimport.instruments.importer import ALLOWED_ANALYSIS_STATES
    from senaite.core.exportimport.instruments.importer import ALLOWED_SAMPLE_STATES
    from senaite.core.exportimport.instruments.importer import AnalysisResultsImporter
    from senaite.core.exportimport.instruments.parser import InstrumentResultsFileParser
    from senaite.core.exportimport.instruments.utils import get_instrument_import_ar_allowed_states
    from senaite.core.exportimport.instruments.utils import get_instrument_import_override
    from zope.interface import implementer

    @implementer(IInstrumentImportInterface, IInstrumentAutoImportInterface)
    class MyImporter(AnalysisResultsImporter):
        title = "My Instrument"

        def __init__(self, context):
            self.context = context
            self.override = [False, False]
            self.allowed_sample_states = ALLOWED_SAMPLE_STATES
            self.allowed_analysis_states = ALLOWED_ANALYSIS_STATES

        def get_automatic_importer(self, instrument, parser, **kw):
            """Called during automated results import
            """
            # initialize the base class with the required parameters
            super(MyInstrumentImporter, self).__init__(
                parser, self.context,
                override=self.override,
                allowed_sample_states=self.allowed_sample_states,
                allowed_analysis_states=self.allowed_analysis_states,
                instrument_uid=api.get_uid(instrument))
            return self

        def get_automatic_parser(self, infile):
            """Called during automated results import

            Returns the parser to be used by default for the file passed in when
            automatic results import for this instrument interface is enabled
            """
            return MyInstrumentParser(infile)

        def Import(self, context, request):
            """Called from the manual import view
            """
            # Get the uploaded results file
            infile = request.form.get("instrument_results_file")
            # Sample states to apply results?
            allowed_states = request.form.get("artoapply", "received")
            # The selected instrument
            instrument_uid = request.form.get("instrument", None)

            if not infile:
                return json.dumps({
                    "errors": ["No file selected", ],
                    "log": [],
                    "warns": []
                })

            # Override results?
            override = request.form.get("results_override", "nooverride")
            self.override = get_instrument_import_override(override)

            # allowed states
            self.allowed_sample_states = get_instrument_import_ar_allowed_states(
                allowed_states)

            # instrument
            instrument = api.get_object(instrument_uid)
            parser = self.get_automatic_parser(infile)
            importer = self.get_automatic_importer(instrument, parser)

            importer.process()

            return json.dumps({
                "errors": self.errors,
                "log": self.logs,
                "warns": self.warns,
            })
            
            
    class MyInstrumentParser(InstrumentResultsFileParser):
        """Parse the import file and fills the raw results dictionary
        """
        def __init__(self, infile):
            InstrumentResultsFileParser.__init__(self, infile, "JSON")

        def parse(self):
            """Parses the input file and generate the results dictionary for import
            
            see: `senaite.core.exportimport.instruments.parser.getRawResults` 
            """
            return super(MyInstrumentParser, self).parse()

```


The rendered form template must be provided as `my_instrument_import.pt` in the same directory: 

``` html
    <div class="my-2">
      <label for="instrument_results_file">File</label>
      <input type="file" name="instrument_results_file" id="instrument_results_file"/>
      <label for="instrument_results_file_format">Format</label>
      <select name="instrument_results_file_format" id="instrument_results_file_format">
        <option value="csv">CSV</option>
      </select>
      <p></p>
    
      <h3>Advanced options</h3>
      <table cellpadding="0" cellspacing="0">
        <tr>
          <td><label for="artoapply">Samples state</label></td>
          <td>
            <select name="artoapply" id="artoapply">
              <option value="received">Received</option>
              <option value="received_tobeverified">Received and to be verified</option>
            </select>
          </td>
        </tr>
        <tr>
          <td><label for="results_override">Results override</label></td>
          <td>
            <select name="results_override" id="results_override">
              <option value="nooverride">Don't override results</option>
              <option value="override">Override non-empty results</option>
              <option value="overrideempty">Override non-empty results (also with empty)</option>
            </select>
          </td>
        </tr>
      </table>
      <p></p>
      <input name="firstsubmit" type="submit" value="Submit" i18n:attributes="value"/>
    </div>
```

