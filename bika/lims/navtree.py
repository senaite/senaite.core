from plone.app.portlets.portlets.navigation import Renderer
from bika.lims import PMF

def createNavTree(self):
    """see ./configure.zcml
    This chops translated strings (from plone domain) into navtree titles.
    Only goes 2 levels down the tree.
    """
    data = self.getNavTree()

    q = ["data['children']"]
    while q:
        for i in range(len(eval(q[0]))):
            try:
                exec("%s[%s]['Title'] = "
                     "self.context.translate(PMF(%s[%s]['Title']))" %(
                         q[0], i, q[0], i))
            except:
                pass
            if eval("%s[%s]" % (q[0], i)).get('children', []):
                q.append(q[0] + "[%s]['children']"%i)
        del(q[0])

    bottomLevel = self.data.bottomLevel \
        or self.properties.getProperty('bottomLevel', 0)

    return self.recurse(children=data['children'],
                        level=1,
                        bottomLevel=bottomLevel)
