The Analysis Service content type
===============================

In this section we are tesing the Analysis Service content type by performing
basic operations like adding, updadating and deleting Analysis Service content
items.

Adding a new Analysis Service content item
--------------------------------

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'Analysis Service' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Analysis Service').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Analysis Service' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Analysis Service Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

And we are done! We added a new 'Analysis Service' content item to the portal.

Updating an existing Analysis Service content item
---------------------------------------

Let's click on the 'edit' tab and update the object attribute values.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='title').value = 'New Analysis Service Sample'
    >>> browser.getControl('Save').click()

We check that the changes were applied.

    >>> 'Changes saved' in browser.contents
    True
    >>> 'New Analysis Service Sample' in browser.contents
    True

Removing a/an Analysis Service content item
--------------------------------

If we go to the home page, we can see a tab with the 'New Analysis Service
Sample' title in the global navigation tabs.

    >>> browser.open(portal_url)
    >>> 'New Analysis Service Sample' in browser.contents
    True

Now we are going to delete the 'New Analysis Service Sample' object. First we
go to the contents tab and select the 'New Analysis Service Sample' for
deletion.

    >>> browser.getLink('Contents').click()
    >>> browser.getControl('New Analysis Service Sample').click()

We click on the 'Delete' button.

    >>> browser.getControl('Delete').click()
    >>> 'Item(s) deleted' in browser.contents
    True

So, if we go back to the home page, there is no longer a 'New Analysis Service
Sample' tab.

    >>> browser.open(portal_url)
    >>> 'New Analysis Service Sample' in browser.contents
    False

Adding a new Analysis Service content item as contributor
------------------------------------------------

Not only site managers are allowed to add Analysis Service content items, but
also site contributors.

Let's logout and then login as 'contributor', a portal member that has the
contributor role assigned.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = 'contributor'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

We select 'Analysis Service' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Analysis Service').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Analysis Service' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Analysis Service Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

Done! We added a new Analysis Service content item logged in as contributor.

Finally, let's login back as manager.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)


