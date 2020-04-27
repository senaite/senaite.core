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

import unittest

from bika.lims.tests.base import DataTestCase
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, login, setRoles
from Products.validation import validation as validationService


class Tests(DataTestCase):

    def setUp(self):
        super(Tests, self).setUp()
        setRoles(self.portal, TEST_USER_ID, ['Member', 'LabManager'])
        login(self.portal, TEST_USER_NAME)

    def test_UniqueFieldValidator(self):
        login(self.portal, TEST_USER_NAME)

        clients = self.portal.clients
        client1 = clients['client-2']  # not Happy Hills
        self.assertEqual(
            client1.schema.get('ClientID').validate('HH', client1),
            u"Validation failed: 'HH' is not unique")
        self.assertEqual(
            None,
            client1.schema.get(
                'title').validate(
                    'Another Client',
                    client1))

    def test_ServiceKeywordValidator(self):
        login(self.portal, TEST_USER_NAME)

        services = self.portal.bika_setup.bika_analysisservices
        service1 = services['analysisservice-1']

        self.assertEqual(
            service1.schema.get('Keyword').validate('', service1),
            u'Analysis Keyword is required, please correct.')
        self.assertEqual(
            service1.schema.get('Keyword').validate('&', service1),
            u'Validation failed: keyword contains invalid characters')
        self.assertEqual(
            service1.schema.get('Keyword').validate('Ca', service1),
            u"Validation failed: 'Ca': This keyword is already in use by service 'Calcium'")
        self.assertEqual(
            service1.schema.get('Keyword').validate('TV', service1),
            u"Validation failed: 'TV': This keyword is already in use by calculation 'Titration'")
        self.assertEqual(
            None,
            service1.schema.get(
                'Keyword').validate(
                    'VALID_KW',
                    service1))

    def test_InterimFieldsValidator(self):
        login(self.portal, TEST_USER_NAME)

        calcs = self.portal.bika_setup.bika_calculations
        # Titration
        calc1 = calcs['calculation-1']

        key = calc1.id + 'InterimFields'

        interim_fields = []
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.portal.REQUEST['validated'] = None
        if key in self.portal.REQUEST:
            self.portal.REQUEST[key] = False
        self.assertEqual(
            None,
            calc1.schema.get(
                'InterimFields').validate(
                    interim_fields,
                    calc1,
                    REQUEST=self.portal.REQUEST))

        interim_fields = [{'keyword': '&',
                           'title': 'Titration Volume',
                           'unit': '',
                           'default': ''},
                          ]
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.portal.REQUEST['validated'] = None
        if key in self.portal.REQUEST:
            self.portal.REQUEST[key] = False
        self.assertEqual(
            calc1.schema.get(
                'InterimFields').validate(
                    interim_fields,
                    calc1,
                    REQUEST=self.portal.REQUEST),
            u"Validation failed: keyword contains invalid characters")

        interim_fields = [
            {'keyword': 'XXX',
             'title': 'Gross Mass',
             'unit': '',
             'default': ''},
            {'keyword': 'TV', 'title': 'Titration Volume', 'unit': '', 'default': ''}]
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.portal.REQUEST['validated'] = None
        if key in self.portal.REQUEST:
            self.portal.REQUEST[key] = False
        self.assertEqual(
            calc1.schema.get(
                'InterimFields').validate(
                    interim_fields,
                    calc1,
                    REQUEST=self.portal.REQUEST),
            u"Validation failed: column title 'Gross Mass' must have keyword 'GM'")

        interim_fields = [
            {'keyword': 'GM', 'title': 'XXX', 'unit': '', 'default': ''},
            {'keyword': 'TV', 'title': 'Titration Volume', 'unit': '', 'default': ''}]
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.portal.REQUEST['validated'] = None
        if key in self.portal.REQUEST:
            self.portal.REQUEST[key] = False
        self.assertEqual(
            calc1.schema.get(
                'InterimFields').validate(
                    interim_fields,
                    calc1,
                    REQUEST=self.portal.REQUEST),
            u"Validation failed: keyword 'GM' must have column title 'Gross Mass'")

        interim_fields = [
            {'keyword': 'TV',
             'title': 'Titration Volume',
             'unit': '',
             'default': ''},
            {'keyword': 'TV', 'title': 'Titration Volume 1', 'unit': '', 'default': ''}]
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.portal.REQUEST['validated'] = None
        if key in self.portal.REQUEST:
            self.portal.REQUEST[key] = False
        self.assertEqual(
            calc1.schema.get(
                'InterimFields').validate(
                    interim_fields,
                    calc1,
                    REQUEST=self.portal.REQUEST),
            u"Validation failed: 'TV': duplicate keyword")

        interim_fields = [
            {'keyword': 'TV',
             'title': 'Titration Volume',
             'unit': '',
             'default': ''},
            {'keyword': 'TF', 'title': 'Titration Volume', 'unit': '', 'default': ''}]
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.portal.REQUEST['validated'] = None
        if key in self.portal.REQUEST:
            self.portal.REQUEST[key] = False
        self.assertEqual(
            calc1.schema.get(
                'InterimFields').validate(
                    interim_fields,
                    calc1,
                    REQUEST=self.portal.REQUEST),
            u"Validation failed: 'Titration Volume': duplicate title")

        interim_fields = [
            {'keyword': 'TV',
             'title': 'Titration Volume',
             'unit': '',
             'default': ''},
            {'keyword': 'TF', 'title': 'Titration Factor', 'unit': '', 'default': ''}]
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.portal.REQUEST['validated'] = None
        if key in self.portal.REQUEST:
            self.portal.REQUEST[key] = False
        self.assertEqual(
            None,
            calc1.schema.get(
                'InterimFields').validate(
                    interim_fields,
                    calc1,
                    REQUEST=self.portal.REQUEST))

    def test_UncertaintyValidator(self):
        login(self.portal, TEST_USER_NAME)
        services = self.portal.bika_setup.bika_analysisservices
        serv1 = services['analysisservice-1']
        v = validationService.validatorFor('uncertainties_validator')
        field = serv1.schema['Uncertainties']
        key = serv1.id + field.getName()

        uncertainties = [{'intercept_min': '100.01', 'intercept_max': '200', 'errorvalue': '200%'}]
        self.portal.REQUEST['Uncertainties'] = uncertainties
        res = v(uncertainties, instance=serv1, field=field, REQUEST=self.portal.REQUEST)
        self.failUnlessEqual(res, "Validation failed: Error percentage must be between 0 and 100")

        uncertainties = [{'intercept_min': 'a', 'intercept_max': '200', 'errorvalue': '10%'}]
        self.portal.REQUEST['Uncertainties'] = uncertainties
        if key in self.portal.REQUEST:
            self.portal.REQUEST[key] = False
        res = v(uncertainties, instance=serv1, field=field, REQUEST=self.portal.REQUEST)
        self.failUnlessEqual(res, "Validation failed: Min values must be numeric")

        uncertainties = [{'intercept_min': '100.01', 'intercept_max': 'a', 'errorvalue': '10%'}]
        self.portal.REQUEST['Uncertainties'] = uncertainties
        if key in self.portal.REQUEST:
            self.portal.REQUEST[key] = False
        res = v(uncertainties, instance=serv1, field=field, REQUEST=self.portal.REQUEST)
        self.failUnlessEqual(res, "Validation failed: Max values must be numeric")

        uncertainties = [{'intercept_min': '100.01', 'intercept_max': '200', 'errorvalue': 'a%'}]
        self.portal.REQUEST['Uncertainties'] = uncertainties
        if key in self.portal.REQUEST:
            self.portal.REQUEST[key] = False
        res = v(uncertainties, instance=serv1, field=field, REQUEST=self.portal.REQUEST)
        self.failUnlessEqual(res, "Validation failed: Error values must be numeric")

        uncertainties = [{'intercept_min': '200', 'intercept_max': '100', 'errorvalue': '10%'}]
        self.portal.REQUEST['Uncertainties'] = uncertainties
        if key in self.portal.REQUEST:
            self.portal.REQUEST[key] = False
        res = v(uncertainties, instance=serv1, field=field, REQUEST=self.portal.REQUEST)
        self.failUnlessEqual(res, "Validation failed: Max values must be greater than Min values")

        uncertainties = [{'intercept_min': '100', 'intercept_max': '200', 'errorvalue': '-5%'}]
        self.portal.REQUEST['Uncertainties'] = uncertainties
        if key in self.portal.REQUEST:
            self.portal.REQUEST[key] = False
        res = v(uncertainties, instance=serv1, field=field, REQUEST=self.portal.REQUEST)
        self.failUnlessEqual(res, "Validation failed: Error percentage must be between 0 and 100")

        uncertainties = [{'intercept_min': '100', 'intercept_max': '200', 'errorvalue': '-5'}]
        self.portal.REQUEST['Uncertainties'] = uncertainties
        if key in self.portal.REQUEST:
            self.portal.REQUEST[key] = False
        res = v(uncertainties, instance=serv1, field=field, REQUEST=self.portal.REQUEST)
        self.failUnlessEqual(res, "Validation failed: Error value must be 0 or greater")

    def test_FormulaValidator(self):
        login(self.portal, TEST_USER_NAME)

        v = validationService.validatorFor('formulavalidator')
        calcs = self.portal.bika_setup.bika_calculations
        calc1 = calcs['calculation-1']

        interim_fields = [
            {'keyword': 'TV',
             'title': 'Titration Volume',
             'unit': '',
             'default': ''},
            {'keyword': 'TF', 'title': 'Titration Factor', 'unit': '', 'default': ''}]
        self.portal.REQUEST.form['InterimFields'] = interim_fields

        formula = "[TV] * [TF] * [Wrong]"
        self.failUnlessEqual(
            v(formula, instance=calc1, field=calc1.schema.get(
                'Formula'), REQUEST=self.portal.REQUEST),
            "Validation failed: Keyword 'Wrong' is invalid")

        formula = "[TV] * [TF]"
        self.assertEqual(
            True,
            v(formula,
              instance=calc1,
              field=calc1.schema.get('Formula'),
              REQUEST=self.portal.REQUEST))

    def test_CoordinateValidator(self):
        login(self.portal, TEST_USER_NAME)

        sp = self.portal.bika_setup.bika_samplepoints['samplepoint-1']

        latitude = {
            'degrees': '!',
            'minutes': '2',
            'seconds': '3',
            'bearing': 'N'}
        self.portal.REQUEST.form['Latitude'] = latitude
        val = sp.schema.get('Latitude').validate(latitude, sp)
        self.assertEqual(
            True,
            u"Validation failed: degrees must be numeric" in val)

        latitude = {
            'degrees': '0',
            'minutes': '!',
            'seconds': '3',
            'bearing': 'N'}
        self.portal.REQUEST.form['Latitude'] = latitude
        self.portal.REQUEST['validated'] = None
        val = sp.schema.get('Latitude').validate(latitude, sp)
        self.assertEqual(
            True,
            u"Validation failed: minutes must be numeric" in val)

        latitude = {
            'degrees': '0',
            'minutes': '0',
            'seconds': '!',
            'bearing': 'N'}
        self.portal.REQUEST.form['Latitude'] = latitude
        self.portal.REQUEST['validated'] = None
        val = sp.schema.get('Latitude').validate(latitude, sp)
        self.assertEqual(
            True,
            u"Validation failed: seconds must be numeric" in val)

        latitude = {
            'degrees': '0',
            'minutes': '60',
            'seconds': '0',
            'bearing': 'N'}
        self.portal.REQUEST.form['Latitude'] = latitude
        self.portal.REQUEST['validated'] = None
        val = sp.schema.get('Latitude').validate(latitude, sp)
        self.assertEqual(
            True,
            u"Validation failed: minutes must be 0 - 59" in val)

        latitude = {
            'degrees': '0',
            'minutes': '0',
            'seconds': '60',
            'bearing': 'N'}
        self.portal.REQUEST.form['Latitude'] = latitude
        self.portal.REQUEST['validated'] = None
        val = sp.schema.get('Latitude').validate(latitude, sp)
        self.assertEqual(
            True,
            u"Validation failed: seconds must be 0 - 59" in val)

        # latitude specific

        latitude = {
            'degrees': '91',
            'minutes': '0',
            'seconds': '0',
            'bearing': 'N'}
        self.portal.REQUEST.form['Latitude'] = latitude
        self.portal.REQUEST['validated'] = None
        val = sp.schema.get('Latitude').validate(latitude, sp)
        self.assertEqual(
            True,
            u"Validation failed: degrees must be 0 - 90" in val)

        latitude = {
            'degrees': '90',
            'minutes': '1',
            'seconds': '0',
            'bearing': 'N'}
        self.portal.REQUEST.form['Latitude'] = latitude
        self.portal.REQUEST['validated'] = None
        val = sp.schema.get('Latitude').validate(latitude, sp)
        self.assertEqual(
            True,
            u"Validation failed: degrees is 90; minutes must be zero" in val)

        latitude = {
            'degrees': '90',
            'minutes': '0',
            'seconds': '1',
            'bearing': 'N'}
        self.portal.REQUEST.form['Latitude'] = latitude
        self.portal.REQUEST['validated'] = None
        val = sp.schema.get('Latitude').validate(latitude, sp)
        self.assertEqual(
            True,
            u"Validation failed: degrees is 90; seconds must be zero" in val)

        latitude = {
            'degrees': '90',
            'minutes': '0',
            'seconds': '0',
            'bearing': 'E'}
        self.portal.REQUEST.form['Latitude'] = latitude
        self.portal.REQUEST['validated'] = None
        val = sp.schema.get('Latitude').validate(latitude, sp)
        self.assertEqual(
            True,
            u"Validation failed: Bearing must be N/S" in val)

        # longitude specific

        longitude = {
            'degrees': '181',
            'minutes': '0',
            'seconds': '0',
            'bearing': 'E'}
        self.portal.REQUEST.form['Longitude'] = longitude
        self.portal.REQUEST['validated'] = None
        val = sp.schema.get('Longitude').validate(longitude, sp)
        self.assertEqual(
            True,
            u"Validation failed: degrees must be 0 - 180" in val)

        longitude = {
            'degrees': '180',
            'minutes': '1',
            'seconds': '0',
            'bearing': 'E'}
        self.portal.REQUEST.form['Longitude'] = longitude
        self.portal.REQUEST['validated'] = None
        val = sp.schema.get('Longitude').validate(longitude, sp)
        self.assertEqual(
            True,
            u"Validation failed: degrees is 180; minutes must be zero" in val)

        longitude = {
            'degrees': '180',
            'minutes': '0',
            'seconds': '1',
            'bearing': 'E'}
        self.portal.REQUEST.form['Longitude'] = longitude
        self.portal.REQUEST['validated'] = None
        val = sp.schema.get('Longitude').validate(longitude, sp)
        self.assertEqual(
            True,
            u"Validation failed: degrees is 180; seconds must be zero" in val)

        longitude = {
            'degrees': '0',
            'minutes': '0',
            'seconds': '0',
            'bearing': 'N'}
        self.portal.REQUEST.form['Longitude'] = longitude
        self.portal.REQUEST['validated'] = None
        val = sp.schema.get('Longitude').validate(longitude, sp)
        self.assertEqual(
            True,
            u"Validation failed: Bearing must be E/W" in val)

        longitude = {
            'degrees': '1',
            'minutes': '1',
            'seconds': '1',
            'bearing': 'E'}
        self.portal.REQUEST.form['Longitude'] = longitude
        self.portal.REQUEST['validated'] = None
        self.assertEqual(
            None,
            sp.schema.get(
                'Longitude').validate(
                    longitude,
                    sp))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Tests))
    return suite
