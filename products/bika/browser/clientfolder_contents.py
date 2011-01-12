from five import grok
from Acquisition import aq_inner
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from Products.bika.interfaces import IClientFolder

class clientfolder_view(grok.View):
    """
    """
    
    grok.context(IClientFolder)
    grok.require('zope2.View')
    grok.name('clientfolder_view')

    def display_colums(self):
        return {}

    def render(self):
        return ViewPageTemplateFile(filename = "folder_tabular_view.pt")
