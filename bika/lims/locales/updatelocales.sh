#!/bin/bash
I18NDUDE=~/Plone/zinstance/bin/i18ndude

### Grab new translated strings
# tx pull -a

find . -name "*.mo" -delete

### bika domain
### ===========
$I18NDUDE rebuild-pot --pot bika.pot --exclude "build" --create bika ..
$I18NDUDE merge --pot bika.pot --merge bika-manual.pot
$I18NDUDE sync --pot bika.pot */LC_MESSAGES/bika.po

### plone domain
### ============
PLONE_POT=~/Plone/zinstance/parts/omelette/plone/app/locales/locales/plone.pot
$I18NDUDE rebuild-pot --pot i18ndude.pot --create plone ../profiles/
$I18NDUDE filter i18ndude.pot $PLONE_POT > plone.pot
$I18NDUDE merge --pot plone.pot --merge plone-manual.pot
$I18NDUDE sync --pot plone.pot */LC_MESSAGES/plone.po
rm i18ndude.pot

for po in `find . -name "*.po"`; do msgfmt -o ${po/%po/mo} $po; done

### push new strings to transifex
# tx push -s -t

