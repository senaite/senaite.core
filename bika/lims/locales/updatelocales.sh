#!/bin/sh

PLONEPRODUCTS="/home/cb/Plone413/buildout-cache/eggs"
I18NDUDE="/home/cb/Plone413/zinstance/bin/i18ndude"

##
## Domain: 'plone'
##
##
## Search all translations in 'plone' domain and rebiuld a new catalog
#i18ndude rebuild-pot --exclude build --pot "i18ndude-plone.pot" \
#                     --create plone "../"
##
## Filter out all msgids that are already translated in PloneTranslations
#i18ndude filter "i18ndude-plone.pot" \
#                "${PLONEPRODUCTS}/PloneTranslations/i18n/plone.pot" > "filtered-plone.pot"
##
## Merge generated file with manual maintained pot file then with the current catalog
#i18ndude merge --pot "${POPREFIX}-plone.pot" \
#               --merge "filtered-plone.pot" \
#               --merge2 "manual-plone.pot"
##
## Cleaning
#rm "filtered-plone.pot" "i18ndude-plone.pot"
##
## Refresh po files for 'plone' domain
#i18ndude sync --pot "${POPREFIX}-plone.pot" \
#                    "${POPREFIX}-plone-fr.po" "${POPREFIX}-plone-en.po"


$I18NDUDE rebuild-pot --exclude build --pot "i18ndude.pot" --create bika ".."
$I18NDUDE merge --pot "bika.pot" --merge "i18ndude.pot" --merge2 "manual.pot"
rm "i18ndude.pot"

$I18NDUDE sync --pot "bika.pot" \
                    "en/LC_MESSAGES/bika.po" \
                    "af/LC_MESSAGES/bika.po" \
                    "zh/LC_MESSAGES/bika.po" \
                    "nl/LC_MESSAGES/bika.po" \
                    "de/LC_MESSAGES/bika.po" \
                    "pt/LC_MESSAGES/bika.po" \
                    "es/LC_MESSAGES/bika.po" \

echo "#########################################################"
echo "##"
echo "## untranslated messages summary report"
echo
$I18NDUDE find-untranslated ..

tx pull -a
tx push -t

exit 0
