#!/bin/bash

NAME=websup-git-`git describe --always`.tgz
touch $NAME
tar zcvf $NAME -C .. websup/ \
  --exclude env \
  --exclude .git \
  --exclude .gitignore \
  --exclude package.sh \
  --exclude "websup-git-*.tgz"
