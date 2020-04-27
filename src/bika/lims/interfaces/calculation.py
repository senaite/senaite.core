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

from zope.interface import Attribute, Interface


# noinspection PyMethodParameters
class ICalculation(Interface):
    """Describe Calculation attributes and fields.
    
    TODO Because Calculation uses Archetypes schema fields, this is messy;
    their respective getters/setters are included here, but fields which
    will fall away after porting away from Archetypes are not included.
    """

    schema = Attribute("This is the Archetypes Schema for a calculation.")

    def _renameAfterCreation(check_auto_id=False):
        """Calls bika.lims.idserver.renameAfterCreation to set the ID
        for this object
        """

    def setId(value):
        """Set the object ID.
        Inherited from Products.Archetypes/BaseObject.py
        """

    def getId():
        """Get the object ID.
        Inherited from Products.Archetypes/BaseObject.py
        """

    def setTitle(value):
        """Set the object's Title
        Inherited from Products.Archetypes/BaseObject.py
        """

    def Title():
        """Get the object Title.
        Inherited from Products.Archetypes/BaseObject.py
        """

    def setDescription(value):
        """Set the object's Description
        Inherited from Products.Archetypes/BaseObject.py
        """

    def Description():
        """Get the object Description.
        Inherited from Products.Archetypes/BaseObject.py
        """

    def setInterimFields(value):
        """Set the interim field values used for calculating results.
        """

    def getInterimFields():
        """Get the interim field values used for calculating results.
        """

    def setDependentServices(value):
        """Set the list of services referenced by this calculation's Formula
        """

    def getDependentServices():
        """Get the list of services referenced by this calculation's Formula
        """

    def setPythonImports(value):
        """Set the imported python methods available to this Calculation.
        """

    def getPythonImports():
        """Get the imported python methods available to this Calculation.
        """

    def setFormula(value):
        """Set the calculation's Formula (String) 
        """

    def getFormula():
        """Get the calculation's Formula (String) 
        """

    def setTestParameters(value):
        """Set the parameters defined to test the calculation
        """

    def getTestParameters():
        """Get the parameters defined to test the calculation
        """

    def setTestResult(value):
        """Set the result calculated with TestParameters value.
        """

    def getTestResult():
        """Get the result calculated with TestParameters value.
        """

    def workflow_script_activate(self):
        """A calculation cannot be re-activated if services it depends on
        are deactivated.
        """

    def workflow_script_deactivate(self):
        """A calculation cannot be deactivated if active services are using it.
        """
