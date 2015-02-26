#!/usr/bin/env bash

# we make assumptions here:
# 1) i18ndude is in the path.
# 2) unifiedinstaller-style paths are used to find plone.pot.
#    this means buildout-cache/ is located relative to bika/lims/locales

i18ndude=$(which i18ndude)
CWD=$(dirname $0)
cd ${CWD}
### Always pull everything from transifex
tx pull -a -f

#########################
### bika.lims "bika" domain
DOMAIN='bika'
echo "Using ${i18ndude} for ${DOMAIN} in ${CWD}"
${i18ndude} rebuild-pot --pot ${DOMAIN}.pot --exclude '../build' --merge ${DOMAIN}-manual.pot --create ${DOMAIN} ..
### Synchronise the .pot with the templates.
echo "Sync .po files for ${DOMAIN}"
for po in */LC_MESSAGES/${DOMAIN}.po;do
    ${i18ndude} sync --pot ${DOMAIN}.pot $po
done


####################################
### bika.lims "plone" domain overrides
### This only scans for messages in ../profiles folder
### XXX This should also learn to scan for _p() in ..
DOMAIN='plone'
echo "Using ${i18ndude} for ${DOMAIN} in ${CWD}"
${i18ndude} rebuild-pot --pot ${DOMAIN}.pot --exclude '../build' --merge ${DOMAIN}-manual.pot --create ${DOMAIN} ../profiles
${buildout:directory}/parts/omelette/plone/app/locales/locales/plone.pot
### Synchronise the .pot with the templates.
echo "Sync .po files for ${DOMAIN}"
for po in */LC_MESSAGES/${DOMAIN}.po;do
    ${i18ndude} sync --pot ${DOMAIN}.pot $po
done

first we get our bika.lims plone overrides, with -manual merged.
Then we apply-first, ours then theirs.
done.
