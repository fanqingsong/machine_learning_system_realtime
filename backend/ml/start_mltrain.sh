




#!/bin/sh

MYDIR=$(cd `dirname $0`; pwd)

/usr/local/spark/bin/spark-submit $MYDIR/training_subprocess.py CN-00015440.ericsson.se:2181 1 oneIrisData 1 3


