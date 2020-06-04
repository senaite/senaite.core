===================
Action Handler Pool
===================

The `ActionHandlerPool` is a singleton instance to increase performance by
postponing reindexing operations for objects.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t ActionHandlerPool

Test Setup
==========

Needed Imports:

    >>> from bika.lims.workflow import ActionHandlerPool


Testing
=======

Getting an instance of the action handler pool:

    >>> pool = ActionHandlerPool.get_instance()

    >>> pool
    <ActionHandlerPool for UIDs:[]>

When a piece of code is utilizing the utility function `doActionFor`,
the pool is utilized to increase the performance by

  - avoiding the same transition to be multiple times
  - postponing the reindexing to the end of the process

For this to work, each calling function needs to call `queue_pool()`
to postpone (eventual) multiple reindex operation:

    >>> pool.queue_pool()

This will *increase* the internal `num_calls` counter:

    >>> pool.num_calls
    1

If all operations are done by the calling code, it has to call `resume()`, which
will decrease the counter by 1:

    >>> pool.resume()

This will *decrease* the internal `num_calls` counter:

    >>> pool.num_calls
    0

Multiple calls to `resume()` should not lead to a negative counter:

    >>> for i in range(10):
    ...     pool.resume()

    >>> pool.num_calls
    0

Because the `ActionHandlerPool` is a singleton, we must ensure that it is thread safe.
This means that concurrent access to this counter must be protected.

To simulate this, we will need to simulate concurrent calls to `queue_pool()`,
which will add some lag in between the reading and writing operation.


    >>> import random
    >>> import threading
    >>> import time

    >>> threads = []

    >>> def simulate_queue_pool(tid):
    ...     pool.queue_pool()
    ...     time.sleep(random.random())

    >>> for num in range(100):
    ...     t = threading.Thread(target=simulate_queue_pool, args=(num, ))
    ...     threads.append(t)
    ...     t.start()

    >>> for t in threads:
    ...     t.join()
