""" ScilVet abc Plus
"""
from bika.lims.exportimport.instruments.abaxis.vetscan.vs2 import \
    AbaxisVetScanCSVVS2Parser, AbaxisVetScanVS2Importer, Import as VS2Import

title = "ScilVet abc - Plus"


def Import(context, request):
    """
    We will use the same import logic as Abaxis VetScan VS2
    """
    return VS2Import(context, request)


class ScilVetabcPlusCSVParser(AbaxisVetScanCSVVS2Parser):
    """
    This instrument will use the same parser as Abaxis VetScan VS2
    """


class ScilVetabcPlusImporter(AbaxisVetScanVS2Importer):
    """
    This instrument will use the same importer as Abaxis VetScan VS2
    """