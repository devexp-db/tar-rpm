#!/bin/sh

rm -rf tar && \
git clone git://git.savannah.gnu.org/tar.git  && \
pushd tar && \
./bootstrap && \
./configure && \
make dist

