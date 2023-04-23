# -*- coding: utf-8 -*-

from senaite.core.registry import get_registry_record


def on_client_created(client, event):
    """Event handler when a new Client was created
    """
    if get_registry_record("auto_create_client_group", True):
        # create a new client group
        client.create_group()
