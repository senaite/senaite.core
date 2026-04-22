Dashboard
=========

The unified SENAITE dashboard combines a personalized greeting,
status overview, quick action links, and detailed statistics into
a single view at ``/senaite-dashboard``.


Sections
--------

The dashboard renders in three tiers:

1. **Greeting and status cards** -- personalized welcome with the
   user's full name, current date/time, and permission-gated status
   cards showing sample/worksheet counts.

2. **Quick action links** -- role-aware navigation shortcuts
   (Register Samples, Worksheets, Verify, Publish, Setup).

3. **Statistics sections** -- detailed breakdown by workflow state
   with evolution bar charts. Only visible to users with the
   ``senaite.core: View Dashboard`` permission.


Permissions
-----------

``senaite.core: View Dashboard``
    Controls visibility of the statistics sections (Samples,
    Analyses, Worksheets panels with charts). Granted by default
    to LabClerk, LabManager, and Manager via ``rolemap.xml``.

The status cards and quick action links use individual permissions
(e.g., ``TransitionReceiveSample``, ``TransitionVerify``,
``EditResults``, ``AddAnalysisRequest``, ``ManageBika``) to
determine which cards and links each user sees.


Async Loading
-------------

The dashboard page skeleton (greeting, quick links, section
headings) renders immediately without database queries. Status
cards and statistics sections load asynchronously via the
``@@senaite-dashboard-data`` JSON endpoint.

Each section is fetched independently, so slow queries in one
section do not block the others.


Caching
-------

Search counts use ``@ram.cache`` with a 5-minute TTL, shared
across all users and requests. The cache key includes the full
query and catalog name, so different filters ("mine" vs "all")
produce separate cache entries.

Evolution chart data is cached for 2 hours.


Files
-----

``dashboard.py``
    View classes: ``DashboardView`` (main page) and
    ``DashboardDataView`` (JSON endpoint).

``templates/dashboard.pt``
    Page template with async JS loading.

``static/css/dashboard.css``
    Styles for bar charts and statistics panels.

``static/js/dashboard.js``
    Async loading, DOM rendering, D3 bar charts.

``configure.zcml``
    View and resource registrations.
