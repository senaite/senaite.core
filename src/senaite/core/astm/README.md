# SENAITE ASTM Interface

This package provides a JSON API endpoint and a results importer for the
[senaite.astm](https://github.com/senaite/senaite.astm) middleware.


## JSON Message Format 

The required message format of this interface is JSON.

One JSON format comes in the following format:

    {
        u'H': [{...}],
        u'P': [{...}],
        u'O': [{...}],
        u'R': [{...}, ...],
        u'C': [{...}, ...],
        u'M': [{...}, ...],
        u'Q': [{...}, ...],
        u'L': [{...}]
    }
    
Where all records come as lists of dictionaries.

Please refer to the `senaite.astm.records` module to see the Python aliases for
the LIS2-A identifiers.


## Results Importer

The consumer will lookup for a named adapter for an adapter first, where the
name is equal to the *sender name* of the header record.

Therefore, you could register a specific adapter, e.g. for the Yumizen H550 as follows:

``` xml
    <configure xmlns="http://namespaces.zope.org/zope">
        <!-- Adapter to handle instrument imports from senaite.astm -->
        <adapter name="H550" factory=".astm_importer.ASTMImporter" />
    </configure>
```
    
And implement the `import_data` method like this:

``` python
    from bika.lims import api
    from senaite.core.astm.importer import ASTMImporter as Base
    from senaite.core.interfaces import IASTMImporter
    from senaite.core.interfaces import ISenaiteCore
    from zope.component import adapter
    from zope.interface import Interface
    from zope.interface import implementer

    ALLOWED_SAMPLE_STATES = ["sample_received"]

    @adapter(Interface, Interface, ISenaiteCore)
    @implementer(IASTMImporter)
    class ASTMImporter(Base):
        """ASTM results importer for Yumizen H500/H550
        """

        def import_data(self):
            """Import Yumizen H550 Results
            """
            if not self.instrument:
                return self.log("Instrument not found")

            if not self.sample:
                return self.log("Sample not found")

            self.log("Starting instrument import")

            sample = self.sample
            sample_id = self.sample.getId()
            sample_state = api.get_workflow_status_of(self.sample)
            sender = self.get_sender()
            instrument = self.instrument
            instrument_title = self.instrument.Title()
            analyses = sample.getAnalyses(full_objects=True)

            if sample_state not in ALLOWED_SAMPLE_STATES:
                return self.log(
                    "Sample review state must be in %s" %
                    ", ".join(ALLOWED_SAMPLE_STATES))

            self.log("Starting results import for sample '%s'" % sample_id)

            # crate a new attachment with the message contents
            filename = "%s.txt" % "_".join(sender)
            attachment = self.create_attachment(
                sample.getClient(), self.message, filename=filename)
            attachments = sample.getAttachment()
            if attachment not in attachments:
                attachments.append(attachment)
                sample.setAttachment(attachments)

            for result in self.get_results():
                value = result.get("value")
                ...
```


## ASTM Server Configuration

The consumer and importer support only the JSON format from the middleware.

Therefore, the `senaite.astm` server needs to be started, e.g. like this:

    $ senaite-astm-server -m json -u http://admin:admin@localhost:8080/senaite
    
For more information, used the command:

``` sh
    $ senaite-astm-server -h
    
    usage: senaite-astm-server [-h] [-l LISTEN] [-p PORT] [-o OUTPUT] [-u URL] [-c CONSUMER] [-m MESSAGE_FORMAT]
                               [-r RETRIES] [-d DELAY] [-v] [--logfile LOGFILE]

    optional arguments:
    -h, --help            show this help message and exit
    -v, --verbose         Verbose logging (default: False)
    --logfile LOGFILE     Path to store log files (default: senaite-astm-server.log)

    ASTM SERVER:
    -l LISTEN, --listen LISTEN
                            Listen IP address (default: 0.0.0.0)
    -p PORT, --port PORT  Port to connect (default: 4010)
    -o OUTPUT, --output OUTPUT
                            Output directory to write full messages (default: None)

    SENAITE LIMS:
    -u URL, --url URL     SENAITE URL address including username and password in the format:
                            http(s)://<user>:<password>@<senaite_url> (default: None)
    -c CONSUMER, --consumer CONSUMER
                            SENAITE push consumer interface (default: senaite.core.lis2a.import)
    -m MESSAGE_FORMAT, --message-format MESSAGE_FORMAT
                            Message format to send to SENAITE. Allowed formats: "astm", "lis2a", "json". (default: json)
    -r RETRIES, --retries RETRIES
                            Number of attempts of reconnection when SENAITE instance is not reachable. Only has
                            effect when argument --url is set (default: 3)
    -d DELAY, --delay DELAY
                            Time delay in seconds between retries when SENAITE instance is not reachable. Only
                            has effect when argument --url is set (default: 5)
```

**☝️ NOTE:** A proper instrument schema needs to be written to extract the required
fields for the importer, see `senaite.astm.instruments` for examples.
