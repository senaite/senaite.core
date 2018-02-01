.. figure:: https://raw.githubusercontent.com/senaite/senaite.core/master/bika/lims/skins/bika/senaite-core-logo.png
   :width: 500px
   :alt: senaite.core
   :align: center

— **SENAITE.CORE**: *the heart of SENAITE.LIMS, the evolution of Bika LIMS*

.. image:: https://img.shields.io/pypi/v/senaite.core.svg?style=flat-square
    :target: https://pypi.python.org/pypi/senaite.core

.. image:: https://img.shields.io/travis/senaite/senaite.core/master.svg?style=flat-square
    :target: https://travis-ci.org/senaite/senaite.core

.. image:: https://img.shields.io/scrutinizer/g/senaite/senaite.core/master.svg?style=flat-square
    :target: https://scrutinizer-ci.com/g/senaite/senaite.core/

.. image:: https://img.shields.io/github/issues-pr/senaite/senaite.core.svg?style=flat-square
    :target: https://github.com/senaite/senaite.core/pulls

.. image:: https://img.shields.io/github/issues/senaite/senaite.core.svg?style=flat-square
    :target: https://github.com/senaite/senaite.core/issues

.. image:: https://img.shields.io/github/contributors/senaite/senaite.core.svg?style=flat-square
    :target: https://github.com/senaite/senaite.core/blob/master/CONTRIBUTORS.rst


Introduction
============

SENAITE.CORE is an Open Source Laboratory Information Management System (LIMS)
for enterprise environments, especially focused to behave with high speed,
excellent performance and good stability.

This software is a derivative work of BikaLIMS_
software and comes with the same user interface. Since SENAITE.CORE provides the
core functionalities and entities used by `SENAITE.LIMS <https://github.com/senaite/senaite.lims>`_,
the installation of the latter is strongly recommended for an optimal user
experience.


Installation
============

SENAITE.CORE is built on top of `Plone CMS <https://plone.org>`_, so it must be
installed first.
Please, follow the `installation instructions for Plone 4.x <https://docs.plone.org/4/en/manage/installing/installation.html>`_
first.

Once Plone 4.x is installed successfully, you can choose any of the two options
below:

Ready-to-go installation
------------------------
With this installation modality, the sources from ``senaite.core`` will be
downloaded automatically from `Python Package Index (Pypi) <https://pypi.python.org/pypi/senaite.core>`_.
If you want the latest code from the `source code repository <https://github.com/senaite/senaite.core>`_,
follow the `installation instructions for development <https://github.com/senaite/senaite.core/blob/master/README.rst#installation-for-development>`_.

Create a new buildout file ``senaite.cfg`` which extends your existing
``buildout.cfg`` – this way you can easily keep development stuff separate from
your main buildout.cfg which you can also use on the production server::

  [buildout]
  index = https://pypi.python.org/simple
  extends = buildout.cfg

  [instance]
  eggs +=
      senaite.core

Note that with this approach you do not need to modify the existing buildout.cfg
file.

Then build it out with this special config file::

  bin/buildout -c senaite.cfg

and buildout will automatically download and install all required dependencies.

For further details about Buildout and how to install add-ons for Plone, please check
`Installing add-on packages using Buildout from Plone documentation <https://docs.plone.org/4/en/manage/installing/installing_addons.html>`_.


Installation for development
----------------------------

This is the recommended approach how to enable ``senaite.core`` for your
development environment. With this approach, you'll be able to download the
latest source code from `senaite.core's repository <https://github.com/senaite/senaite.core>`_
and contribute as well.

Use git to fetch ``senaite.core`` source code to your buildout environment::

  cd src
  git clone git://github.com/senaite/senaite.core.git senaite.core

Create a new buildout file ``senaite.cfg`` which extends your existing
``buildout.cfg`` – this way you can easily keep development stuff separate
from your main buildout.cfg which you can also use on the production server.

``senaite.cfg``::

  [buildout]
  index = https://pypi.python.org/simple
  extends = buildout.cfg
  develop +=
      src/senaite.core

  [instance]
  eggs +=
      senaite.core

Note that with this approach you do not need to modify the existing buildout.cfg
file.

Then build it out with this special config file::

  bin/buildout -c senaite.cfg

and buildout will automatically download and install all required dependencies.


Contribute
==========

We want contributing to SENAITE.CORE to be fun, enjoyable, and educational for
anyone, and everyone. This project adheres to the `Contributor Covenant <https://github.com/senaite/senaite.core/blob/master/CODE_OF_CONDUCT.md>`_.
By participating, you are expected to uphold this code. Please report
unacceptable behavior.

Contributions go far beyond pull requests and commits. Although we love giving
you the opportunity to put your stamp on SENAITE.CORE, we also are thrilled to
receive a variety of other contributions. Please, read `Contributing to senaite.core
document <https://github.com/senaite/senaite.core/blob/master/CONTRIBUTING.md>`_.


Feedback and support
====================

* `Gitter channel <https://gitter.im/senaite/Lobby>`_
* `Users list <https://sourceforge.net/projects/senaite/lists/senaite-users>`_


License
=======
SENAITE.CORE
Copyright (C) 2018 Senaite Foundation

This software, henceforth "SENAITE.CORE", an add-on for
`Plone software <https://plone.org/>`_, is a derivative work of BIKALIMS_.

This program is free software; you can redistribute it and/or
modify it under the terms of the `GNU General Public License version 2 <./LICENSE>`_ as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

SENAITE.CORE uses third party libraries that are distributed under their own
terms (see LICENSE-3RD-PARTY.rst)


.. Links

.. _BIKALIMS: https://github.com/bikalims/bika.lims
