from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import TimeOrDate

class AccreditationView(BrowserView):
    """
    """
    template = ViewPageTemplateFile("templates/accreditation.pt")

    def __init__(self, context, request):
        super(AccreditationView, self).__init__(context, request)

        lab = self.context.bika_setup.laboratory
        self.accredited = lab.getLaboratoryAccredited()

        self.mapping = {'labname': lab.getName(),
                        'labcountry': lab.getPhysicalAddress().get('country', ''),
                        'confidence': lab.getConfidence(),
                        'abbr': lab.getAccreditationBody(),
                        'body': lab.getAccreditationBodyLong(),
                        'url': lab.getAccreditationBodyURL(),
                        'accr': lab.getAccreditation(),
                        'ref': lab.getAccreditationReference()
                        }

        msg =  _("accreditation_description",
                 default = "${labname} has been accredited as ${accr} " + \
                           "conformant by ${abbr}, (${body}). ${abbr} is " + \
                           "recognised by government as a national " + \
                           "accreditation body in ${labcountry}",
                 mapping = self.mapping)

        self.accreditation_description = self.context.translate(msg)

    def __call__(self):
        return self.template()
