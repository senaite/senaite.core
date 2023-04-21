# -*- coding: utf-8 -*-


def on_client_created(client, event):
    """Event handler when a new Client was created
    """
    # create a new client group
    client.create_group()
