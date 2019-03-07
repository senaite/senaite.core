# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from zope.interface import Interface

class IRequestAnalysis(Interface):
    """This adapter distinguishes analyses that have a request assigned from
    those that do not have one. Typically, routine and duplicate analyses are
    assigned to a request, whilst reference analyses are not"""

    def getRequest(self):
        """Returns the Analysis Request this analysis belongs to
        :return: the Analysis Request this analysis belongs to
        :rtype: IAnalysisRequest
        """

    def getRequestID(self):
        """Returns the Analysis Request ID this analysis belongs to. If there
        is no Request assigned to this analysis, returns None
        :return: the Analysis Request ID this analysis belongs to
        :rtype: str
        """

    def getRequestUID(self):
        """Returns the Analysis Request UID this analysis belongs to. If there
        is no Request assigned to this analysis, returns None
        :return: the Analysis Request UID this analysis belongs to
        :rtype: str
        """

    def getRequestURL(self):
        """Returns the url path of the Analysis Request object this analysis
        belongs to. Returns None if there is no Request assigned.
        :return: the Analysis Request URL path this analysis belongs to
        :rtype: str
        """

    def getClient(self):
        """Returns the Client assigned to the Analysis Request this analysis
        belongs to. Returns None if there is no Request assigned
        :return: the Client associated to this analysis
        :rtype: IClient"""

    def getClientID(self):
        """Returns the UID of the Client assigned to the Analysis Request this
        analysis belongs to. Returns None if there is no Request nor a Client
        assigned to this analysis
        :return: the UID of the Client
        :rtype: str
        """

    def getClientUID(self):
        """Returns the UID of the Client assigned to the Analysis Request this
        analysis belongs to. Returns None if there is no Request nor a Client
        assigned to this analysis
        :return: the UID of the Client
        :rtype: str
        """

    def getClientTitle(self):
        """Returns the name of the Client assigned to the Analysis Request this
        analysis belongs to. Returns None if there is no Request nor a Client
        assigned to this analysis
        :return: the name of the Client
        :rtype: str
        """

    def getClientURL(self):
        """Returns the absolute url path of the Client assigned to the Analysis
        Request this analysis belongs to. Returns None if there is no Request
        nor a Client assigned to this analysis
        :return: the url path of the Client
        :type: str
        """
