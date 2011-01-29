from Acquisition import aq_parent, aq_inner
from Products.bika import logger
from Products.bika.browser.bika_folder_contents import BikaFolderContentsView
from Products.bika.interfaces import IClientFolderView
from zope.interface import implements

class ClientAnalysisRequestsView(BikaFolderContentsView):
    implements(IClientFolderView)
    allowed_content_types = ['AnalysisRequest']
    contentFilter = {'portal_type': 'AnalysisRequest'}
    batch = True
    b_size = 100
    full_objects = False
    wflist_states = [
                    {'title': 'All', 'id':'all'},
                    {'title': 'Sample due', 'id':'sample_due'},
                    {'title': 'Sample received', 'id':'sample_received'},
                    {'title': 'Assigned to Worksheet', 'id':'assigned'},
                    {'title': 'To be verified', 'id':'to_be_verified'},
                    {'title': 'Verified', 'id':'verified'},
                    {'title': 'Published', 'id':'published'},
                    ]
    columns = [
              {'title': 'Client ID', 'field':'getClientID'},
              {'title': 'Title', 'field':'title_or_id'},
              {'title': 'Modified', 'field':'modified'},
              {'title': 'State', 'field':'state_title'},
              ]

class ClientSamplesView(BikaFolderContentsView):
    implements(IClientFolderView)
    allowed_content_types = ['Sample']
    contentFilter = {'portal_type': 'Sample'}
    batch = True
    b_size = 100
    full_objects = False
    wflist_states = [
                    {'title': 'All', 'id':'all'},
                    {'title': 'Due', 'id':'sample_due'},
                    {'title': 'Received', 'id':'sample_received'},
                    {'title': 'Expired', 'id':'sample_expired'},
                    {'title': 'Disposed', 'id':'sample_disposed'},
                    ]
    columns = [
              {'title': 'Sample ID', 'field':'getSampleID'},
#              {'title': 'Requests', 'field':'title_or_id'},
#              {'title': 'Client Ref', 'field':'modified'},
#              {'title': 'Client SID', 'field':'state_title'},
#              {'title': 'Sample Type', 'field':'title_or_id'},
#              {'title': 'Sample Point', 'field':'modified'},
#              {'title': 'Date Received', 'field':'state_title'},
              ]

class ClientContactsView(BikaFolderContentsView):
    implements(IClientFolderView)
    allowed_content_types = ['Contact']
    contentFilter = {'portal_type': 'Contact'}
    batch = True
    b_size = 100
    full_objects = False
    wflist_states = []
    columns = [
              {'title': 'Full Name', 'field':'getFullname'},
              {'title': 'Email Address', 'field':'getEmailAddress'},
              {'title': 'Business Phone', 'field':'getBusinessPhone'},
              {'title': 'Mobile Phone', 'field':'getMobilePhone'},
              {'title': 'Fax', 'field':'getFax'},
              ]

