




#!/bin/sh

MYDIR=$(cd `dirname $0`; pwd)

ROOTDIR=`dirname $MYDIR`

/usr/local/spark/bin/spark-submit $ROOTDIR/ml/streaming_kmeans_train.py CN-00015440.ericsson.se:2181 1 oneIrisData 1


