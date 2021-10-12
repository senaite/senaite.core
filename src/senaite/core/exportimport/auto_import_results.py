# -*- coding: utf-8 -*-

import logging
import os
import traceback

from six import string_types

from bika.lims import api
from bika.lims.catalog import SETUP_CATALOG
from DateTime import DateTime
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five.browser import BrowserView
from senaite.core import logger
from senaite.core.exportimport.instruments import get_automatic_parser
from senaite.core.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter
from zope.interface import alsoProvides

CR = "\n"
LOGFILE = "logs.log"
INDEXFILE = "imported.csv"


class AutoImportResultsView(BrowserView):
    """Auto import instrument results

    This view will be called from any periodically running script to run
    auto-import process. Instruments which has interfaces, and also interfaces
    which auto-import folders assigned, will participate in this process. To
    import for specified Instrument or/and Interface, these parameters can be
    set in URL as well.
    """
    def __init__(self, context, request):
        super(AutoImportResultsView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.logs = []

    def __call__(self):
        # disable CSRF because
        alsoProvides(self.request, IDisableCSRFProtection)
        # run auto import of results
        self.auto_import_results()
        # return the concatenated logs
        return CR.join(self.logs)

    def auto_import_results(self):
        """Check instrument results folders
        """
        interfaces = []
        for brain in self.query_active_instruments():
            instrument = api.get_object(brain)
            instrument_title = api.get_title(instrument)
            self.log("Auto import for %s started ..." % instrument_title,
                     instrument=instrument)

            # get a valid interface -> folder mapping
            mapping = self.get_interface_folder_mapping(instrument)

            # If Import Interface ID is specified in request, then auto-import
            # will run only that interface. Otherwise all available interfaces
            # of this instruments
            if self.request.get("interface"):
                interfaces.append(self.request.get("interface"))
            else:
                interfaces = mapping.keys()

            # import instrument results from all configured interfaces
            for interface in interfaces:
                folder = mapping.get(interface)
                # check if instrument import folder exists
                if not os.path.exists(folder):
                    self.log("Interface %s: Folder %s does not exist" %
                             (folder, interface), instrument=instrument,
                             interface=interface, level="error")
                    continue
                # get all files in the instrument folder
                allfiles = self.list_files(folder)
                # get already imported files
                imported = self.read_imported_files(folder)
                # import results file
                for f in allfiles:
                    if f in imported:
                        # skip already imported files
                        continue
                    self.import_results(instrument, interface, folder, f)

            self.log("Auto-Import finished")

    def import_results(self, instrument, interface, folder, resultsfile):
        """Import resultsfile for instrument interface
        """
        with open(os.path.join(folder, resultsfile), "r") as fileobj:
            wrapped = UploadFileWrapper(fileobj)
            parser = get_automatic_parser(interface, wrapped)
            if not parser:
                self.log("No parser found for %s" % resultsfile,
                         instrument=instrument, interface=interface,
                         level="warning")
                return False
            self.log("Parsing file %s" % resultsfile,
                     instrument=instrument, interface=interface)
            importer = AnalysisResultsImporter(
                parser=parser,
                context=self.context,
                override=[False, False],
                instrument_uid=api.get_uid(instrument))

            tb = None
            try:
                importer.process()
            except Exception:
                tb = traceback.format_exc()
            self.log(importer.logs, instrument=instrument, interface=interface)
            self.log(importer.errors, instrument=instrument,
                     interface=interface, level="error")
            if tb:
                self.log(tb, instrument=instrument, interface=interface,
                         level="error")

            # write imported file
            self.write_imported_file(folder, resultsfile)

        return True

    def list_files(self, folder, ignore=""):
        """Returns all files in folder

        :param folder: folder path
        :param ignore: comma separated list of file names to ignore
        """
        files = []
        ignore_files = ignore.split(",") if ignore else []
        for f in os.listdir(folder):
            # skip hidden files
            if f.startswith("."):
                continue
            path = os.path.join(folder, f)
            # skip folders
            if not os.path.isfile(path):
                continue
            # skip ignored files
            if f in ignore_files:
                continue
            files.append(f)
        return files

    def read_imported_files(self, folder):
        """Read filenames from index file
        """
        path = os.path.join(folder, INDEXFILE)

        # create the index file if it does not exist
        if not os.path.exists(path):
            with open(path, "wb") as fileobj:
                self.writelines(fileobj, [LOGFILE, INDEXFILE])
            return [INDEXFILE, LOGFILE]

        # read the contents of the file
        with open(path, "r") as fileobj:
            imported = fileobj.readlines()
            return [i.strip() for i in imported]

    def write_imported_file(self, folder, filename):
        """Append filename to index file
        """
        path = os.path.join(folder, INDEXFILE)
        with open(path, "a") as fileobj:
            self.writelines(fileobj, filename)

    def writelines(self, fileobj, lines):
        """write line to file with newline at the end

        :param fileobj: open file
        :param lines: list or string of lines to write
        """
        if isinstance(lines, string_types):
            lines = [lines]
        for line in lines:
            if not line.endswith(CR):
                line += CR
            fileobj.write(line)
        return fileobj

    def get_interface_folder_mapping(self, instrument):
        """Returns an instrument interface -> folder mapping

        :param instrument: Instrument object
        :returns: dictionary of interface -> folder path
        """
        mapping = {}
        for record in instrument.getResultFilesFolder():
            interface = record.get("InterfaceName")
            folder = record.get("Folder")
            if not folder:
                self.log("No folder set for interface %s" % interface,
                         instrument=instrument, interface=interface,
                         level="warning")
                continue
            mapping[interface] = folder
        return mapping

    def query_active_instruments(self):
        """Return all active instruments

        :returns: list of catalog brains
        """
        query = {
            "portal_type": "Instrument",
            "is_active": True
        }

        # BBB: request can specify instrument UID
        instrument_uid = self.request.get("i_uid")
        if instrument_uid is not None:
            query["UID"] = instrument_uid

        results = api.search(query, SETUP_CATALOG)
        return results

    def log(self, message, instrument=None, interface=None, level="info"):
        """Logging multiplexer

        :param message: Log message
        :param instrument: Instrument object
        :param interface: Interface name. e.g. generic.two_dimension
        :param level: Log level, e.g. debug, info, warning, error
        """
        if isinstance(message, (list, tuple)):
            for msg in message:
                self.log(msg, instrument=instrument, interface=interface,
                         level=level)
            return
        # log into default facility
        log_level = logging.getLevelName(level.upper())
        logger.log(level=log_level, msg=message)
        # Append to logs
        timestamp = DateTime.strftime(DateTime(), "%Y-%m-%d %H:%M:%S")
        log_msg = "%s [%s] " % (timestamp, level.upper())
        if instrument:
            log_msg += "[Instrument:%s] " % api.get_title(instrument)
        if interface:
            log_msg += "[Interface:%s] " % interface
        log_msg += "%s" % message
        self.logs.append(log_msg)


class UploadFileWrapper:
    """File object wrapper

    File objects don't have 'filename' and 'headers' attributes.
    Since Import step of different Interfaces checks if 'filename' is set
    to be sure that submitted form contains uploaded file, we also have to add
    this attribute to our File object.
    """
    def __init__(self, orig_file):
        if hasattr(orig_file, "__methods__"):
            methods = orig_file.__methods__
        else:
            methods = ["close", "fileno", "flush", "isatty",
                       "read", "readline", "readlines", "seek",
                       "tell", "truncate", "write", "writelines",
                       "__iter__", "next", "name"]
        d = self.__dict__
        for m in methods:
            if hasattr(orig_file, m):
                d[m] = getattr(orig_file, m)
        self.filename = orig_file.name
