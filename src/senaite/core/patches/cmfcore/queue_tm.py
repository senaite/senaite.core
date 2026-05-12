# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301 USA.
#
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from Products.CMFCore.indexing import processing


def before_commit(self):
    """Patched before_commit with re-entrancy guard.

    The original QueueTM.before_commit calls queue.process() without
    adding the queue to the `processing` set. This allows recursive
    calls to processQueue() (triggered by catalog queries inside
    processors) to re-enter process(), causing double indexing and
    UUIDIndex errors.

    This patch adds the same guard that processQueue() uses.
    """
    if self.queue not in processing:
        try:
            processing.add(self.queue)
            self.queue.process()
        finally:
            processing.remove(self.queue)
    self.queue.clear()
