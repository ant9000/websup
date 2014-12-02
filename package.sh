#!/bin/bash

if [ "`git status --porcelain|wc -l`" != "0" ]; then
 echo "Your git repository has uncommited changes - aborting."
 exit 1
fi
VERSION=`git describe --always`
NAME=websup-git-$VERSION.tgz
echo "Git revision: $VERSION" > VERSION.txt
touch $NAME
tar zcvf $NAME -C .. websup/ \
  --exclude env \
  --exclude .git \
  --exclude .gitignore \
  --exclude package.sh \
  --exclude credentials.json \
  --exclude "*.pyc" \
  --exclude "websup-git-*.tgz"
