# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.interfaces import IVocabulary
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
try:
    from zope.component.hooks import getSite
except:
    # Plone < 4.3
    from zope.app.component.hooks import getSite


class RejectionWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/rejectionwidget",
        'helper_js': ("bika_widgets/rejectionwidget.js",),
        'helper_css': ("bika_widgets/rejectionwidget.css",),
    })

    security = ClassSecurityInfo()

    def isVisible(self, instance, mode='view', default=None, field=None):
        """
        This function returns the visibility of the widget depending on whether
        the rejection workflow is enabled or not.
        """
        vis = super(RejectionWidget, self).isVisible(
            instance=instance, mode=mode, default=default, field=field)
        if instance.bika_setup.isRejectionWorkflowEnabled():
            return vis
        else:
            return 'invisible'

    def rejectionOptionsList(self):
        "Return a sorted list with the options defined in bikasetup"
        plone = getSite()
        settings = plone.bika_setup
        # RejectionReasons will return something like:
        # [{'checkbox': u'on', 'textfield-2': u'b', 'textfield-1': u'c', 'textfield-0': u'a'}]
        if len(settings.RejectionReasons) > 0:
            reject_reasons = settings.RejectionReasons[0]
        else:
            return []
        sorted_keys = sorted(reject_reasons.keys())
        if 'checkbox' in sorted_keys:
            sorted_keys.remove('checkbox')
        # Building the list with the values only because the keys are not needed any more
        items = []
        for key in sorted_keys:
            items.append(reject_reasons[key].strip())
        return items

    def isRejectionEnabled(self, dd):
        """
        'd' is a dictionary with the stored data in the widget like:
        {u'selected': [u'a', u'b'], u'checkbox': True, u'other': 'dsadas', u'checkbox_other': True}
        Return whether the checkbox of the widget is enabled or not
        """
        return dd['checkbox'] if 'checkbox' in dd.keys() else False

    def getRejectionReasons(self,dd):
        """
        'd' is a dictionary with the stored data in the widget like:
        {u'selected': [u'a', u'b'], u'checkbox': True, u'other': 'dsadas', u'checkbox_other': True}
        Returns a string with the options both from selected and input items
        """
        keys = dd.keys()
        reasons = []
        if not('checkbox' in keys ) or not(dd['checkbox']):
            return 0
        if 'selected' in keys:
            reasons += dd['selected']
        if 'other' in keys and dd['checkbox_other']:
            reasons.append(dd['other'])
        if len(reasons) < 1:
            return "Yes, unknow"
        return ', '.join(reasons)

registerWidget(RejectionWidget,
               title = "Rejection Widget",
               description = ('Widget to choose rejection reasons and set the rejection workflow'),
               )
