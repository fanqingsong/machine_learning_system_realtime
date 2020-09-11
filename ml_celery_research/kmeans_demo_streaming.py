from pyspark import SparkConf, SparkContext
from pyspark.mllib.clustering import StreamingKMeans, StreamingKMeansModel
from pyspark.streaming import StreamingContext
import time, os, shutil
import requests, json

import pickle


spark_conf = SparkConf().setAppName("iris_model_streaming_test")
sc = SparkContext(conf=spark_conf)
sc.setLogLevel("ERROR")

ssc = StreamingContext(sc, 1)
ssc.checkpoint(".")

stkm = StreamingKMeans(decayFactor=0.5, k=2)
#stkm.setInitialCenters([[0.0], [1.0]], [1.0, 1.0])
stkm.setRandomCenters(1, 1.0, 1)

# Since decay factor is set to zero, once the first batch
# is passed the clusterCenters are updated to [-0.5, 0.7]
# which causes 0.2 & 0.3 to be classified as 1, even though the
# classification based in the initial model would have been 0
# proving that the model is updated.
batches = [[[-0.5], [0.6], [0.8]], [[0.2], [-0.1], [0.3]]]
batches = [sc.parallelize(batch) for batch in batches]
input_stream = ssc.queueStream(batches)


predict_results = []

def collect(rdd):
    rdd_collect = rdd.collect()
    if rdd_collect:
        print(rdd_collect)
        predict_results.append(rdd_collect)

        model = stkm.latestModel()
        clusterCenters = model.centers
        clusterWeights = model.clusterWeights
        print("cluster center({})  cluster weight({})".format(clusterCenters, clusterWeights))

        modelParams = {'clusterCenters':clusterCenters, 'clusterWeights':clusterWeights}
        with open("./model.pk", 'wb') as f:
            pickle.dump(modelParams, f, pickle.HIGHEST_PROTOCOL)

        with open('./model.pk', 'rb') as f:
            # The protocol version used is detected automatically, so we do not
            # have to specify it.
            data = pickle.load(f)
            print("--------- restore pickle --------")
            print(data)

            typed_model = StreamingKMeansModel(clusterCenters=data['clusterCenters'],
                                               clusterWeights=data['clusterWeights'])

            test_data = [0.5]
            test_result = typed_model.predict(test_data)
            print("test.data({}) has test.result({})".format(test_data, test_result))




stkm.trainOn(input_stream)

predict_stream = stkm.predictOn(input_stream)

predict_stream.pprint()

predict_stream.foreachRDD(collect)

ssc.start()

time.sleep(3)

print("------------------------- after sleep --------")
model = stkm.latestModel()
typed_model = StreamingKMeansModel(clusterCenters=model.centers, clusterWeights=model.clusterWeights)

test_data = [0.5]
test_result = typed_model.predict(test_data)
print("test.data({}) has test.result({})".format(test_data, test_result))


'''
StreamingKMeansModel inherits KMeansModel
save method belongs to KMeansModel, so it doesn't treat StreamingKMeansModel part
only care its own part
'''
# shutil.rmtree("./kmeans_model_streaming")
# typed_model.save(sc, "./kmeans_model_streaming")
#
# print("---------- typed centers --------")
# print(typed_model.clusterCenters)
#
# print("---------- typed weights --------")
# print(typed_model.clusterWeights)


'''
StreamingKMeansModel inherits KMeansModel
load method belongs to KMeansModel, so it doesn't treat StreamingKMeansModel part
and return a new KMeansModel, don't affect StreamingKMeansModel instance
'''
# restored_model = StreamingKMeansModel([[0.0], [1.0]], [1.0, 1.0])
# restored_model.load(sc, "./kmeans_model_streaming")
#
# print("---------- restored centers --------")
# print(restored_model.clusterCenters)
#
# print("---------- restored weights --------")
# print(restored_model.clusterWeights)


ssc.awaitTermination()


ssc.stop(False)

sc.stop()