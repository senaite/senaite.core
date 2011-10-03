from plone.app.controlpanel.overview import OverviewControlPanel

def Overview(PloneOverviewControlPanel):

    def categories(self):
        # add bika to the list of control panel categories.
        groups = PloneOverviewControlPanel.categories()
        groups.append({'id': 'bika', 'title': u'Bika Configuration'})
        return groups