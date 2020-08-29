from pyspark.sql import Row
from pyspark.ml.clustering import KMeans,KMeansModel
from pyspark.ml.linalg import Vectors
from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession
from pyspark.sql import SQLContext
from pyspark import sql

spark_conf = SparkConf().setAppName("iris_model")
sc = SparkContext(conf=spark_conf)
sqlContext = sql.SQLContext(sc)
sc.setLogLevel("ERROR")

rawData = sc.textFile("file:///root/win10/mine/machine_learning_system_on_spark/ml_celery_research/iris.txt")
def f(x):
    rel = {}
    rel['features'] = Vectors.dense(float(x[0]),float(x[1]),float(x[2]),float(x[3]))
    return rel
 
df = rawData.map(lambda line: line.split(',')).map(lambda p: Row(**f(p))).toDF()

kmeans = KMeans()

kmeans.setK(3).setFeaturesCol('features').setPredictionCol('prediction')

kmeansmodel = kmeans.fit(df)

# kmeans_path = "./kmeans"
# kmeans.save(kmeans_path)
# kmeans2 = KMeans.load(kmeans_path)
# kmeans2.getK()

model_path = "./kmeans_model"
kmeansmodel.write().overwrite().save(model_path)
model2 = KMeansModel.load(model_path)

print("----------- classified result ---------")
transformed = kmeansmodel.transform(df)
results = transformed.collect()
for item in results:
    print(str(item[0])+' is predcted as cluster'+ str(item[1]))


print("----------- cluster centroid ---------")
results2 = kmeansmodel.clusterCenters()
for item in results2:
    print(item)

#kmeansmodel.computeCost(data)


