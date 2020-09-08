# task.py

import time, os
from celery import Celery, Task
import asyncio
from pyspark.sql import Row
from pyspark.ml.clustering import KMeans,KMeansModel
from pyspark.mllib.clustering import StreamingKMeans, StreamingKMeansModel
from pyspark.streaming import StreamingContext
from pyspark.ml.linalg import Vectors
from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession
from pyspark.sql import SQLContext
from pyspark import sql
from numpy import array
from pyspark.sql import Row
import csv
from pprint import pprint

class StreamingIrisCluster():
    def __init__(self):
        self._init_sparkcontext()

        self._model_path = "./kmeans_model_streaming"
        self._kmeans_model = None
        #self._init_model()

    def create_streaming_kmeans(self, k):
        stkm = StreamingKMeans(decayFactor=0.5, k=k)
        stkm.setRandomCenters(1, 1.0, 1)

        self._stkm = stkm

    def train(self):
        ds = self._get_train_ds()

        print("train start")
        self._stkm.trainOn(ds)
        print("train over")

        predict_stream = self._stkm.predictOn(ds)

        predict_results = []

        def collect(rdd):
            rdd_collect = rdd.collect()
            if rdd_collect:
                print(rdd_collect)
                predict_results.append(rdd_collect)

        predict_stream.foreachRDD(collect)

        self._ssc.start()
        self._ssc.awaitTermination()

        time.sleep(300)

    def predict(self, one_features):
        print("enter predict")

        return

    def _init_sparkcontext(self):
        spark_conf = SparkConf().setAppName("iris_model_streaming")
        sc = SparkContext(conf=spark_conf)
        sc.setLogLevel("ERROR")

        ssc = StreamingContext(sc, 1)
        ssc.checkpoint(".")

        self._sc = sc
        self._ssc = ssc

    def _get_train_ds(self):
        # Since decay factor is set to zero, once the first batch
        # is passed the clusterCenters are updated to [-0.5, 0.7]
        # which causes 0.2 & 0.3 to be classified as 1, even though the
        # classification based in the initial model would have been 0
        # proving that the model is updated.
        batches = [[[-0.5], [0.6], [0.8]], [[0.2], [-0.1], [0.3]]]
        batches = [self._sc.parallelize(batch) for batch in batches]
        input_stream = self._ssc.queueStream(batches)

        return input_stream


def main():
    iris_cluster = StreamingIrisCluster()

    iris_cluster.create_streaming_kmeans(2)

    iris_cluster.train()


if __name__ == '__main__':
    print("Start Online Learning Process ...")

    main()

