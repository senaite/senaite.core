#!/bin/bash
I18NDUDE=~/Plone414/zinstance/bin/i18ndude
PLONE_POT=~/Plone414/zinstance/parts/omelette/plone/app/locales/locales/plone.pot

#tx pull -a -f

# if strings are removed, and not replaced with new ones then
# these files are used to revert them after we're done here.
for x in `find . -name bika.po`; do cp -vf $x `dirname $x`/bika-backup.po; done
for x in `find . -name plone.po`; do cp -vf $x `dirname $x`/plone-backup.po; done
$I18NDUDE rebuild-pot --pot bika.pot --exclude "build" --create bika ..
$I18NDUDE merge --pot bika.pot --merge bika-manual.pot
$I18NDUDE sync --pot bika.pot */LC_MESSAGES/bika.po
for x in `find . -name bika-backup.po`; do
  SRC=$x;
  DEST=`dirname $x`/bika.po;
  $I18NDUDE admix $DEST $SRC > $DEST.new;
  rm $DEST
  mv $DEST.new $DEST
done

$I18NDUDE rebuild-pot --pot i18ndude.pot --create plone ../profiles/
$I18NDUDE filter i18ndude.pot $PLONE_POT > plone.pot
$I18NDUDE merge --pot plone.pot --merge plone-manual.pot
$I18NDUDE sync --pot plone.pot */LC_MESSAGES/plone.po
for x in `find . -name plone-backup.po`; do
  SRC=$x;
  DEST=`dirname $x`/plone.po;
  $I18NDUDE admix $DEST $SRC > $DEST.new;
  rm $DEST
  mv $DEST.new $DEST
done
rm i18ndude.pot

find . -name *backup.po -delete
find . -name *backup.mo -delete

#tx push -s -t

#$I18NDUDE find-untranslated -n ..
