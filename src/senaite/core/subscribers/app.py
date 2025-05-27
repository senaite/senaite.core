from OFS.Application import import_product


def databaseOpenedWithRootHandler(event):
    # db = event.database
    path = "/Products"
    import sys
    sys.path.append("/Users/rbartl/develop/buildout/addons")
    import_product(path, "addon")
