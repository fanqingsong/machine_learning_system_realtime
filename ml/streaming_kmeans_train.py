# task.py

from kafka import KafkaProducer
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark import SparkConf, SparkContext
import json
import sys


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


def train(ds):
    stkm = StreamingKMeans(decayFactor=0.5, k=2)
    stkm.setRandomCenters(1, 1.0, 1)

    print("train start")
    stkm.trainOn(ds)
    print("train over")

    predict_stream = stkm.predictOn(ds)
    predict_stream.pprint()

    predict_results = []

    def collect(rdd):
        rdd_collect = rdd.collect()
        if rdd_collect:
            print("predict_stream foreach")
            print(rdd_collect)
            predict_results.append(rdd_collect)

    predict_stream.foreachRDD(collect)


def ml_train(zkQuorum, group, topics, numThreads):
    spark_conf = SparkConf().setAppName("StreamingKmeansTrain")
    sc = SparkContext(conf=spark_conf)
    sc.setLogLevel("ERROR")
    ssc = StreamingContext(sc, 5)
    # ssc.checkpoint("file:///usr/local/spark/checkpoint")
    # 这里表示把检查点文件写入分布式文件系统HDFS，所以要启动Hadoop
    ssc.checkpoint("_checkpoint")
    topicAry = topics.split(",")
    # 将topic转换为hashmap形式，而python中字典就是一种hashmap
    topicMap = {}
    for topic in topicAry:
        topicMap[topic] = numThreads
    rawds = KafkaUtils.createStream(ssc, zkQuorum, group, topicMap)
    rawds.pprint()

    def type_trans(x):
        # print("------ now trans ------")
        # print("x:")
        # print(x)
        # print("type of x[1]:")
        # print(type(x[1]))
        # print(x[1])
        result = float(x[1])
        # print("result:")
        # print(result)

        result = [result]
        return result

    #ds = rawds.map(lambda x: x[1])

    ds = rawds.map(type_trans)
    ds.pprint()

    train(ds)

    ssc.start()
    ssc.awaitTermination()


if __name__ == '__main__':
    print("Start Online Learning Process ...")

    # 输入的四个参数分别代表着
    # 1.zkQuorum为zookeeper地址
    # 2.group为消费者所在的组
    # 3.topics该消费者所消费的topics
    # 4.numThreads开启消费topic线程的个数
    if (len(sys.argv) < 5):
        print("Usage: KafkaWordCount <zkQuorum> <group> <topics> <numThreads>")
        exit(1)
    zkQuorum = sys.argv[1]
    group = sys.argv[2]
    topics = sys.argv[3]
    numThreads = int(sys.argv[4])
    print(group, topics)
    ml_train(zkQuorum, group, topics, numThreads)


