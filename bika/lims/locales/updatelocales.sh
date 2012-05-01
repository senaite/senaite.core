I18NDUDE=~/Plone414/zinstance/bin/i18ndude
PLONE_POT=~/Plone414/zinstance/parts/omelette/plone/app/locales/locales/plone.pot

echo Pull transifex
tx pull -a -f

echo Building bika
$I18NDUDE rebuild-pot --pot bika.pot --exclude "build" --create bika --merge bika-manual.pot ..
echo Syncing bika
$I18NDUDE sync --pot bika.pot */LC_MESSAGES/bika.po

echo Building plone
$I18NDUDE rebuild-pot --pot i18ndude.pot --create plone --merge plone-manual.pot ../profiles/
echo Filtering plone
$I18NDUDE filter i18ndude.pot $PLONE_POT > plone.pot
echo Syncing plone
$I18NDUDE sync --pot plone.pot */LC_MESSAGES/plone.po
rm i18ndude.pot

echo Push transifex
tx push -s -t

echo "#########################################################"
echo "## untranslated messages"
echo
$I18NDUDE find-untranslated -n ..
