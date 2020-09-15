from rest_framework import routers
from .api import IrisViewSet, IrisTrainStarter, IrisTrainStopper, IrisPredictor, IrisDataFeeder
from django.urls import path, include

router = routers.DefaultRouter()
router.register('api/iris', IrisViewSet, 'iris')

urlpatterns = [
    path('api/train/start', IrisTrainStarter.as_view()),
    path('api/train/stop', IrisTrainStopper.as_view()),
    path('api/predict', IrisPredictor.as_view()),
    path('api/feed',  IrisDataFeeder.as_view()),
]

urlpatterns += router.urls



