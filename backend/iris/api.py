from .models import Iris
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import IrisSerializer
from ml.training_subprocess_manager import start_subprocess, stop_subprocess, print_subprocess
from ml.training_data_sender import send_iris_data
from ml.predicting_functor import predict_one
import json, time
import numpy
from celery import result
from pprint import pprint



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



class IrisTrainStarter(APIView):
    """
    train iris cluster model
    """
    def post(self, request, format=None):
        print("--------------- IrisTrain start post --------")

        print(request.data)

        n_clusters = request.data["cluster_number"]
        n_clusters = int(n_clusters)
        print("n_cluster=%d" % n_clusters)

        print("---- now start training subprocess -------")
        start_subprocess.delay(n_clusters)

        resp = {'status': 'OK'}
        respData = json.dumps(resp)

        return Response(respData, status=status.HTTP_201_CREATED)


class IrisTrainStopper(APIView):
    """
    stop train iris cluster model
    """
    def post(self, request, format=None):
        print("--------------- IrisTrain stop post --------")

        print(request.data)

        print("---- now stop training subprocess -------")
        stop_subprocess.delay()

        resp = {'status': 'OK'}
        respData = json.dumps(resp)

        return Response(respData, status=status.HTTP_201_CREATED)




class IrisDataFeeder(APIView):
    """
    send iris data to training process one by one
    """
    def post(self, request, format=None):
        print("--------------- IrisDataFeeder post --------")
        print(request.data)

        sepal_len = request.data["sepal_len"]
        sepal_width = request.data["sepal_width"]
        petal_len = request.data["petal_len"]
        petal_width = request.data["petal_width"]

        one_feature = [sepal_len, sepal_width, petal_len, petal_width]

        # sending train data
        print("-------- sending one iris data for training -------")
        send_iris_data.delay([one_feature])

        resp = {'status': 'OK'}
        respData = json.dumps(resp)

        return Response(respData, status=status.HTTP_201_CREATED)


class IrisPredictor(APIView):
    """
    predict iris cluster
    """
    def post(self, request, format=None):
        print("--------------- IrisPredictor post --------")
        print(request.data)

        sepal_len = request.data["sepal_len"]
        sepal_width = request.data["sepal_width"]
        petal_len = request.data["petal_len"]
        petal_width = request.data["petal_width"]

        print("sepal_len=%s" % sepal_len)

        one_feature = [sepal_len, sepal_width, petal_len, petal_width]

        predict_promise = predict_one.delay(one_feature)
        prediction = predict_promise.get()
        print(one_feature, ", cluster=", prediction)

        # transfer data to client
        irisDataPredict = {
            "predicted_cluster": prediction
        }

        respData = json.dumps(irisDataPredict, cls=MyEncoder)

        return Response(respData, status=status.HTTP_201_CREATED)





