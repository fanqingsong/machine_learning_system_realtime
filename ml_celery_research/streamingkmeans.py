
from pyspark import SparkConf, SparkContext
from pyspark.mllib.clustering import StreamingKMeans, StreamingKMeansModel
from pyspark.streaming import StreamingContext
import time


spark_conf = SparkConf().setAppName("iris_model")
sc = SparkContext(conf=spark_conf)
sc.setLogLevel("ERROR")

ssc = StreamingContext(sc, 1)
ssc.checkpoint(".")

stkm = StreamingKMeans(decayFactor=0.0, k=2)
stkm.setInitialCenters([[0.0], [1.0]], [1.0, 1.0])

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


stkm.trainOn(input_stream)
predict_stream = stkm.predictOn(input_stream)

predict_stream.foreachRDD(collect)

ssc.start()

time.sleep(10)

ssc.stop(False)

sc.stop()