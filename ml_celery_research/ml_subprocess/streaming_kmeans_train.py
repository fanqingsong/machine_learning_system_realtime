from pyspark.streaming.kafka import KafkaUtils
from pyspark.mllib.clustering import StreamingKMeans, StreamingKMeansModel
from pyspark.streaming import StreamingContext
from pyspark import SparkConf, SparkContext
import json
import sys
import pickle


class MLTrainer:
    def __init__(self, zkQuorum, group, topics, numThreads, k):
        self._zkQuorum = zkQuorum
        self._group = group
        self._topics = topics
        self._numThreads = numThreads
        self._k = k

        self._init_spark()
        self._init_kafka()

    def start(self):
        self._prepare_input()
        self._set_model_on_input()
        self._set_prediction_on_input()
        self._start()

    def _init_spark(self):
        spark_conf = SparkConf().setAppName("StreamingKMeansTrain")
        sc = SparkContext(conf=spark_conf)
        sc.setLogLevel("ERROR")
        ssc = StreamingContext(sc, 5)
        # ssc.checkpoint("file:///usr/local/spark/checkpoint")
        # 这里表示把检查点文件写入分布式文件系统HDFS，所以要启动Hadoop
        ssc.checkpoint("_checkpoint")

        self._ssc = ssc

    def _init_kafka(self):
        topicAry = self._topics.split(",")

        # 将topic转换为hashmap形式，而python中字典就是一种hashmap
        topicMap = {}
        for topic in topicAry:
            topicMap[topic] = self._numThreads

        raw_ds = KafkaUtils.createStream(self._ssc, self._zkQuorum, self._group, topicMap)
        raw_ds.pprint()

        self._raw_ds = raw_ds

    def _start(self):
        self._ssc.start()
        self._ssc.awaitTermination()

    def _prepare_input(self):
        def type_trans(x):
            # print("------ now trans ------")
            # print("x:")
            # print(x)
            # print("type of x[1]:")
            # print(type(x[1]))
            # print(x[1])
            result = json.loads(x[1])
            print("one iris data:")
            print(result)

            return result

        ds = self._raw_ds.map(type_trans)
        ds.pprint()

        self._model_input = ds

    def _set_model_on_input(self):
        stkm = StreamingKMeans(decayFactor=0.5, k=self._k)
        stkm.setRandomCenters(4, 1.0, 1)

        ds = self._model_input

        print("set model on input")
        stkm.trainOn(ds)

        self._stkm = stkm

    def _set_prediction_on_input(self):
        ds = self._model_input
        stkm = self._stkm

        predict_stream = stkm.predictOn(ds)
        predict_stream.pprint()

        def save_model():
            model = stkm.latestModel()
            clusterCenters = model.centers
            clusterWeights = model.clusterWeights
            print("cluster center({})  cluster weight({})".format(clusterCenters, clusterWeights))

            sys.stdout.flush()

            modelParams = {'clusterCenters': clusterCenters, 'clusterWeights': clusterWeights}
            with open("./model.pk", 'wb') as f:
                pickle.dump(modelParams, f, pickle.HIGHEST_PROTOCOL)

        def test_model():
            with open('./model.pk', 'rb') as f:
                # The protocol version used is detected automatically, so we do not
                # have to specify it.
                data = pickle.load(f)
                print("--------- restore pickle --------")
                print(data)

                typed_model = StreamingKMeansModel(clusterCenters=data['clusterCenters'],
                                                   clusterWeights=data['clusterWeights'])

                test_data = [5.1, 3.5, 1.4, 0.2]
                test_result = typed_model.predict(test_data)
                print("test.data({}) has test.result({})".format(test_data, test_result))

        def collect(rdd):
            rdd_collect = rdd.collect()
            if rdd_collect:
                print("----- predict_stream foreach ------")
                print(rdd_collect)

                save_model()

                test_model()

        predict_stream.foreachRDD(collect)


def main():
    print("Start Online Learning Process ...")

    # 输入的四个参数分别代表着
    # 1.zkQuorum为zookeeper地址
    # 2.group为消费者所在的组
    # 3.topics该消费者所消费的topics
    # 4.numThreads开启消费topic线程的个数
    # 5.k 聚类的总数
    if (len(sys.argv) < 6):
        print("Usage: APP <zkQuorum> <group> <topics> <numThreads> <k>")
        exit(1)
    zkQuorum = sys.argv[1]
    group = sys.argv[2]
    topics = sys.argv[3]
    numThreads = int(sys.argv[4])
    k = int(sys.argv[5])
    print(group, topics)

    mltrainer = MLTrainer(zkQuorum, group, topics, numThreads, k)
    mltrainer.start()


if __name__ == '__main__':
    main()

