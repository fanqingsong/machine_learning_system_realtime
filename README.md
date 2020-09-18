# Machine Learning System on Spark

## introduction

> This project is a full stack Django/React/Redux/Celery/Spark app that uses token based authentication with Knox.
 
> Then I add Machine Learning features for demostrating the full workflow of the data mining, including the four stage corresponding to four pages:
> - data management
> - data explore
> - model train
> - prediction

> The data set is the classic iris data, which is only for demo, and this project is from my interest. 
so you can reference, but the quality is not assured.

---

## features

* authentication functions
> login from login page
> register your account
> logout from inner page

* data management
> input iris items
> edit iris items
> delete iris items

* data explore
> inspect attribute distribution through histogram
> inspect sepal distribution through scatter graph
> inspect petal distribution through scatter graph

* model train
> input cluster number
> train a cluster model using spark.ml library streamingly
> inspect cluster result through sepal and petal scatter

* prediction
> input iris sepal and petal attributes
> predict iris cluster

---

## Architecture

Generally, train process is time consumming, and predict process is quick.
So set train flow as async mode, and predict flow as sync mode.
BTW, train process is implemented by stream, with streaming kmeans library:
https://spark.apache.org/docs/latest/api/python/pyspark.mllib.html?highlight=streaminglinearregressionwithsgd#pyspark.mllib.clustering.StreamingKMeans


### train flow

* user start model train from browser
* django recieve the "start train" message
* django schedule process manager celery process to launch a train process based on kafka.
* browser transfer iris data one by one to django
* django call sender process to send one iris data to train process by kafka
* train process receive one iris data, training model with streaming kmeans library
* after feeding all iris data, display the train result for all iris data

### predict flow

* user input prediction features on browser, then click submit
* browser send prediction features to django
* django call prediction api with prediction features
* django feedback the prediction result to browser

```
+----------------+              +-------------+          +------------+       +---------------+
|                |              |             |          |            |       |               |
|     Browser    |              |   django    |          |   Celery   |       |   train proc  |
|                |              |             |          |            |       |   ess         |
+-------+--------+              +------+------+          +------+-----+       +-------+-------+
        |                              |                        |                     |
        |       request train          |                        |                     |
        +----------------------------->+                launch a train process with celery
        |                              +------------------------+-------------------->|
        |                              |                        |                     |
        |     send 1st iris data       |                        |                     |
        +----------------------------->+           send 1st iris data with celery     |
        |                              +------------------------+-------------------->+
        |                              |                        |                     |
        |                              |                        |                     |
        |                              |                        |                     |
        |                              |                        |                     |
        |     send last iris data      |                        |                     |
        +----------------------------->+           send last iris data with celery    |
        |                              +------------------------+-------------------->+
        |                              |                        |                     |
        |                              |                        |                     |
        |                              |                        |                     |
        |                              |                        |                     |
        |                              |                        |                     |
        |                              |                        |                     |
        |     send one iris features   |                        |                     |
        +----------------------------->+     predict cluster in celery                |
        |                              +------------------------>                     |
        |                              |                        |                     |
        |                              |                        |                     |
        |                              |                        |                     |
        +                              +                        +                     +

```

---

## technology stack

category | name | comment
---------|----------|---------
 frontend | reactjs | frontend framework
 frontend | redux | state management
 frontend | react-C3JS | D3 based graph tool
 frontend | react-bootstrap | style component library
 frontend | data-ui | react data visualization tool
 backend | django | backend framework
 backend | django-rest-knox | authentication library
 backend | djangorestframework | restful framework
 backend | spark.ml | machine learning tool
 backend | redis-server | broker for celery
 backend | celery | worker for django
 backend | kafka | broker for spark.ml streaming kmeans train
---

## Install

- pyenv install
[reference](https://github.com/pyenv/pyenv#installation)

- install all other dependencies

```bash
./bin/install_deps.sh
```

- install spark(2.1.0)
[reference](http://dblab.xmu.edu.cn/blog/1307-2/)

---

## Run

### Prerequisite for Run

- frontend build

```bash
./bin/build_ui.sh
```

### Run (On One Terminal)

```bash
./bin/start.sh
```

### Run (On Different Terminals)

- start redis server

```bash
./bin/start_redis.sh
```

- start kafka

```bash
./bin/start_kafka.sh
```

- start celery worker for django

```bash
./bin/start_celery.sh
```

- start Server on localhost:8000

```bash
./bin/start_django.sh
```

---

## snapshot

### login page
Note: account: admin/admin
![avatar](./snapshot/loginpage.png)

### data management page
![avatar](./snapshot/dataManagement.png)

### data explore page
![avatar](./snapshot/explore.png)

### model train page
![avatar](./snapshot/train.png)

### prediction page
![avatar](./snapshot/predict.png)

---

