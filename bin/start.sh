

echo "----- start redis --------"
./bin/start_redis.sh&

sleep 5s

echo "----- start kafka --------"
./bin/start_kafka.sh&

sleep 20s


echo "----- start celery --------"
./bin/start_celery.sh&

sleep 10s


echo "----- start django --------"
./bin/start_django.sh



