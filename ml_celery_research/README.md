
the following command for ml test

```
cd ml_celery_research
# start celery worker for test
celery -A celerytask worker -l info

# test celery worker running
python3 celerytask.py

# test kmeans stand-alone code
python3 kmeans_demo.py

# start celery worker for ml
celery -A iris_cluster worker -l info

# test ml celery worker running
python3 iris_cluster.py
```

