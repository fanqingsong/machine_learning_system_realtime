

for job in `ps aux | grep celery | awk '{print $2}'`; do
	echo "kill ${job}"
	kill -9 $job
done


