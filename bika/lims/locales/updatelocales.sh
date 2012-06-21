#!/bin/bash
I18NDUDE=~/Plone414/zinstance/bin/i18ndude
PLONE_POT=~/Plone414/zinstance/parts/omelette/plone/app/locales/locales/plone.pot

echo Pull transifex
#tx pull -a -f

# if strings are removed, and not replaced with new ones then
# these files are used to revert them after we're done here.
for x in `find . -name bika.po`; do cp -vf $x `dirname $x`/bika-backup.po; done
for x in `find . -name plone.po`; do cp -vf $x `dirname $x`/plone-backup.po; done

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

echo Checking bika for missing strings
for x in `find . -name bika-backup.po`; do
  SRC=$x;
  DEST=`dirname $x`/bika.po;
  $I18NDUDE admix $DEST $SRC > $DEST.new;
  rm $DEST
  mv $DEST.new $DEST
done

echo Checking plone for missing strings
for x in `find . -name plone-backup.po`; do
  SRC=$x;
  DEST=`dirname $x`/plone.po;
  $I18NDUDE admix $DEST $SRC > $DEST.new;
  rm $DEST
  mv $DEST.new $DEST
done

echo Merging extra strings from bika into plone
for x in `find . -name bika.po`; do
  SRC=$x;
  DEST=`dirname $x`/plone.po;
  if [ -e `dirname $x`/plone.po ]; then
  $I18NDUDE admix $DEST $SRC > $DEST.new;
  rm $DEST
  mv $DEST.new $DEST
  fi;
done

echo Merging extra strings from plone into bika
for x in `find . -name plone.po`; do
  SRC=$x;
  DEST=`dirname $x`/bika.po;
  if [ -e $DEST ]; then
  $I18NDUDE admix $DEST $SRC > $DEST.new;
  rm $DEST
  mv $DEST.new $DEST
  fi;
done

find . -name *backup.po -delete
find . -name *backup.mo -delete

echo Push transifex
#tx push -s -t

#echo "#########################################################"
#echo "## untranslated messages"
#echo
#$I18NDUDE find-untranslated -n ..
