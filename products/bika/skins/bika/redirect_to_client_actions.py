REQUEST=context.REQUEST
REQUEST.SESSION.set('client_setup_state', 'actions')
dest = '%s/client_analysisrequests' %(context.absolute_url())
REQUEST.RESPONSE.redirect(dest)
