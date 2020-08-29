from .models import Iris
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import IrisSerializer
from .mltask import train, predict
import json
import numpy
from celery import result


# Iris Viewset
class IrisViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = IrisSerializer
    queryset = Iris.objects.all()


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.integer):
            return int(obj)
        elif isinstance(obj, numpy.floating):
            return float(obj)
        elif isinstance(obj, numpy.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)

class IrisTrain(APIView):
    """
    train iris cluster model
    """
    def get(self, request, format=None):
        print("--------------- IrisTrain get --------")

        print(request)
        print(request.GET)

        train_task_id = request.GET.get("train_task_id")
        print("train_task_id=%s" % train_task_id)

        train_promise = result.AsyncResult(train_task_id)
        if train_promise.ready():
            # wait for train over
            train_fit_data = train_promise.get()
            print("------------- train over!! ------------")
            print(train_fit_data)

            # transfer data to client
            train_result = [
                {"sepal_len": one_fit_data['features'][0],
                 "sepal_width": one_fit_data['features'][1],
                 "petal_len": one_fit_data['features'][2],
                 "petal_width": one_fit_data['features'][3],
                 "cluster": one_fit_data['prediction']}
                for one_fit_data in train_fit_data
            ]

            print(train_result[0])
            print(len(train_result))

            train_task_status = {'status': train_promise.state, 'result': train_result}
        else:
            train_task_status = {'status': train_promise.state, 'result': []}

        print(train_task_status)

        respData = json.dumps(train_task_status)

        return Response(respData)


    def post(self, request, format=None):
        print("--------------- IrisTrain post --------")

        print(request.data)

        n_clusters = request.data["cluster_number"]
        n_clusters = int(n_clusters)
        print("n_cluster=%d" % n_clusters)

        irisObjects = Iris.objects.all()
        irisDataTrain = [[oneIris.sepal_len, oneIris.sepal_width, oneIris.petal_len, oneIris.petal_width] for oneIris in irisObjects]
        print("------- train data ----------")
        print(irisDataTrain)

        # start train process
        train_promise = train.delay(n_clusters, irisDataTrain)
        train_task_id = train_promise.task_id
        print("----------", 'train_task_id = ', train_task_id)

        resp = {'train_task_id': train_task_id}

        respData = json.dumps(resp)

        return Response(respData, status=status.HTTP_201_CREATED)


class IrisPredict(APIView):
    """
    predict iris cluster
    """
    def post(self, request, format=None):
        print("--------------- IrisPredict post --------")
        print(request.data)

        sepal_len = request.data["sepal_len"]
        sepal_width = request.data["sepal_width"]
        petal_len = request.data["petal_len"]
        petal_width = request.data["petal_width"]

        print("sepal_len=%s" % sepal_len)

        one_feature = [sepal_len, sepal_width, petal_len, petal_width]

        predict_promise = predict.delay(one_feature)
        prediction = predict_promise.get()
        print(one_feature, ", cluster=", prediction)

        # transfer data to client
        irisDataPredict = {
            "predicted_cluster": prediction
        }

        respData = json.dumps(irisDataPredict, cls=MyEncoder)

        return Response(respData, status=status.HTTP_201_CREATED)





