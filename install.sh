#!/bin/bash
set -e

me=$BASH_SOURCE
while [ -L "$me" ]; do me=$(file -- "$me"|cut -f2 -d\`|cut -f1 -d\'); done
#'
BASE="`cd -P -- "$(dirname -- "$me")" && pwd -P`"
cd $BASE

virtualenv env
. env/bin/activate
pip install -U pip
pip install -r requirements.txt 
cat<<MSG
############################
Setup completed. To run the test app, use

   cd $BASE
   . env/bin/activate
   ./app.py

MSG
