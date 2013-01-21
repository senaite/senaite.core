### buildout for development

You can copy development-buildout.cfg into your zinstance folder, then run:

    $ bin/buildout -c development-buildout.cfg

If filestorage files have been deleted/recreated, you may need to re-create
the admin user:

    $ bin/plonectl adduser admin <password>

If you don't have a mail server configured, you can use this command to start
a simple printing debug SMTP server:

    $ python -m smtpd -n -c DebuggingServer localhost:1025

In debug mode a copy of the HTML that is meant to be included in the email when
publishing, will be written to zinstance/parts/instance/var/*.html

### Updating PO files from Transifex:

Install the transifex-client (tx).  Visit http://www.transifex.net/ for
more information.

Alternatively, download the PO files for your language directly from Transifex,
and replace them in the bika/lims/locales folder.

### Re-compiling PO to MO

There should be configuration in buildout.cfg to re-compile the PO files,
though sometimes it's necessary to compile them yourself:

    $ cd bika/lims/locales
    $ for po in `find . -name "*.po"`;do sudo msgfmt -o ${po/%po/mo} $po; done

### Dates/Times

The plonelocales msgids (date_format_long, date_format_short,
date_format_short_datepicker) exist also in the bika domain.
This is the one that the bika functions use.  By default it's
configured to %Y-%m-%d %I:%M %p.
