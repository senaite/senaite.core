# -*- coding: utf-8 -*-

from zope import interface


class IInfo(interface.Interface):
    """ JSON Info Interface
    """

    def to_dict():
        """ return the dictionary representation of the object
        """

    def __call__():
        """ return the dictionary representation of the object
        """


class IDataManager(interface.Interface):
    """ Field Interface
    """

    def get(name):
        """ Get the value of the named field with
        """

    def set(name, value):
        """ Set the value of the named field
        """

    def json_data(name, default=None):
        """ Get a JSON compatible structure from the value
        """


class IFieldManager(interface.Interface):
    """A Field Manager is able to set/get the values of a single field.
    """

    def get(instance, **kwargs):
        """Get the value of the field
        """

    def set(instance, value, **kwargs):
        """Set the value of the field
        """

    def json_data(instance, default=None):
        """Get a JSON compatible structure from the value
        """


class ICatalog(interface.Interface):
    """ Plone catalog interface
    """

    def search(query):
        """ search the catalog and return the results
        """

    def get_catalog():
        """ get the used catalog tool
        """

    def get_indexes():
        """ get all indexes managed by this catalog
        """

    def get_index(name):
        """ get an index by name
        """

    def to_index_value(value, index):
        """ Convert the value for a given index
        """


class ICatalogQuery(interface.Interface):
    """ Plone catalog query interface
    """

    def make_query(**kw):
        """ create a new query or augment an given query
        """


class IBatch(interface.Interface):
    """ Batch Interface
    """

    def get_batch():
        """ return the wrapped batch object
        """

    def get_pagesize():
        """ return the current page size
        """

    def get_pagenumber():
        """ return the current page number
        """

    def get_numpages():
        """ return the current number of pages
        """

    def get_sequence_length():
        """ return the length
        """

    def make_next_url():
        """ build and return the next url
        """

    def make_prev_url():
        """ build and return the previous url
        """
