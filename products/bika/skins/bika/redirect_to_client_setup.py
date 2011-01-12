REQUEST=context.REQUEST
REQUEST.SESSION.set('client_setup_state', 'setup')
dest = '%s/base_edit' %(context.absolute_url())
REQUEST.RESPONSE.redirect(dest)
