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
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget
from Products.CMFPlone.i18nl10n import ulocalized_time

class ScheduleInputWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'ulocalized_time': ulocalized_time,
        'macro': "bika_widgets/scheduleinputwidget",
        'helper_js': ("bika_widgets/scheduleinputwidget.js",),
        'helper_css': ("bika_widgets/scheduleinputwidget.css",),
        'maxDate': '+0d',
        'yearRange': '-100:+0'
    })
    
    security = ClassSecurityInfo()
    
    def process_form(self, instance, field, form, empty_marker=None, emptyReturnsMarker=False):
        
        values = len(instance.getScheduleCriteria())>0 and instance.getScheduleCriteria() or []
        
        if "form.button.save" in form:
            value = []            
            fn = form['fieldName']
            fromDate = fn + "_fromdate" in form and form[fn+"_fromdate"] or None
            fromEnabled = (fromDate and fn + "_fromenabled" in form and form[fn+"_fromenabled"] == 'on') and True or False            
            repeatUnit = fn + "_repeatunit" in form and form[fn+"_repeatunit"] or None
            repeatPeriod = fn + "_repeatperiodselected" in form and form[fn+"_repeatperiodselected"] or None
            repeatEnabled = (repeatUnit and fn + "_repeatenabled" in form and form[fn+"_repeatenabled"] == 'on') and True or False           
            repeatUntil = fn + "_repeatuntil" in form and form[fn+"_repeatuntil"] or None
            repeatUntilEnabled = (repeatUntil and fn + "_repeatuntilenabled" in form and form[fn+"_repeatuntilenabled"] == 'on') and True or False
            
            value.append({'fromenabled': fromEnabled,
                          'fromdate': fromDate,
                          'repeatenabled': repeatEnabled,
                          'repeatunit':repeatUnit,
                          'repeatperiod':repeatPeriod,
                          'repeatuntilenabled':repeatUntilEnabled,
                          'repeatuntil':repeatUntil})
            
        return value, {}      
       

registerWidget(ScheduleInputWidget,
               title = 'ScheduleInputWidget',
               description = ('Control for scheduling'),
               )
