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

# 实例化一个Celery
broker = 'redis://localhost:6379/1'
backend = 'redis://localhost:6379/2'

# 参数1 自动生成任务名的前缀
# 参数2 broker 是我们的redis的消息中间件
# 参数3 backend 用来存储我们的任务结果的
app = Celery('iris_cluster_streaming', broker=broker, backend=backend)

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


iris_cluster = StreamingIrisCluster()

@app.task()
def train(k):
    print('Enter train function ...')
    iris_cluster.create_streaming_kmeans(k)
    iris_cluster.train()

    return 0

@app.task()
def predict(one_features):
    print('Enter predict function ...')
    #result = iris_cluster.predict(one_features)

    return result



def sync_call():
    iris_cluster.create_streaming_kmeans(2)
    iris_cluster.train()


if __name__ == '__main__':
    # 这里生产的任务不可用，导入的模块不能包含task任务。会报错
    print("Start Task ...")

    #sync_call()

    '''
    after runing celery mode, the result is fail in celery
    so we move to kafka mode
    '''
    r = train.delay(2)
    print("r=", r.get())
    #
    # one_feature = [5.1, 3.5, 1.4, 0.2]
    # r = predict.delay(one_feature)
    # print(one_feature, ", cluster=", r.get())


    time.sleep(20)
    #
    # # https://docs.celeryproject.org/en/4.0/whatsnew-4.0.html#asyncresult-then-on-success-on-error
    # # https://docs.telethon.dev/en/latest/concepts/asyncio.html
    # loop = asyncio.get_event_loop()  # get the default loop for the main thread
    # try:
    #     # run the event loop forever; ctrl+c to stop it
    #     # we could also run the loop for three seconds:
    #     #     loop.run_until_complete(asyncio.sleep(3))
    #     loop.run_forever()
    # except KeyboardInterrupt:
    #     pass

    print("End Task ...")

