#!/bin/sh

MYDIR=$(cd `dirname $0`; pwd)

ROOTDIR=`dirname $MYDIR`

python ml/streaming_kmeans_train.py CN-00015440.ericsson.se:2181 1 oneIrisData 1
