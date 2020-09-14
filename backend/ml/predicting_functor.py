# task.py

import os
from celery import shared_task
import asyncio
from pyspark.mllib.clustering import StreamingKMeansModel
import pickle


class MLPredictor:
    def __init__(self):
        self._model_path = './model.pk'
        self._model = None

        #self._load_model()

    def _load_model(self):
        if not os.path.exists(self._model_path):
            print("model path({}) do not exist!".format(self._model_path))
            return

        with open(self._model_path, 'rb') as f:
            # The protocol version used is detected automatically, so we do not
            # have to specify it.
            data = pickle.load(f)
            print("--------- restore pickle --------")
            print(data)

            clusterCenters = data['clusterCenters']
            clusterWeights = data['clusterWeights']
            model = StreamingKMeansModel(clusterCenters=clusterCenters,
                                               clusterWeights=clusterWeights)

            self._model = model

    def predict_one(self, one_iris_data):
        #one_iris_data = [5.1, 3.5, 1.4, 0.2]

        if not self._model:
            print("model is not loaded, please check first.")
            return

        result = self._model.predict(one_iris_data)
        print("one_iris_data({}) has prediction result({})".format(one_iris_data, result))
        return result

    def predict_batch(self, batch):
        #batch = [ [5.1, 3.5, 1.4, 0.2] ]

        if not self._model:
            print("model is not loaded, please check first.")
            return

        result = []
        for one_iris_data in batch:
            one_result = self._model.predict(one_iris_data)
            result.append(one_result)

        return result


ml_predictor = MLPredictor()

@shared_task
def predict_one(one_iris_data):
    print('Enter predict_one function ...')

    # currently load actively,
    # model update should be triggered automatically by MQ event
    ml_predictor._load_model()

    result = ml_predictor.predict_one(one_iris_data)

    return result


@shared_task
def predict_batch(batch):
    print('Enter predict_batch function ...')

    # currently load actively,
    # model update should be triggered automatically by MQ event
    ml_predictor._load_model()

    result = ml_predictor.predict_batch(batch)

    return result


if __name__ == '__main__':
    # 这里生产的任务不可用，导入的模块不能包含task任务。会报错
    print("Start Task ...")

    print("before predict batch")
    batch = [[5.1, 3.5, 1.4, 0.2]]
    result = predict_batch.delay(batch)
    print("batch({}) result({})".format(batch, result))
    print("after predict batch")

    # actively query
    # for i in range(0,100):
    #     print("---- loop {} -----".format(i))
    #     print(r.status)
    #     if r.status == "SUCCESS":
    #         print(r.get())
    #     time.sleep(1)

    # https://docs.celeryproject.org/en/4.0/whatsnew-4.0.html#asyncresult-then-on-success-on-error
    # https://docs.telethon.dev/en/latest/concepts/asyncio.html
    loop = asyncio.get_event_loop()  # get the default loop for the main thread
    try:
        # run the event loop forever; ctrl+c to stop it
        # we could also run the loop for three seconds:
        #     loop.run_until_complete(asyncio.sleep(3))
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    print("End Task ...")

