from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from bika.lims.config import PROJECTNAME
from zope.i18nmessageid import MessageFactory
import logging

PloneMessageFactory = MessageFactory('plone')
_ = MessageFactory(PROJECTNAME)

def createObjects(parent, children):
    """Create new objects or modify existing ones.
    @param parent: The parent plone folder
    @param children: A (possibly nested) list of dictionaries:
        [{ 'id':      'clients', 
           'title':   'Clients',
           'description': 'A folder for Clients',
           'type':   'ClientFolder',
           'layout': 'folder_listing',
           'children': [{  'id':      'company1', 
                           'title':   'First Client',
                           'description': 'A client',
                           'type':   'Client',
                           'layout': 'folder_listing',
                           'children': (another list of dictionaries)
                       },],
        },]
    """
    logger = logging.getLogger('bika.lims')
    existing = parent.objectIds()
    for new_object in children:
        if not new_object['id'] in existing:
            _createObjectByType(new_object['type'], parent, \
                id = new_object['id'], title = new_object['title'], \
                description = new_object['description'])
        obj = parent.get(new_object['id'], None)
        if obj is None:
            # can't modify object but continue anyway
            logger.warn("can't get %s, shouldn't happen" % new_object['id'])
        else:
            if obj.Type() != new_object['type']:
                logger.warn("existing object %s is of wrong type, skipping!")
            else:
                obj.setLayout(new_object['layout'])
                #workflow.doActionFor(obj, 'publish')
                obj.reindexObject()
                children = new_object.get('children', [])
                if len(children) > 0:
                    createObjects(obj, children)

def setupVarious(context):
    """Initial configuration.  Ideally everything should be handled by
    the GenericSetup XML profile, but that's not always possible.
    """
    if context.readDataFile('bika.lims.txt') is None:
        return

    logger = logging.getLogger('bika.lims')
    portal = context.getSite()
    membership = getToolByName(portal, 'portal_membership', None) 
    workflow = getToolByName(portal, 'portal_workflow')

    # Hide the standard Plone stuff that we don't want around
    # XXX does not play well with others?  Should at least hide,
    # instead of deleting.
    existing = portal.objectIds()
    items = ['Members', 'news', 'events']
    logger.info("Hiding default portal content: %s" % items)
    for item in items:
        if item in existing:
            portal.manage_delObjects(item)

    # Create folder structure.  We do it here so that we can control
    # exactly when it happens, and how.
    logger.info("Creating new portal content")
    top_folders = [{'id': 'clients',
                    'title': 'Clients',
                    'description': 'Folder for Clients',
                    'type': 'ClientFolder',
                    'layout': 'view',
          },
        ]
    createObjects(parent = portal, children = top_folders)

    # Configure the control panel configlets.
    logger.info("Configuring the Control Panel")
    groups = portal.portal_controlpanel.group
    site_groups = [g[0] for g in groups['site']]
