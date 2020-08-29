from __future__ import absolute_import, unicode_literals
from celery import shared_task
import time, os
from pyspark.ml.clustering import KMeans,KMeansModel
from pyspark.ml.linalg import Vectors
from pyspark import SparkConf, SparkContext
from pyspark.sql import SQLContext
from pyspark.sql import Row
import csv
from pprint import pprint


class IRIS_Cluster():
    def __init__(self):
        self._init_sparkcontext()

        self._model_path = "./kmeans_model"
        self._kmeans_model = None
        self._init_model()

    def train(self, k, train_data):
        print("enter train")

        kmeans = self._get_kmeans_instance(k)

        df = self._get_train_df(train_data)

        kmeansmodel = kmeans.fit(df)

        self._kmeans_model = kmeansmodel
        self._save_model()

        self._print_after_train(df)

        train_fit_df = self._get_train_fit_df(df)
        train_fit_data = self._get_train_fit_data(train_fit_df)

        return train_fit_data

    def predict(self, one_features):
        print("enter predict")

        if self._kmeans_model == None:
            print("no model, train first.")
            return

        df = self._get_predict_df(one_features)

        transformed = self._kmeans_model.transform(df)
        transformed.show()
        results = transformed.collect()
        print(results)

        predicted_cluster = None

        for item in results:
            print(str(item[0]) + ' is predcted as cluster' + str(item[1]))
            predicted_cluster = item[1]

        return predicted_cluster

    def _init_sparkcontext(self):
        spark_conf = SparkConf().setAppName("iris_cluster")

        sc = SparkContext(conf=spark_conf)
        sc.setLogLevel("ERROR")

        self._sparkcontext = sc

        self._sqlcontext = SQLContext(sc)

    def _get_predict_df(self, one_features):
        Features = Row('features')
        one_feature = Features(Vectors.dense(one_features))
        data = [one_feature]
        df = self._sqlcontext.createDataFrame(data)

        return df

    def _get_train_df(self, train_data):
        if not train_data:
            print("train_data must be inputed")

        Features = Row('features')

        data = []
        for one_data in train_data:
            one_features = Features(Vectors.dense(one_data))
            data.append(one_features)

        df = self._sqlcontext.createDataFrame(data)

        df.show()

        return df

    def _get_kmeans_instance(self, k):
        kmeans = KMeans()

        kmeans.setK(k).setFeaturesCol('features').setPredictionCol('prediction')

        return kmeans

    def _save_model(self):
        model_path = self._model_path
        self._kmeans_model.write().overwrite().save(model_path)

    def _init_model(self):
        model_path = self._model_path
        if os.path.exists(model_path):
            self._kmeans_model = KMeansModel.load(model_path)

    def _get_train_fit_df(self, df):
        kmeansmodel = self._kmeans_model
        transformed = kmeansmodel.transform(df)
        results = transformed.collect()

        print("----------- train collect result ---------")
        print(results)

        print("----------- train fit data ---------")
        for item in results:
            print(item)
            print(str(item[0]) + ' is predcted as cluster' + str(item[1]))

        return results

    def _get_train_fit_data(self, train_fit_df):
        print("----- enter get train fit data -----------")
        print(train_fit_df)

        fit_data = []
        for one_row in train_fit_df:
            one_fit_data = {}
            one_fit_data['features'] = one_row['features'].values.tolist()
            one_fit_data['prediction'] = one_row['prediction']

            fit_data.append(one_fit_data)

        print("--------- fitted data ------------")
        print(fit_data)

        return fit_data

    def _print_after_train(self, df):
        print("----------- cluster centroid ---------")
        kmeansmodel = self._kmeans_model
        results2 = kmeansmodel.clusterCenters()
        for item in results2:
            print(item)


iris_cluster = IRIS_Cluster()


@shared_task
def train(k, train_data):
    print('Enter train function ...')
    train_fit_data = iris_cluster.train(k, train_data)

    return train_fit_data

@shared_task
def predict(one_features):
    print('Enter predict function ...')
    result = iris_cluster.predict(one_features)

    return result




# for test
def _get_train_data():
    with open('./iris.txt', 'r') as f:  # 采用b的方式处理可以省去很多问题
        reader = csv.reader(f)

        train_data = []
        for row in reader:
            # do something with row, such as row[0],row[1]
            #print(row[0])
            one_features = [float(row[0]), float(row[1]), float(row[2]), float(row[3])]
            train_data.append(one_features)

        pprint(train_data)
        return train_data

if __name__ == '__main__':
    # 这里生产的任务不可用，导入的模块不能包含task任务。会报错
    print("Start Task ...")

    train_data = _get_train_data()

    r = train.delay(3, train_data)
    print("r=", r.get())

    one_feature = [5.1, 3.5, 1.4, 0.2]
    r = predict.delay(one_feature)
    print(one_feature, ", cluster=", r.get())


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




