#!/bin/sh

I18NDUDE="/home/cb/Plone413/zinstance/bin/i18ndude"

tx pull -a -f

$I18NDUDE rebuild-pot --exclude build --pot "i18ndude.pot" --create bika ".."
$I18NDUDE merge --pot "bika.pot" --merge "i18ndude.pot" --merge2 "manual.pot"
rm "i18ndude.pot"

$I18NDUDE sync --pot "bika.pot" \
                    "af/LC_MESSAGES/bika.po" \
                    "bn/LC_MESSAGES/bika.po" \
                    "ca/LC_MESSAGES/bika.po" \
                    "de/LC_MESSAGES/bika.po" \
                    "el/LC_MESSAGES/bika.po" \
                    "en/LC_MESSAGES/bika.po" \
                    "es/LC_MESSAGES/bika.po" \
                    "fr/LC_MESSAGES/bika.po" \
                    "hi/LC_MESSAGES/bika.po" \
                    "id/LC_MESSAGES/bika.po" \
                    "it/LC_MESSAGES/bika.po" \
                    "ja/LC_MESSAGES/bika.po" \
                    "kn/LC_MESSAGES/bika.po" \
                    "nl/LC_MESSAGES/bika.po" \
                    "pl/LC_MESSAGES/bika.po" \
                    "pt/LC_MESSAGES/bika.po" \
                    "ta/LC_MESSAGES/bika.po" \
                    "ur/LC_MESSAGES/bika.po" \
                    "zh/LC_MESSAGES/bika.po" \
                    "zh_CN/LC_MESSAGES/bika.po"

echo "#########################################################"
echo "##"
echo "## untranslated messages summary report"
echo
$I18NDUDE find-untranslated ..

tx push -s -t

exit 0
