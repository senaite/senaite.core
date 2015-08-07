""" Sysmex XS 1000i
"""
import i500
# Since the printed results from the 500i and 100i are the same,
# we can import i500 features
title = "Sysmex XS - 1000i"

def Import(context, request):
    """ Sysmex XS - 1000i analysis results
    """
    return i500.Import(context, request, 'sysmex_xs_1000i')
